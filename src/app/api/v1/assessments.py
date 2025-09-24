import secrets
import uuid
from datetime import datetime
from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user

from ...core.db.database import async_get_db
from ...assessment_templates import (
    get_assessment_template,
    list_assessment_templates,
)
from ...models.assessment import Assessment
from ...models.category import Category
from ...models.question import Question
from ...models.question_option import QuestionOption
from ...models.user_profile import UserProfile
from ...schemas.assessment import (
    AssessmentResponse,
    AssessmentResult,
    AssessmentStartRequest,
    AssessmentStartResponse,
    AssessmentSubmission,
    CategoryScore,
    SharedAssessmentSubmission,
)
from ...schemas.assessment_template import (
    AssessmentDefinition,
    AssessmentTemplateSummary,
)

router = APIRouter()


@router.get("/schema", response_model=list[AssessmentTemplateSummary])
async def list_available_assessment_templates() -> list[AssessmentTemplateSummary]:
    """List all bundled assessment templates."""

    return list_assessment_templates()


@router.get("/schema/{template_id}", response_model=AssessmentDefinition)
async def get_assessment_template_definition(template_id: str) -> AssessmentDefinition:
    """Retrieve a detailed assessment template definition."""

    template = get_assessment_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Assessment template not found")

    return template


@router.get("/")
async def get_assessment_info(db: AsyncSession = Depends(async_get_db)):
    """
    Get basic assessment information and statistics.
    This endpoint handles GET requests to /api/v1/assessment
    """
    try:
        # Get total number of questions
        questions_result = await db.execute(select(func.count(Question.id)))
        total_questions = questions_result.scalar()

        # Get categories count
        categories_result = await db.execute(select(func.count(Category.id)))
        total_categories = categories_result.scalar()

        # Get total assessments completed
        assessments_result = await db.execute(
            select(func.count(Assessment.id)).where(Assessment.status == "completed")
        )
        total_completed = assessments_result.scalar()

        return {
            "message": "Security Assessment API",
            "status": "operational",
            "total_questions": total_questions,
            "total_categories": total_categories,
            "assessments_completed": total_completed,
            "estimated_time_minutes": max(5, total_questions * 2) if total_questions else 15,
            "available_endpoints": [
                "POST /api/v1/assessment/start - Start new assessment",
                "POST /api/v1/assessment/submit - Submit assessment answers",
                "GET /api/v1/assessment/{assessment_id} - Get assessment results",
                "GET /api/v1/assessment/user/{user_id} - Get user's assessments"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving assessment info: {str(e)}")


@router.get("/data/full")
async def get_assessment_data_full(db: AsyncSession = Depends(async_get_db)):
    """
    Get full assessment data including all questions and categories.
    This endpoint handles GET requests to /v1/assessment-data/full
    """
    try:
        # Get all categories with questions
        categories_result = await db.execute(
            select(Category).order_by(Category.title)
        )
        categories = categories_result.scalars().all()

        assessment_data = []
        for category in categories:
            # Get questions for this category
            questions_result = await db.execute(
                select(Question).where(Question.category_id == category.id).order_by(Question.id)
            )
            questions = questions_result.scalars().all()

            category_questions = []
            for question in questions:
                # Get options for this question
                options_result = await db.execute(
                    select(QuestionOption).where(QuestionOption.question_id == question.id).order_by(QuestionOption.id)
                )
                options = options_result.scalars().all()

                question_data = {
                    "id": question.id,
                    "text": question.question_text,
                    "type": question.question_type,
                    "weight": question.weight,
                    "options": [
                        {
                            "id": opt.id,
                            "value": opt.option_value,
                            "label": opt.option_text
                        } for opt in options
                    ]
                }
                category_questions.append(question_data)

            category_data = {
                "id": category.id,
                "name": category.title,
                "description": category.description,
                "questions": category_questions
            }
            assessment_data.append(category_data)

        return {
            "status": "success",
            "total_categories": len(assessment_data),
            "total_questions": sum(len(cat["questions"]) for cat in assessment_data),
            "categories": assessment_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving full assessment data: {str(e)}")


@router.post("/start", response_model=AssessmentStartResponse)
async def start_assessment(
    data: AssessmentStartRequest,
    db: Annotated[AsyncSession, Depends(async_get_db)]
):
    """
    Start a new assessment for a user.
    Checks if user can take more assessments based on their tier.
    """
    # Get user profile from request data
    user_id = data.user_id

    # Get or create user profile
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    user_profile = result.scalar_one_or_none()

    if not user_profile:
        # Create default user profile for new users
        user_profile = UserProfile()
        user_profile.user_id = user_id
        user_profile.assessments_count = 0
        user_profile.max_assessments = 3  # Default limit for new users
        user_profile.subscription_tier = "free"
        db.add(user_profile)
        await db.commit()
        await db.refresh(user_profile)

    # Check if user has reached assessment limit
    if user_profile.assessments_count >= user_profile.max_assessments:
        raise HTTPException(
            status_code=403,
            detail=f"Assessment limit reached. You have completed {user_profile.assessments_count}/{user_profile.max_assessments} assessments."
        )

    # Check for existing incomplete assessment
    result = await db.execute(
        select(Assessment).where(
            Assessment.user_profile_id == user_profile.id,
            Assessment.status.in_(["started", "in_progress"])
        )
    )
    existing_assessment = result.scalar_one_or_none()

    if existing_assessment:
        # Return existing assessment
        questions_count = await db.execute(select(func.count()).select_from(Question).where(Question.is_active == True))
        return AssessmentStartResponse(
            assessment_id=existing_assessment.id,
            message="Continuing your existing assessment",
            questions_count=questions_count.scalar_one(),
            estimated_time_minutes=max(5, questions_count.scalar_one() * 2)  # 2 minutes per question, min 5
        )

    # Create new assessment
    assessment = Assessment()
    assessment.user_profile_id = user_profile.id
    assessment.status = "started"
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)

    # Get questions count for response
    questions_count_result = await db.execute(select(func.count()).select_from(Question).where(Question.is_active == True))
    questions_count = questions_count_result.scalar_one()

    return AssessmentStartResponse(
        assessment_id=assessment.id,
        message="Assessment started successfully",
        questions_count=questions_count,
        estimated_time_minutes=max(5, questions_count * 2)
    )


@router.post("/submit", response_model=AssessmentResult)
async def submit_assessment(submission: AssessmentSubmission, db: Annotated[AsyncSession, Depends(async_get_db)], current_user: dict = Depends(get_current_user)):
    """
    Submit assessment answers and calculate results.
    """
    # Get assessment
    result = await db.execute(select(Assessment).where(Assessment.id == submission.assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    if assessment.status == "completed":
        raise HTTPException(status_code=400, detail="Assessment already completed")

    # Store answers
    answers_data = {}
    for answer in submission.answers:
        answers_data[str(answer.question_id)] = {
            "selected_options": answer.selected_options,
            "text_answer": answer.text_answer
        }

    assessment.answers = answers_data
    assessment.status = "completed"
    assessment.completed_at = datetime.utcnow()

    # Calculate scores
    total_score = 0.0
    max_possible_score = 0.0
    category_scores_data = {}

    # Get all questions and their options
    result = await db.execute(select(Question).where(Question.is_active == True))
    questions = result.scalars().all()

    for question in questions:
        question_score = 0.0
        max_question_score = question.weight

        if str(question.id) in answers_data:
            answer_data = answers_data[str(question.id)]
            selected_option_ids = answer_data.get("selected_options", [])

            # Calculate score based on selected options
            for option_id in selected_option_ids:
                option_result = await db.execute(select(QuestionOption).where(QuestionOption.id == option_id))
                option = option_result.scalar_one_or_none()
                if option:
                    question_score += option.score_points

        # Add to category scores
        if question.category_id not in category_scores_data:
            category_scores_data[question.category_id] = {
                "score": 0.0,
                "max_score": 0.0
            }

        category_scores_data[question.category_id]["score"] += question_score
        category_scores_data[question.category_id]["max_score"] += max_question_score

        total_score += question_score
        max_possible_score += max_question_score

    # Calculate percentage
    percentage_score = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0

    # Determine risk level
    if percentage_score >= 80:
        risk_level = "low"
    elif percentage_score >= 60:
        risk_level = "medium"
    elif percentage_score >= 40:
        risk_level = "high"
    else:
        risk_level = "critical"

    # Generate category scores for response
    category_scores_list = []
    categories_result = await db.execute(select(Category).where(Category.is_active == True))
    categories = categories_result.scalars().all()

    for category in categories:
        if category.id in category_scores_data:
            cat_data = category_scores_data[category.id]
            cat_percentage = (cat_data["score"] / cat_data["max_score"] * 100) if cat_data["max_score"] > 0 else 0

            # Determine category risk level
            if cat_percentage >= 80:
                cat_risk = "low"
            elif cat_percentage >= 60:
                cat_risk = "medium"
            elif cat_percentage >= 40:
                cat_risk = "high"
            else:
                cat_risk = "critical"

            category_scores_list.append(CategoryScore(
                category_id=category.id,
                category_title=category.title,
                score=cat_data["score"],
                max_score=cat_data["max_score"],
                percentage=cat_percentage,
                risk_level=cat_risk
            ))

    # Generate basic recommendations
    recommendations = []
    if risk_level == "critical":
        recommendations.extend([
            "Immediate action required: Your security posture needs significant improvement",
            "Consider implementing a comprehensive security framework",
            "Conduct regular security training for all staff"
        ])
    elif risk_level == "high":
        recommendations.extend([
            "Several security areas need attention",
            "Prioritize fixing critical vulnerabilities",
            "Implement regular security assessments"
        ])
    elif risk_level == "medium":
        recommendations.extend([
            "Good foundation, but room for improvement",
            "Focus on strengthening weaker areas",
            "Consider advanced security measures"
        ])
    else:
        recommendations.extend([
            "Excellent security posture!",
            "Maintain current security practices",
            "Stay updated with latest security trends"
        ])

    # Generate share token
    share_token = secrets.token_urlsafe(32)

    # Update assessment with results
    assessment.total_score = total_score
    assessment.max_possible_score = max_possible_score
    assessment.percentage_score = percentage_score
    assessment.risk_level = risk_level
    assessment.category_scores = {
        str(cat.id): {
            "score": category_scores_data.get(cat.id, {}).get("score", 0),
            "max_score": category_scores_data.get(cat.id, {}).get("max_score", 0),
            "percentage": (
                (category_scores_data.get(cat.id, {}).get("score", 0) / category_scores_data.get(cat.id, {}).get("max_score", 1) * 100)
                if category_scores_data.get(cat.id, {}).get("max_score")
                else 0
            )
        } for cat in categories
    }
    assessment.recommendations = recommendations
    assessment.share_token = share_token

    # Update user profile assessment count
    user_profile_result = await db.execute(select(UserProfile).where(UserProfile.id == assessment.user_profile_id))
    user_profile = user_profile_result.scalar_one_or_none()
    if user_profile:
        user_profile.assessments_count += 1

    await db.commit()
    await db.refresh(assessment)

    return AssessmentResult(
        assessment_id=assessment.id,
        user_id=current_user.get("id"),
        status=assessment.status,
        total_score=total_score,
        max_possible_score=max_possible_score,
        percentage_score=percentage_score,
        risk_level=risk_level,
        category_scores=category_scores_list,
        recommendations=recommendations,
        insights=f"Your overall security score is {percentage_score:.1f}%. Focus on improving areas with lower scores.",
        completed_at=assessment.completed_at,
        share_token=share_token
    )



@router.post("/submit-shared", response_model=AssessmentResult)
async def submit_shared_assessment(submission: SharedAssessmentSubmission, db: Annotated[AsyncSession, Depends(async_get_db)]):
    """Submit an assessment from a shared link (anonymous user)."""

    # Find the owner of the shared token
    result = await db.execute(
        select(Assessment).where(Assessment.share_token == submission.company_token)
    )
    owner_assessment = result.scalar_one_or_none()
    if not owner_assessment:
        raise HTTPException(status_code=404, detail="Invalid sharing token")

    # Get the user profile of the token owner
    user_result = await db.execute(
        select(UserProfile).where(UserProfile.id == owner_assessment.user_profile_id)
    )
    owner_user = user_result.scalar_one_or_none()
    if not owner_user:
        raise HTTPException(status_code=404, detail="Token owner not found")

    # Create a new assessment for this shared submission
    new_assessment = Assessment(
        id=uuid.uuid4(),
        user_profile_id=owner_user.id,  # Attribute to the token owner
        status="in_progress",
        share_token=submission.company_token,  # Keep reference to original token
        created_at=datetime.utcnow()
    )

    db.add(new_assessment)
    await db.flush()  # Get the ID

    # Store answers
    answers_data = {}
    for answer in submission.answers:
        answers_data[str(answer.question_id)] = {
            "selected_options": answer.selected_options,
            "text_answer": answer.text_answer
        }

    new_assessment.answers = answers_data
    new_assessment.status = "completed"
    new_assessment.completed_at = datetime.utcnow()

    # Calculate scores (same logic as regular submission)
    total_score = 0.0
    max_possible_score = 0.0
    category_scores_data = {}

    # Get all questions and their options
    questions_result = await db.execute(select(Question).where(Question.is_active == True))
    questions = questions_result.scalars().all()

    for question in questions:
        question_score = 0.0
        max_question_score = question.weight

        if str(question.id) in answers_data:
            answer_data = answers_data[str(question.id)]
            selected_option_ids = answer_data.get("selected_options", [])

            # Calculate score based on selected options
            for option_id in selected_option_ids:
                option_result = await db.execute(select(QuestionOption).where(QuestionOption.id == option_id))
                option = option_result.scalar_one_or_none()
                if option:
                    question_score += option.score_points

        # Add to category scores
        if question.category_id not in category_scores_data:
            category_scores_data[question.category_id] = {
                "score": 0.0,
                "max_score": 0.0
            }

        category_scores_data[question.category_id]["score"] += question_score
        category_scores_data[question.category_id]["max_score"] += max_question_score

        total_score += question_score
        max_possible_score += max_question_score

    # Calculate percentage and risk level
    percentage_score = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0

    if percentage_score >= 80:
        risk_level = "Low"
    elif percentage_score >= 60:
        risk_level = "Medium"
    elif percentage_score >= 40:
        risk_level = "High"
    else:
        risk_level = "Critical"

    new_assessment.total_score = total_score
    new_assessment.percentage_score = percentage_score
    new_assessment.risk_level = risk_level
    new_assessment.category_scores = category_scores_data

    # Create category scores list for response
    category_scores_list = []
    categories_result = await db.execute(select(Category))
    categories = categories_result.scalars().all()

    for category in categories:
        if category.id in category_scores_data:
            score_data = category_scores_data[category.id]
            category_percentage = (score_data["score"] / score_data["max_score"] * 100) if score_data["max_score"] > 0 else 0

            if category_percentage >= 80:
                cat_risk_level = "Low"
            elif category_percentage >= 60:
                cat_risk_level = "Medium"
            elif category_percentage >= 40:
                cat_risk_level = "High"
            else:
                cat_risk_level = "Critical"

            category_scores_list.append(CategoryScore(
                category_id=str(category.id),
                category_title=category.title,
                score=score_data["score"],
                max_score=score_data["max_score"],
                percentage=category_percentage,
                risk_level=cat_risk_level
            ))

    await db.commit()

    return AssessmentResult(
        assessment_id=new_assessment.id,
        user_profile_id=new_assessment.user_profile_id,
        status=new_assessment.status,
        total_score=total_score,
        max_possible_score=max_possible_score,
        percentage_score=percentage_score,
        risk_level=risk_level,
        category_scores=category_scores_list,
        recommendations=new_assessment.recommendations or [],
        insights=new_assessment.insights,
        completed_at=new_assessment.completed_at,
        share_token=new_assessment.share_token
    )


@router.get("/{assessment_id}", response_model=AssessmentResult)
async def get_assessment_result(assessment_id: UUID, db: Annotated[AsyncSession, Depends(async_get_db)]):
    """Get assessment results by ID."""
    result = await db.execute(select(Assessment).where(Assessment.id == assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    if assessment.status != "completed":
        raise HTTPException(status_code=400, detail="Assessment not completed yet")

    # Rebuild category scores for response
    category_scores_list = []
    if assessment.category_scores:
        categories = db.query(Category).filter(Category.is_active == True).all()
        for category in categories:
            if category.id in assessment.category_scores:
                cat_data = assessment.category_scores[category.id]
                cat_percentage = (cat_data["score"] / cat_data["max_score"] * 100) if cat_data["max_score"] > 0 else 0

                if cat_percentage >= 80:
                    cat_risk = "low"
                elif cat_percentage >= 60:
                    cat_risk = "medium"
                elif cat_percentage >= 40:
                    cat_risk = "high"
                else:
                    cat_risk = "critical"

                category_scores_list.append(CategoryScore(
                    category_id=category.id,
                    category_title=category.title,
                    score=cat_data["score"],
                    max_score=cat_data["max_score"],
                    percentage=cat_percentage,
                    risk_level=cat_risk
                ))

    return AssessmentResult(
        assessment_id=assessment.id,
        user_id=assessment.user_id,
        status=assessment.status,
        total_score=assessment.total_score,
        max_possible_score=assessment.max_possible_score,
        percentage_score=assessment.percentage_score,
        risk_level=assessment.risk_level,
        category_scores=category_scores_list,
        recommendations=assessment.recommendations or [],
        insights=assessment.insights,
        completed_at=assessment.completed_at,
        share_token=assessment.share_token
    )


@router.get("/user/{user_id}", response_model=List[AssessmentResponse])
async def get_user_assessments(user_id: int, db: Annotated[AsyncSession, Depends(async_get_db)]):
    """Get all assessments for a user."""
    assessments = await db.execute(select(Assessment).where(Assessment.user_id == user_id).order_by(Assessment.created_at.desc()))
    assessments = assessments.scalars().all()

    return AssessmentList(
        assessments=[AssessmentResponse.from_orm(a) for a in assessments],
        total=len(assessments)
    )
