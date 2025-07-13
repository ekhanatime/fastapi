from fastapi import APIRouter

from .login import router as login_router
from .logout import router as logout_router
from .posts import router as posts_router
from .rate_limits import router as rate_limits_router
from .tasks import router as tasks_router
from .tiers import router as tiers_router
from .users import router as users_router
from .assessment import router as assessment_router
from .anonymous_assessment import router as anonymous_assessment_router
from .health import router as health_router
from .categories import router as categories_router
from .questions import router as questions_router
from .question_options import router as question_options_router
from .leads import router as leads_router
from .lead_capture import router as lead_capture_router
from .password import router as password_router
from .assessments import router as assessments_router
from .email import router as email_router

# New comprehensive endpoints from migration file analysis
from .user_answers import router as user_answers_router
from .category_scores import router as category_scores_router
from .recommendations import router as recommendations_router
from .customer_info import router as customer_info_router

# Admin endpoints
from .admin_auth import router as admin_auth_router
from .admin_customers import router as admin_customers_router
from .admin_settings import router as admin_settings_router
from .admin_analytics import router as admin_analytics_router
from .admin_audit_logs import router as admin_audit_logs_router

router = APIRouter(prefix="/v1")
router.include_router(login_router)
router.include_router(logout_router)
router.include_router(users_router)
router.include_router(posts_router)
router.include_router(tasks_router)
router.include_router(tiers_router)
router.include_router(rate_limits_router)
router.include_router(assessment_router)
router.include_router(anonymous_assessment_router)
# Health endpoints - accessible at /api/v1/health
router.include_router(health_router, tags=["health"])

# Assessment endpoints - accessible at /api/v1/assessment (singular to match API test console)
router.include_router(assessments_router, prefix="/assessment", tags=["assessments"])

# Other endpoints with standard prefixes
router.include_router(categories_router, prefix="/categories", tags=["categories"])
router.include_router(questions_router, prefix="/questions", tags=["questions"])
router.include_router(question_options_router, prefix="/question-options", tags=["question-options"])
router.include_router(leads_router, prefix="/leads", tags=["leads"])
router.include_router(lead_capture_router, prefix="/lead-capture", tags=["lead-capture"])
router.include_router(password_router, prefix="/password", tags=["password"])
router.include_router(email_router, prefix="/email", tags=["email"])

# Register new comprehensive endpoints
router.include_router(user_answers_router, prefix="/user-answers", tags=["user-answers"])
router.include_router(category_scores_router, prefix="/category-scores", tags=["category-scores"])
router.include_router(recommendations_router, prefix="/recommendations", tags=["recommendations"])
router.include_router(customer_info_router, prefix="/customer-info", tags=["customer-info"])

# Register Admin endpoints
router.include_router(admin_auth_router)
router.include_router(admin_customers_router)
router.include_router(admin_settings_router)
router.include_router(admin_analytics_router)
router.include_router(admin_audit_logs_router)
