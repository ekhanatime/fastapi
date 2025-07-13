from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any
from datetime import datetime
import uuid

from app.core.db.database import async_get_db
from app.models.user_profile import UserProfile
from app.models.customer_info import CustomerInfo
from app.models.assessment import Assessment
from app.models.question import Question
from app.models.question_option import QuestionOption
from app.models.category import Category
from app.models.user_answer import UserAnswer
from app.models.category_score import CategoryScore
from app.models.recommendation import Recommendation
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/assessment", tags=["Anonymous Assessment"])


class AssessmentAnswer(BaseModel):
    question_id: int
    selected_options: List[int]


class AnonymousAssessmentSubmission(BaseModel):
    email: EmailStr
    answers: List[AssessmentAnswer]
    interested_in_contact: bool = False


class AssessmentResponse(BaseModel):
    success: bool
    assessment_id: str
    user_id: str
    overall_score: float
    total_score: float
    max_score: float
    percentage: float
    risk_level: str
    category_scores: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]


async def get_or_create_user(db: AsyncSession, email: str) -> UserProfile:
    """Get existing user or create new one by email"""
    # Check if user exists
    result = await db.execute(select(UserProfile).where(UserProfile.email == email))
    user = result.scalar_one_or_none()
    
    if user:
        return user
    
    # Create new user
    new_user = UserProfile(
        user_id=str(uuid.uuid4()),
        email=email,
        username=email.split('@')[0],  # Use email prefix as username
        created_at=datetime.utcnow()
    )
    db.add(new_user)
    
    # Create customer info record
    customer_info = CustomerInfo(
        user_id=new_user.user_id,
        lead_source="Assessment",
        lead_status="new",
        created_at=datetime.utcnow()
    )
    db.add(customer_info)
    
    await db.commit()
    await db.refresh(new_user)
    return new_user


def calculate_risk_level(percentage: float) -> str:
    """Calculate risk level based on percentage score"""
    if percentage >= 80:
        return "Lav Risiko"
    elif percentage >= 50:
        return "Middels Risiko"
    else:
        return "Høy Risiko"


async def generate_recommendations(db: AsyncSession, assessment_id: str, category_scores: Dict[str, Dict]) -> List[Dict[str, Any]]:
    """Generate recommendations based on category scores"""
    recommendations = []
    
    # Get categories for context
    result = await db.execute(select(Category))
    categories = {cat.id: cat for cat in result.scalars().all()}
    
    for category_id, score_data in category_scores.items():
        percentage = score_data["percentage"]
        category = categories.get(category_id)
        
        if not category:
            continue
            
        # Generate recommendation based on score
        if percentage < 50:
            priority = "high"
            recommendation_text = f"Kritisk forbedring nødvendig innen {category.title.lower()}"
        elif percentage < 80:
            priority = "medium"
            recommendation_text = f"Moderat forbedring anbefalt innen {category.title.lower()}"
        else:
            priority = "low"
            recommendation_text = f"God sikkerhet innen {category.title.lower()}, fortsett det gode arbeidet"
        
        # Create recommendation record
        recommendation = Recommendation(
            assessment_id=assessment_id,
            category_id=category_id,
            priority=priority,
            recommendation=recommendation_text,
            action_items=[f"Gjennomgå {category.title.lower()} retningslinjer"],
            created_at=datetime.utcnow()
        )
        db.add(recommendation)
        
        recommendations.append({
            "category": category.title,
            "priority": priority,
            "recommendation": recommendation_text,
            "action_items": [f"Gjennomgå {category.title.lower()} retningslinjer"]
        })
    
    return recommendations


@router.post("", response_model=AssessmentResponse)
async def submit_anonymous_assessment(
    submission: AnonymousAssessmentSubmission,
    db: AsyncSession = Depends(async_get_db)
):
    """Submit anonymous assessment with email and answers"""
    
    try:
        # Get or create user
        user = await get_or_create_user(db, submission.email)
        
        # Create assessment record
        assessment_id = str(uuid.uuid4())
        assessment = Assessment(
            id=assessment_id,
            user_id=user.user_id,
            status="completed",
            interested_in_contact=submission.interested_in_contact,
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db.add(assessment)
        
        # Get all questions and options for scoring
        questions_result = await db.execute(select(Question).where(Question.is_active == True))
        questions = {q.id: q for q in questions_result.scalars().all()}
        
        options_result = await db.execute(select(QuestionOption))
        options = {opt.id: opt for opt in options_result.scalars().all()}
        
        # Process answers and calculate scores
        total_score = 0.0
        max_possible_score = 0.0
        category_scores = {}
        
        for answer in submission.answers:
            question = questions.get(answer.question_id)
            if not question:
                raise HTTPException(status_code=400, detail=f"Question {answer.question_id} not found")
            
            # Calculate score for this question
            question_score = 0.0
            is_correct = False
            
            for option_id in answer.selected_options:
                option = options.get(option_id)
                if option and option.question_id == question.id:
                    question_score += option.score_points
                    if option.is_correct:
                        is_correct = True
            
            # Store user answer
            user_answer = UserAnswer(
                assessment_id=assessment_id,
                question_id=question.id,
                selected_options=answer.selected_options,
                is_correct=is_correct,
                points_earned=question_score,
                created_at=datetime.utcnow()
            )
            db.add(user_answer)
            
            # Add to category totals
            if question.category_id not in category_scores:
                category_scores[question.category_id] = {
                    "score": 0.0,
                    "max_score": 0.0,
                    "questions": 0
                }
            
            category_scores[question.category_id]["score"] += question_score
            category_scores[question.category_id]["max_score"] += question.weight
            category_scores[question.category_id]["questions"] += 1
            
            total_score += question_score
            max_possible_score += question.weight
        
        # Calculate overall percentage
        overall_percentage = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0
        risk_level = calculate_risk_level(overall_percentage)
        
        # Update assessment with scores
        assessment.total_score = total_score
        assessment.max_score = max_possible_score
        assessment.overall_score = overall_percentage
        
        # Store category scores
        category_scores_response = []
        for category_id, score_data in category_scores.items():
            percentage = (score_data["score"] / score_data["max_score"] * 100) if score_data["max_score"] > 0 else 0
            
            category_score = CategoryScore(
                assessment_id=assessment_id,
                category_id=category_id,
                score=score_data["score"],
                max_score=score_data["max_score"],
                percentage=percentage,
                created_at=datetime.utcnow()
            )
            db.add(category_score)
            
            # Get category name for response
            category_result = await db.execute(select(Category).where(Category.id == category_id))
            category = category_result.scalar_one_or_none()
            
            category_scores_response.append({
                "category_id": category_id,
                "category_name": category.title if category else "Unknown",
                "score": score_data["score"],
                "max_score": score_data["max_score"],
                "percentage": round(percentage, 1)
            })
        
        # Generate recommendations
        recommendations = await generate_recommendations(db, assessment_id, {
            cat_id: {"percentage": (data["score"] / data["max_score"] * 100) if data["max_score"] > 0 else 0}
            for cat_id, data in category_scores.items()
        })
        
        # Update customer info if interested in contact
        if submission.interested_in_contact:
            customer_result = await db.execute(select(CustomerInfo).where(CustomerInfo.user_id == user.user_id))
            customer_info = customer_result.scalar_one_or_none()
            if customer_info:
                customer_info.lead_status = "interested"
                customer_info.updated_at = datetime.utcnow()
        
        await db.commit()
        
        return AssessmentResponse(
            success=True,
            assessment_id=assessment_id,
            user_id=user.user_id,
            overall_score=overall_percentage,
            total_score=total_score,
            max_score=max_possible_score,
            percentage=round(overall_percentage, 1),
            risk_level=risk_level,
            category_scores=category_scores_response,
            recommendations=recommendations
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Assessment submission failed: {str(e)}")
