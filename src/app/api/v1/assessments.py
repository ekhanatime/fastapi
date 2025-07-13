from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Annotated, List, Optional
from uuid import UUID

from ...core.db.database import async_get_db
from app.api.dependencies import get_current_user
from ...models.user_profile import UserProfile
from ...models.assessment import Assessment
from ...models.question import Question
from ...models.question_option import QuestionOption
from ...models.category import Category
from ...schemas.assessment import (
    AssessmentStartRequest,
    AssessmentStartResponse,
    AssessmentSubmission,
    AssessmentResult,
    AssessmentResponse,
    CategoryScore
)
import uuid
import secrets
import string
from datetime import datetime

router = APIRouter()


@router.post("/start", response_model=AssessmentStartResponse)
async def start_assessment(assessment_data: AssessmentStartRequest, db: AsyncSession = Depends(async_get_db), current_user: dict = Depends(get_current_user)):
    """
    Start a new assessment for a user.
    Checks if user can take more assessments based on their tier.
    """
    # Get user profile (either from authenticated user or by user_id for leads)
    if current_user:
        user_id = current_user["id"]
    else:
        user_id = assessment_data.user_id
    
    # Get user profile
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    user_profile = result.scalar_one_or_none()
    if not user_profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    
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
    assessment = Assessment(
        user_profile_id=user_profile.id,
        status="started"
    )
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)
    
    # Get questions count for response
    questions_count = await db.execute(select(func.count()).select_from(Question).where(Question.is_active == True))
    
    return AssessmentStartResponse(
        assessment_id=assessment.id,
        message="Assessment started successfully",
        questions_count=questions_count,
        estimated_time_minutes=max(5, questions_count * 2)
    )


@router.post("/submit", response_model=AssessmentResult)
async def submit_assessment(submission: AssessmentSubmission, db: Annotated[AsyncSession, Depends(async_get_db)]):
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
    assessment.category_scores = category_scores_data
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
        user_id=assessment.user_id,
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
