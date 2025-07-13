# Changelog

All notable changes to the Security Assessment API will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-01-13

### Added - Comprehensive Entity Coverage from Migration Analysis

#### New Database Models
- **UserAnswer**: Store user responses to assessment questions with scoring
- **CategoryScore**: Per-category scoring results for detailed analytics
- **Recommendation**: AI-generated recommendations based on assessment results
- **CustomerInfo**: Extended customer/lead information and subscription management
- **EmailNotification**: Email tracking system for assessment notifications
- **SubscriptionPlan**: Subscription tiers and feature management

#### New API Endpoints

**User Answers Management (`/api/v1/user-answers/`)**
- `POST /` - Create new user answer for assessment question
- `GET /assessment/{assessment_id}` - Get all answers for specific assessment
- `GET /{user_answer_id}` - Get specific user answer by ID
- `PUT /{user_answer_id}` - Update user answer
- `DELETE /{user_answer_id}` - Delete user answer

**Category Scores Management (`/api/v1/category-scores/`)**
- `POST /` - Create new category score for assessment
- `GET /assessment/{assessment_id}` - Get all category scores for assessment
- `GET /{category_score_id}` - Get specific category score by ID
- `PUT /{category_score_id}` - Update category score
- `DELETE /{category_score_id}` - Delete category score

**Recommendations Management (`/api/v1/recommendations/`)**
- `POST /` - Create new recommendation for assessment
- `GET /assessment/{assessment_id}` - Get all recommendations for assessment
- `GET /category/{category_id}` - Get all recommendations for category
- `GET /{recommendation_id}` - Get specific recommendation by ID
- `PUT /{recommendation_id}` - Update recommendation
- `DELETE /{recommendation_id}` - Delete recommendation

**Customer Information Management (`/api/v1/customer-info/`)**
- `POST /` - Create customer info for user
- `GET /` - Get all customer info with filtering (lead_status, subscription_plan)
- `GET /user/{user_id}` - Get customer info for specific user
- `GET /{customer_info_id}` - Get customer info by ID
- `PUT /{customer_info_id}` - Update customer info
- `DELETE /{customer_info_id}` - Delete customer info
- `POST /{customer_info_id}/increment-submissions` - Increment submission count with validation

#### Enhanced Features
- **Comprehensive CRUD Operations**: Full create, read, update, delete operations for all entities
- **Advanced Filtering**: Query parameters for filtering customer info by status and subscription
- **Submission Tracking**: Automatic validation of submission limits based on subscription plans
- **Multi-language Support**: Norwegian priority levels and recommendation text
- **Relationship Management**: Proper foreign key relationships between all entities
- **Authentication Integration**: All endpoints protected with existing FastAPI boilerplate auth

#### Database Schema Enhancements
- **UUID Primary Keys**: Consistent UUID usage across all new models
- **Proper Foreign Keys**: Correct references to existing boilerplate tables
- **Enum Support**: Type-safe enums for lead status, email status, and priority levels
- **Array Fields**: PostgreSQL array support for selected options and action items
- **Timestamp Tracking**: Created/updated timestamps on all relevant models
- **Cascade Deletes**: Proper cleanup when parent records are deleted

### Technical Improvements
- **Import Path Consistency**: All models use proper absolute imports matching boilerplate structure
- **Error Handling**: Comprehensive error handling with proper HTTP status codes
- **Async Operations**: Full async/await support for all database operations
- **Type Safety**: Pydantic schemas with proper type validation
- **API Documentation**: Comprehensive OpenAPI/Swagger documentation for all endpoints

### Migration Coverage
Based on comprehensive analysis of all migration files in `backend/database/`:
- ✅ **Core Entities**: users, user_accounts, customer_info, assessments, categories, questions, question_options, user_answers, category_scores, recommendations, email_notifications
- ✅ **Subscription System**: subscription_plans with feature management
- 🔄 **Company Features**: company_assessments (planned for next release)
- 🔄 **Payment System**: payment_sessions, payment_transactions (planned for next release)
- 🔄 **Admin System**: admin_users (planned for next release)

### Documentation Updates
- **API Documentation**: Updated with all new endpoints and models
- **Database Schema**: Documented all new entities and relationships
- **Integration Guide**: Updated authentication and user profile integration
- **Migration Guide**: Instructions for database initialization and seeding

## [1.0.0] - 2024-01-01

### Added - Initial Release
- Basic assessment system with categories, questions, and options
- Lead capture functionality
- User authentication integration
- Assessment taking and results endpoints
- Docker containerization
- PostgreSQL database with Redis caching

### Infrastructure
- FastAPI boilerplate integration
- Async database operations
- JWT authentication
- Docker Compose setup
- Automated database migrations

---

## Upcoming Features (Roadmap)

### [2.1.0] - Company Sharing & Collaboration
- Company assessment sharing functionality
- Team collaboration features
- Bulk assessment management

### [2.2.0] - Payment Integration
- Dintero payment processing
- Subscription management
- Payment transaction tracking

### [2.3.0] - Advanced Admin Features
- Admin user management
- Advanced analytics dashboard
- Bulk data operations

### [2.4.0] - Enhanced Analytics
- Dashboard functions implementation
- Company submission tracking
- Advanced reporting features
