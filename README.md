# Complete User Flow Documentation - Security Assessment Platform

## 🎯 Overview

This document describes the complete user flow for the Security Assessment Platform, including the seamless auto-login and authentication architecture.

## 🔐 Authentication Architecture

### User Account Creation
- **Endpoint**: `POST /api/v1/lead-capture/capture-lead`
- **Input**: `{"email": "user@example.com"}`
- **Output**: 
```json
{
  "user_id": "uuid-here",
  "temporary_password": "ABC123XYZ",
  "is_existing_user": false,
  "requires_password_change": true
}
```

### Authentication Requirements
- **No Auth Required**: Assessment start, question loading
- **Auth Required**: Assessment submission, results viewing, dashboard access
- **Credentials**: Email + temporary password from account creation

## 🚀 Complete User Flow

```mermaid
flowchart TD
    A[User visits assessment page] --> B[Enters email address]
    B --> C{Email exists?}
    
    C -->|No| D[Create new account]
    C -->|Yes| E[Show 'Welcome back' modal]
    
    D --> F[Generate temporary password]
    F --> G[Return user_id + password]
    G --> H[Start new assessment]
    
    E --> I[Load existing user data]
    I --> H
    
    H --> J[Get assessment_id]
    J --> K[Load questions from API]
    K --> L[Show assessment interface]
    
    L --> M[User answers questions]
    M --> N[Submit with authentication]
    N --> O[Calculate results]
    O --> P[Show results page]
    
    P --> Q{User interested?}
    Q -->|Yes| R[Send login link via email]
    Q -->|No| S[Store as lead for nurturing]
    
    R --> T[User accesses dashboard]
    T --> U[View history & recommendations]
```

## 📊 Technical Flow Sequence

### 1. Frontend Email Submission
```javascript
// Step 1: Create customer account
const accountResult = await createCustomerAccount(email);
// Returns: {user_id, temporary_password, is_existing_user}

// Step 2: Start assessment  
const assessmentResult = await startAssessment(accountResult.user_id);
// Returns: {assessment_id, questions_count}

// Step 3: Load questions
const questionsData = await loadQuestions();
// Returns: {categories: [{questions: [...]}]}

// Step 4: Show assessment interface
showAssessment();
```

### 2. Assessment Submission (Authenticated)
```javascript
// User must authenticate with email + temporary_password
const token = await authenticate(email, temporary_password);

// Submit answers with authentication
const results = await submitAssessment({
  assessment_id: assessmentId,
  answers: userAnswers
}, token);
```

### 3. Results & Dashboard Access (Authenticated)
```javascript
// All dashboard endpoints require authentication
const dashboardData = await getDashboardData(token);
const assessmentHistory = await getAssessmentHistory(token);
```

## 🔧 Backend API Endpoints

### Public Endpoints (No Authentication)
- `POST /api/v1/lead-capture/capture-lead` - Create user account
- `POST /api/v1/assessment/start` - Start new assessment
- `GET /api/v1/assessment/data/full` - Load questions
- `GET /api/v1/assessment/schema` - List bundled assessment templates
- `GET /api/v1/assessment/schema/{template_id}` - Retrieve full template definition

### Protected Endpoints (Authentication Required)
- `POST /api/v1/assessment/submit` - Submit assessment answers
- `GET /api/v1/assessment/results/{id}` - Get assessment results
- `GET /api/v1/dashboard/*` - Dashboard access
- `POST /api/v1/login` - OAuth2 authentication

### Authentication Flow
```bash
# 1. Get JWT token
curl -X POST "http://localhost:8000/api/v1/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=ABC123XYZ"

# 2. Use token for protected endpoints
curl -X POST "http://localhost:8000/api/v1/assessment/submit" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"assessment_id": "uuid", "answers": {...}}'
```

## 📧 Email Integration

### Login Link Generation
- **Endpoint**: `POST /api/v1/email/send-login-link`
- **Purpose**: Send seamless login links with embedded credentials
- **Template**: HTML email with secure login URL

### Email Simulation (Development)
```python
# When SMTP not configured, emails are logged:
logger.info(f"SIMULATED EMAIL TO: {email}")
logger.info(f"LOGIN LINK: {login_url}")
logger.info(f"CREDENTIALS: {email} / {password}")
```

## 🎨 Frontend Implementation

### Key JavaScript Methods
```javascript
class AssessmentApp {
  // Create user account and get credentials
  async createCustomerAccount(email) { ... }
  
  // Start assessment for user
  async startAssessment(userId) { ... }
  
  // Load questions from API
  async loadQuestions() { ... }
  
  // Submit with authentication
  async submitAssessment(data, token) { ... }
}
```

### Authentication State Management
```javascript
// Store authentication data
this.userId = accountResult.user_id;
this.assessmentId = assessmentResult.assessment_id;
this.temporaryPassword = accountResult.temporary_password;

// Use for authenticated requests
const token = await this.authenticate();
```

## 🔒 Security Considerations

### Password Security
- Temporary passwords are cryptographically secure (12+ characters)
- Passwords are hashed using bcrypt before storage
- Users are encouraged to change passwords after first login

### Session Management
- JWT tokens for stateless authentication
- Token expiration and refresh mechanisms
- Secure cookie handling for persistent sessions

### Data Protection
- User emails are validated and sanitized
- Assessment data is tied to authenticated users
- Results are only accessible by the user who took the assessment

## 🚀 Deployment Architecture

### Backend (FastAPI)
- **Location**: `f:\securityassessment\fastapi\`
- **Port**: 8000
- **Services**: PostgreSQL, Redis, SMTP (optional)

### Frontend (HTML/JS)
- **Location**: `f:\securityassessment\customer_frontend\`
- **Port**: 3000
- **Dependencies**: Tailwind CSS, Fetch API

### Docker Containers
```yaml
# Backend
services:
  web:
    build: .
    ports: ["8000:8000"]
  
  postgres:
    image: postgres:13
    
  redis:
    image: redis:alpine
```

## 📈 User Experience Flow

### New User Journey
1. **Landing** → Enter email → Account created automatically
2. **Assessment** → Answer questions → Submit with auto-authentication  
3. **Results** → View scores → Option to create dashboard account
4. **Follow-up** → Receive login link → Access dashboard seamlessly

### Returning User Journey
1. **Landing** → Enter email → "Welcome back" modal
2. **Assessment** → Continue or start new → Submit with existing auth
3. **Dashboard** → View history → Access recommendations

## 🔍 Testing & Validation

### Manual Testing Steps
1. Clear test users from database
2. Use fresh email address
3. Verify account creation response includes password
4. Confirm assessment start works without auth
5. Verify submission requires authentication
6. Test dashboard access with credentials

### API Testing Console
- Available at: `http://localhost:8000`
- Interactive forms for all endpoints
- Authentication testing capabilities
- Real-time status monitoring

## 📋 Next Steps

1. **Production SMTP** - Configure real email service
2. **Password Reset** - Implement forgot password flow  
3. **Social Login** - Add Google/Microsoft OAuth
4. **Mobile Optimization** - Responsive design improvements
5. **Analytics** - User behavior tracking and insights

---

*Last Updated: 2025-07-14*
*Version: 2.0 - Complete Authentication Architecture*


# Security Assessment System - Complete Integration Guide

## System Overview

The Security Assessment System is built on top of the FastAPI boilerplate and provides a complete lead capture and assessment platform. The system integrates seamlessly with the existing authentication infrastructure while adding assessment-specific functionality.

## Architecture Integration

### Core Components

#### 1. **Existing FastAPI Boilerplate** (Authentication Layer)
- **User Model**: Core authentication (id, username, email, password)
- **JWT Authentication**: Access/refresh tokens, login/logout
- **Security**: Password hashing, token blacklisting
- **Endpoints**: `/api/v1/user`, `/api/v1/login`, `/api/v1/users/me`

#### 2. **Assessment Extension** (Business Logic Layer)
- **UserProfile Model**: Assessment-specific data (company info, subscription, lead tracking)
- **Assessment Model**: Assessment instances and results
- **Content Models**: Categories, Questions, QuestionOptions
- **Endpoints**: Lead capture, assessment flow, results

### Database Schema Integration

```sql
-- Existing User table (from boilerplate)
user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(20) UNIQUE,
    email VARCHAR(255) UNIQUE,
    hashed_password VARCHAR(255),
    is_superuser BOOLEAN DEFAULT FALSE,
    tier_id INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

-- New UserProfile table (assessment extension)
user_profiles (
    id UUID PRIMARY KEY,
    user_id INTEGER REFERENCES user(id) UNIQUE,  -- One-to-one relationship
    full_name VARCHAR(255),
    company_name VARCHAR(255),
    job_title VARCHAR(255),
    phone VARCHAR(50),
    company_size VARCHAR(20),
    industry VARCHAR(100),
    subscription_tier VARCHAR(20) DEFAULT 'free',
    assessments_count INTEGER DEFAULT 0,
    max_assessments INTEGER DEFAULT 3,
    lead_status VARCHAR(20) DEFAULT 'new',
    lead_source VARCHAR(100),
    lead_notes TEXT,
    company_share_token VARCHAR(255) UNIQUE,
    company_share_enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
)

-- Assessment instances
assessments (
    id UUID PRIMARY KEY,
    user_profile_id UUID REFERENCES user_profiles(id),
    status VARCHAR(20) DEFAULT 'started',
    answers JSONB,
    total_score FLOAT,
    max_possible_score FLOAT,
    percentage_score FLOAT,
    risk_level VARCHAR(20),
    category_scores JSONB,
    recommendations TEXT[],
    insights TEXT,
    share_token VARCHAR(255) UNIQUE,
    is_shared BOOLEAN DEFAULT FALSE,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
)
```

## User Flow Integration

### 1. **Lead Capture Flow**
```
Visitor → Email Submission → User + UserProfile Creation → Assessment Available
```

**Implementation:**
- `POST /api/v1/lead-capture/capture-lead`
- Creates User with temporary password
- Creates UserProfile with lead information
- Returns assessment availability status

### 2. **Assessment Taking Flow**
```
Lead/User → Start Assessment → Answer Questions → Submit → Get Results
```

**Implementation:**
- `POST /api/v1/assessments/start` (checks limits, creates instance)
- `GET /api/v1/assessment-data/full` (loads questions)
- `POST /api/v1/assessments/submit` (calculates scores, generates recommendations)
- `GET /api/v1/assessments/{id}` (retrieves results)

### 3. **User Registration Flow** (Optional)
```
Lead → Set Password → Full Account → Dashboard Access
```

**Implementation:**
- Uses existing `POST /api/v1/user` endpoint
- Updates existing User record with real password
- Enables full dashboard and history access

## API Integration Points

### Authentication Integration

#### For Leads (No Authentication Required)
```python
# Lead capture - creates User + UserProfile
POST /api/v1/lead-capture/capture-lead
{
    "email": "user@example.com",
    "company_name": "Acme Corp"
}

# Start assessment - uses user_id from lead capture
POST /api/v1/assessments/start
{
    "user_id": 123
}
```

#### For Registered Users (JWT Authentication)
```python
# Login with existing system
POST /api/v1/login
{
    "username": "user@example.com",
    "password": "password123"
}

# Start assessment - uses current_user from JWT
POST /api/v1/assessments/start
# user_id automatically extracted from JWT token
```

### Data Flow Integration

#### Lead to User Conversion
```python
# 1. Lead submits email
lead_data = {
    "email": "user@example.com",
    "company_name": "Acme Corp"
}

# 2. System creates User + UserProfile
user = User(
    username="user",  # from email
    email="user@example.com",
    hashed_password=temp_password  # temporary
)

profile = UserProfile(
    user_id=user.id,
    company_name="Acme Corp",
    subscription_tier="free",
    max_assessments=3
)

# 3. User can take assessments immediately
# 4. User can upgrade to full account later
```

## Configuration and Setup

### Environment Variables
```env
# Existing boilerplate variables
DATABASE_URL=postgresql://user:pass@localhost:5432/db
SECRET_KEY=your-jwt-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Assessment-specific variables
DEFAULT_ASSESSMENT_LIMIT=3
PREMIUM_ASSESSMENT_LIMIT=50
SHARE_TOKEN_LENGTH=32
TEMP_PASSWORD_LENGTH=12
```

### Database Migration
```sql
-- Add to your migration files
-- 1. Create user_profiles table
-- 2. Create assessments table  
-- 3. Create categories, questions, question_options tables
-- 4. Add indexes for performance
-- 5. Seed initial assessment content
```

### Router Registration
```python
# In main.py or router configuration
from app.api.v1 import (
    login,           # Existing
    users,           # Existing
    lead_capture,    # New
    assessments,     # New
    categories,      # New
    questions,       # New
    question_options # New
)

app.include_router(login.router, prefix="/api/v1", tags=["auth"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(lead_capture.router, prefix="/api/v1/lead-capture", tags=["leads"])
app.include_router(assessments.router, prefix="/api/v1/assessments", tags=["assessments"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(questions.router, prefix="/api/v1/questions", tags=["questions"])
app.include_router(question_options.router, prefix="/api/v1/question-options", tags=["options"])
```

## Frontend Integration

### Assessment Widget Integration
```javascript
// 1. Lead capture
const captureResponse = await fetch('/api/v1/lead-capture/capture-lead', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        email: 'user@example.com',
        company_name: 'Acme Corp'
    })
});

const { user_id, can_take_assessment } = await captureResponse.json();

// 2. Start assessment
if (can_take_assessment) {
    const startResponse = await fetch('/api/v1/assessments/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id })
    });
    
    const { assessment_id } = await startResponse.json();
}

// 3. Load questions
const questionsResponse = await fetch('/api/v1/assessment-data/full');
const { categories } = await questionsResponse.json();

// 4. Submit answers
const submitResponse = await fetch('/api/v1/assessments/submit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        assessment_id,
        answers: [
            {
                question_id: 1,
                selected_options: [1, 3]
            }
        ]
    })
});

const results = await submitResponse.json();
```

### Dashboard Integration
```javascript
// For registered users with JWT
const token = localStorage.getItem('access_token');

// Get user's assessment history
const historyResponse = await fetch(`/api/v1/assessments/user/${user_id}`, {
    headers: { 'Authorization': `Bearer ${token}` }
});

const assessments = await historyResponse.json();
```

## Security Considerations

### Authentication Levels
1. **Public Access**: Lead capture, assessment taking
2. **User Access**: Assessment history, profile management
3. **Admin Access**: Content management, user administration

### Data Protection
- JWT tokens for authenticated access
- Temporary passwords for leads (secure random generation)
- Assessment results private by default
- Optional sharing via secure tokens
- Input validation and sanitization

### Rate Limiting
- Lead capture: 5 per minute per IP
- Assessment start: 1 per minute per user
- Assessment submit: 1 per 5 minutes per user
- API endpoints: Standard boilerplate limits

## Performance Optimization

### Database Optimization
```sql
-- Key indexes for performance
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_assessments_user_profile ON assessments(user_profile_id);
CREATE INDEX idx_assessments_status ON assessments(status);
CREATE INDEX idx_questions_category ON questions(category_id);
CREATE INDEX idx_question_options_question ON question_options(question_id);
```

### Caching Strategy
- Assessment content (categories/questions): Redis cache, 1 hour TTL
- User profiles: Application-level cache, 15 minutes TTL
- Assessment results: No caching (always fresh)

### Query Optimization
- Use select_related/joinedload for related data
- Paginate large result sets
- Limit assessment history to recent items
- Async database operations throughout

## Monitoring and Analytics

### Key Metrics
- Lead capture conversion rate
- Assessment completion rate
- Average assessment score by industry
- User registration conversion
- API response times
- Error rates by endpoint

### Logging
```python
# Assessment-specific logging
logger.info(f"Lead captured: {email} from {company_name}")
logger.info(f"Assessment started: {assessment_id} for user {user_id}")
logger.info(f"Assessment completed: {assessment_id} with score {percentage_score}%")
logger.warning(f"Assessment limit reached for user {user_id}")
logger.error(f"Assessment submission failed: {error_details}")
```

## Deployment Checklist

### Pre-deployment
- [ ] Database migrations applied
- [ ] Assessment content seeded
- [ ] Environment variables configured
- [ ] JWT secrets properly set
- [ ] Rate limiting configured
- [ ] CORS settings updated

### Post-deployment
- [ ] Health check endpoints responding
- [ ] Authentication flow working
- [ ] Lead capture functional
- [ ] Assessment flow complete
- [ ] Email notifications working (if implemented)
- [ ] Monitoring alerts configured

## Troubleshooting

### Common Issues

#### 1. Authentication Integration
**Problem**: JWT tokens not working with assessment endpoints
**Solution**: Ensure `get_current_user` dependency is properly imported and used

#### 2. Database Relationships
**Problem**: UserProfile not found for existing users
**Solution**: Run migration to create UserProfile records for existing users

#### 3. Assessment Limits
**Problem**: Users can't take assessments despite having remaining attempts
**Solution**: Check `assessments_count` vs `max_assessments` in UserProfile

#### 4. Scoring Calculation
**Problem**: Incorrect assessment scores
**Solution**: Verify question weights and option score_points are properly set

### Debug Commands
```bash
# Check database connections
docker-compose exec web python -c "from app.core.database import async_get_db; print('DB OK')"

# Verify user profiles
docker-compose exec db psql -U user -d db -c "SELECT COUNT(*) FROM user_profiles;"

# Check assessment content
docker-compose exec db psql -U user -d db -c "SELECT COUNT(*) FROM questions WHERE is_active = true;"

# Test API endpoints
curl -X POST http://localhost:8000/api/v1/lead-capture/capture-lead \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'
```

## Future Enhancements

### Phase 1 (Current)
- [x] Lead capture and assessment flow
- [x] Basic scoring and recommendations
- [x] Integration with existing auth

### Phase 2 (Next)
- [ ] Email notifications and follow-up sequences
- [ ] Advanced analytics and reporting
- [ ] Custom branding and white-labeling
- [ ] API rate limiting per subscription tier

### Phase 3 (Future)
- [ ] Multi-tenant architecture
- [ ] Advanced recommendation engine
- [ ] Integration with security tools
- [ ] Mobile app support

This integration guide provides a complete overview of how the assessment system works with the existing FastAPI boilerplate, ensuring seamless operation and future scalability.
