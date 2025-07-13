# Security Assessment API Documentation

## Overview

The Security Assessment API provides endpoints for managing security assessments, including lead capture, assessment taking, and results retrieval. The system integrates with the existing FastAPI boilerplate authentication system.

## Architecture

### Database Models

#### User (Existing Authentication)
- **Purpose**: Core user authentication and account management
- **Fields**: id, username, email, hashed_password, is_superuser, tier_id
- **Endpoints**: `/api/v1/user`, `/api/v1/login`, `/api/v1/users/me`

#### UserProfile (Assessment Extension)
- **Purpose**: Assessment-specific user data and lead tracking
- **Fields**: user_id (FK), company info, subscription tier, lead status, assessment limits
- **Relationship**: One-to-one with User model

#### Assessment
- **Purpose**: Individual assessment instances and results
- **Fields**: user_profile_id (FK), status, answers (JSON), scores, risk_level, recommendations
- **Relationship**: Many-to-one with UserProfile

#### Categories, Questions, QuestionOptions
- **Purpose**: Assessment content structure
- **Relationships**: Categories → Questions → QuestionOptions

#### UserAnswer (New)
- **Purpose**: Store user responses to assessment questions
- **Fields**: assessment_id (FK), question_id (FK), selected_options (array), is_correct, points_earned
- **Relationship**: Many-to-one with Assessment and Question

#### CategoryScore (New)
- **Purpose**: Per-category scoring results for assessments
- **Fields**: assessment_id (FK), category_id (FK), score, max_score, questions_count, percentage
- **Relationship**: Many-to-one with Assessment and Category

#### Recommendation (New)
- **Purpose**: Generated recommendations based on assessment results
- **Fields**: assessment_id (FK), category_id (FK), priority, recommendation (text), action_items (array)
- **Relationship**: Many-to-one with Assessment and Category

#### CustomerInfo (New)
- **Purpose**: Extended customer/lead information and subscription management
- **Fields**: user_id (FK), company details, lead_status, subscription_plan, submission limits
- **Relationship**: One-to-one with User

#### EmailNotification (New)
- **Purpose**: Track email notifications sent for assessments
- **Fields**: assessment_id (FK), email_type, recipient_email, sent_at, email_status
- **Relationship**: Many-to-one with Assessment

#### SubscriptionPlan (New)
- **Purpose**: Define subscription tiers and features
- **Fields**: id, name, price, max_submissions, features (array), is_active
- **Relationship**: Referenced by CustomerInfo

## API Endpoints

### 1. Lead Capture

#### POST `/api/v1/lead-capture/capture-lead`
Capture lead information and create user account if needed.

**Request Body:**
```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "company_name": "Acme Corp",
  "job_title": "IT Manager",
  "phone": "+1234567890",
  "company_size": "medium",
  "industry": "Technology",
  "lead_source": "website"
}
```

**Response:**
```json
{
  "message": "Thank you for your interest! You can now take your security assessment.",
  "user_id": 123,
  "profile_id": "uuid-here",
  "can_take_assessment": true,
  "assessments_remaining": 3,
  "registration_required": true
}
```

**Features:**
- Creates new User + UserProfile for new leads
- Updates existing profiles with additional information
- Enforces tier-based assessment limits
- Integrates with existing authentication system

### 2. Assessment Management

#### POST `/api/v1/assessments/start`
Start a new assessment for a user.

**Request Body:**
```json
{
  "user_id": 123
}
```

**Response:**
```json
{
  "assessment_id": "uuid-here",
  "message": "Assessment started successfully",
  "questions_count": 25,
  "estimated_time_minutes": 15
}
```

**Features:**
- Checks assessment limits based on subscription tier
- Returns existing incomplete assessment if found
- Requires authentication for registered users

#### POST `/api/v1/assessments/submit`
Submit assessment answers and get results.

**Request Body:**
```json
{
  "assessment_id": "uuid-here",
  "answers": [
    {
      "question_id": 1,
      "selected_options": [1, 3],
      "text_answer": "Additional comments"
    }
  ]
}
```

**Response:**
```json
{
  "assessment_id": "uuid-here",
  "user_profile_id": "uuid-here",
  "status": "completed",
  "total_score": 75.5,
  "max_possible_score": 100.0,
  "percentage_score": 75.5,
  "risk_level": "medium",
  "category_scores": [
    {
      "category_id": "network-security",
      "category_title": "Network Security",
      "score": 18.0,
      "max_score": 25.0,
      "percentage": 72.0,
      "risk_level": "medium"
    }
  ],
  "recommendations": [
    "Implement multi-factor authentication",
    "Regular security training for employees"
  ],
  "insights": "Your overall security score is 75.5%. Focus on improving areas with lower scores.",
  "completed_at": "2024-01-15T10:30:00Z",
  "share_token": "abc123"
}
```

**Features:**
- Calculates category-wise scores
- Determines risk levels (low/medium/high/critical)
- Generates personalized recommendations
- Creates shareable result tokens
- Updates user assessment count

#### GET `/api/v1/assessments/{assessment_id}`
Get assessment results by ID.

**Response:** Same as submit endpoint response

**Features:**
- Public access via share_token
- Protected access for assessment owner

#### GET `/api/v1/assessments/user/{user_id}`
Get all assessments for a user.

**Response:**
```json
[
  {
    "id": "uuid-here",
    "user_profile_id": "uuid-here",
    "status": "completed",
    "started_at": "2024-01-15T10:00:00Z",
    "completed_at": "2024-01-15T10:30:00Z",
    "total_score": 75.5,
    "percentage_score": 75.5,
    "risk_level": "medium",
    "is_shared": true,
    "share_token": "abc123",
    "created_at": "2024-01-15T10:00:00Z"
  }
]
```

### 3. Assessment Content

#### GET `/api/v1/assessment-data/full`
Get all categories, questions, and options for frontend loading.

**Response:**
```json
{
  "categories": [
    {
      "id": "network-security",
      "title": "Network Security",
      "icon": "network-icon",
      "display_order": 1,
      "is_active": true,
      "questions": [
        {
          "id": 1,
          "category_id": "network-security",
          "question_text": "Do you use a firewall?",
          "question_type": "multiple_choice",
          "is_required": true,
          "weight": 5.0,
          "display_order": 1,
          "is_active": true,
          "options": [
            {
              "id": 1,
              "question_id": 1,
              "option_text": "Yes, enterprise-grade",
              "option_value": "enterprise",
              "score_points": 5.0,
              "is_correct": true,
              "display_order": 1
            }
          ]
        }
      ]
    }
  ]
}
```

### 4. CRUD Endpoints

#### Categories
- `GET /api/v1/categories` - List all categories
- `GET /api/v1/categories/{category_id}` - Get category by ID
- `POST /api/v1/categories` - Create new category
- `PUT /api/v1/categories/{category_id}` - Update category
- `DELETE /api/v1/categories/{category_id}` - Delete category

#### Questions
- `GET /api/v1/questions` - List all questions
- `GET /api/v1/questions/{question_id}` - Get question with options
- `POST /api/v1/questions` - Create new question
- `PUT /api/v1/questions/{question_id}` - Update question
- `DELETE /api/v1/questions/{question_id}` - Delete question

#### Question Options
- `GET /api/v1/question-options` - List all options
- `GET /api/v1/question-options/{option_id}` - Get option by ID
- `POST /api/v1/question-options` - Create new option
- `PUT /api/v1/question-options/{option_id}` - Update option
- `DELETE /api/v1/question-options/{option_id}` - Delete option

## Authentication

### Existing System Integration
The assessment system integrates with the FastAPI boilerplate's authentication:

- **Registration**: `POST /api/v1/user`
- **Login**: `POST /api/v1/login` (returns JWT tokens)
- **Token Refresh**: `POST /api/v1/refresh`
- **User Profile**: `GET /api/v1/users/me`

### Assessment-Specific Flow
1. **Lead Capture**: Creates User + UserProfile (with temp password)
2. **Assessment Taking**: Can be done without full registration
3. **Account Completion**: User can set real password via existing registration
4. **Protected Access**: Full dashboard requires JWT authentication

## Scoring System

### Category Scoring
- Each question has a weight (importance factor)
- Each option has score_points (0-5 scale typically)
- Category score = sum of (question_weight × selected_option_points)
- Category percentage = (category_score / max_category_score) × 100

### Risk Levels
- **Critical**: 0-25% - Immediate action required
- **High**: 26-50% - Significant vulnerabilities
- **Medium**: 51-75% - Some improvements needed
- **Low**: 76-100% - Good security posture

### Recommendations Engine
Generates personalized recommendations based on:
- Low-scoring categories
- Specific answer patterns
- Industry best practices
- Risk level thresholds

## Subscription Tiers

### Free Tier
- 3 assessments maximum
- Basic recommendations
- Email results

### Basic Tier (Future)
- 10 assessments per month
- Detailed recommendations
- Historical tracking

### Premium Tier (Future)
- Unlimited assessments
- Advanced analytics
- Custom branding
- API access

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

#### 401 Unauthorized
```json
{
  "detail": "Authentication required"
}
```

#### 403 Forbidden
```json
{
  "detail": "Assessment limit reached. You have completed 3/3 assessments."
}
```

#### 404 Not Found
```json
{
  "detail": "Assessment not found"
}
```

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Rate Limiting

The system inherits rate limiting from the FastAPI boilerplate:
- 100 requests per minute per IP for public endpoints
- 1000 requests per minute for authenticated users
- Special limits for assessment submission (1 per minute)

## Security Features

### Data Protection
- JWT token authentication
- Password hashing with bcrypt
- SQL injection prevention via SQLAlchemy ORM
- Input validation with Pydantic schemas

### Privacy
- Assessment results are private by default
- Optional sharing via secure tokens
- GDPR-compliant data handling
- User data deletion capabilities

## Development Setup

### Prerequisites
- Docker and Docker Compose
- PostgreSQL 13+
- Python 3.11+
- FastAPI boilerplate setup

### Environment Variables
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/security_assessment

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Assessment Settings
DEFAULT_ASSESSMENT_LIMIT=3
PREMIUM_ASSESSMENT_LIMIT=50
```

### Running the API
```bash
# Start the services
docker-compose up -d

# Run migrations
docker-compose exec web alembic upgrade head

# Seed database (automatic on first run)
# SQL files in backend/database/ are auto-executed
```

## Testing

### Manual Testing
Use the FastAPI automatic documentation at:
- `http://localhost:8000/docs` - Swagger UI
- `http://localhost:8000/redoc` - ReDoc

### Example Test Flow
1. Capture lead via `/api/v1/lead-capture/capture-lead`
2. Start assessment via `/api/v1/assessments/start`
3. Get questions via `/api/v1/assessment-data/full`
4. Submit answers via `/api/v1/assessments/submit`
5. View results via `/api/v1/assessments/{assessment_id}`

## Deployment

### Production Considerations
- Use environment-specific configuration
- Enable HTTPS/TLS
- Configure proper CORS settings
- Set up monitoring and logging
- Implement backup strategies
- Use production-grade database

### Scaling
- Horizontal scaling via load balancers
- Database read replicas for heavy read workloads
- Redis caching for frequently accessed data
- CDN for static assets

## Support

### Common Issues
1. **Assessment limit reached**: Check user subscription tier
2. **Authentication errors**: Verify JWT token validity
3. **Database connection**: Check PostgreSQL service status
4. **Validation errors**: Review request payload format

### Monitoring
- API response times
- Error rates by endpoint
- Assessment completion rates
- User registration conversion
- Database performance metrics
