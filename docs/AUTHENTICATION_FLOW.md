# Authentication Flow - Security Assessment Platform

## 🔐 Complete Authentication Architecture

This document provides detailed mermaid diagrams and technical specifications for the authentication flow in the Security Assessment Platform.

## 🎯 High-Level User Flow

```mermaid
graph TD
    A[User visits assessment page] --> B[Enters email address]
    B --> C{Email exists in database?}
    
    C -->|No| D[Create new account]
    C -->|Yes| E[Show 'Welcome back' modal]
    
    D --> F[Generate temporary password]
    F --> G[Store user with hashed password]
    G --> H[Return user_id + temp_password]
    
    E --> I[Load existing user data]
    I --> J[Return user_id + existing status]
    
    H --> K[Start new assessment]
    J --> K
    
    K --> L[Create assessment record]
    L --> M[Return assessment_id]
    M --> N[Load questions from API]
    N --> O[Show assessment interface]
    
    O --> P[User answers questions]
    P --> Q[Submit with authentication]
    Q --> R[Validate JWT token]
    R --> S[Calculate results]
    S --> T[Store results in database]
    T --> U[Show results page]
    
    U --> V{User interested in contact?}
    V -->|Yes| W[Send login link via email]
    V -->|No| X[Store as lead for nurturing]
    
    W --> Y[User clicks email link]
    Y --> Z[Auto-authenticate with embedded credentials]
    Z --> AA[Redirect to dashboard]
    AA --> BB[View assessment history]
```

## 🔧 Technical Authentication Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant D as Database
    participant E as Email Service
    
    Note over U,E: Account Creation Phase
    U->>F: Enter email address
    F->>A: POST /api/v1/lead-capture/capture-lead
    A->>D: Check if user exists
    
    alt User doesn't exist
        A->>A: Generate temporary password
        A->>A: Hash password with bcrypt
        A->>D: INSERT new user record
        A->>F: Return {user_id, temporary_password, is_existing_user: false}
    else User exists
        A->>F: Return {user_id, is_existing_user: true}
    end
    
    Note over U,E: Assessment Start Phase
    F->>A: POST /api/v1/assessment/start {user_id}
    A->>D: Check/create UserProfile
    A->>D: INSERT assessment record
    A->>F: Return {assessment_id, questions_count}
    
    F->>A: GET /api/v1/assessment/data/full
    A->>D: SELECT categories, questions, options
    A->>F: Return nested question data
    F->>U: Show assessment interface
    
    Note over U,E: Assessment Submission Phase (Authenticated)
    U->>F: Submit assessment answers
    F->>A: POST /api/v1/login {email, temporary_password}
    A->>A: Validate credentials
    A->>F: Return JWT token
    
    F->>A: POST /api/v1/assessment/submit {answers} + Bearer token
    A->>A: Validate JWT token
    A->>D: INSERT user_answers
    A->>D: UPDATE assessment with results
    A->>F: Return assessment results
    
    Note over U,E: Email Login Link Phase
    F->>A: POST /api/v1/email/send-login-link {email}
    A->>A: Generate secure login token
    A->>E: Send email with embedded credentials
    E->>U: Deliver login email
    
    U->>F: Click email login link
    F->>F: Extract credentials from URL
    F->>A: POST /api/v1/login {extracted credentials}
    A->>F: Return JWT token
    F->>U: Redirect to authenticated dashboard
```

## 🛡️ Security Architecture

```mermaid
graph LR
    subgraph "Public Endpoints"
        A[Lead Capture]
        B[Assessment Start]
        C[Question Loading]
        D[Health Checks]
    end
    
    subgraph "Protected Endpoints"
        E[Assessment Submit]
        F[Results Viewing]
        G[Dashboard Access]
        H[User Profile]
    end
    
    subgraph "Authentication Layer"
        I[JWT Token Validation]
        J[Password Hashing]
        K[Credential Verification]
    end
    
    subgraph "Database Security"
        L[Parameterized Queries]
        M[Password Hashing]
        N[UUID Primary Keys]
    end
    
    A --> I
    B --> I
    E --> I
    F --> I
    G --> I
    H --> I
    
    I --> J
    I --> K
    J --> L
    K --> M
    L --> N
```

## 📊 Database Authentication Schema

```mermaid
erDiagram
    USERS {
        uuid id PK
        string email UK
        string hashed_password
        timestamp created_at
        timestamp updated_at
    }
    
    USER_PROFILES {
        uuid id PK
        uuid user_id FK
        int assessments_count
        int max_assessments
        string tier
        timestamp created_at
    }
    
    ASSESSMENTS {
        uuid id PK
        uuid user_profile_id FK
        string status
        float overall_score
        float total_score
        boolean interested_in_contact
        timestamp created_at
        timestamp completed_at
    }
    
    USER_ANSWERS {
        uuid id PK
        uuid assessment_id FK
        uuid question_id FK
        json selected_options
        boolean is_correct
        float points_earned
        timestamp created_at
    }
    
    USERS ||--|| USER_PROFILES : "has profile"
    USER_PROFILES ||--o{ ASSESSMENTS : "takes assessments"
    ASSESSMENTS ||--o{ USER_ANSWERS : "contains answers"
```

## 🔑 Authentication States

```mermaid
stateDiagram-v2
    [*] --> Anonymous
    
    Anonymous --> EmailSubmitted : Enter email
    EmailSubmitted --> NewUser : Email not found
    EmailSubmitted --> ExistingUser : Email found
    
    NewUser --> AccountCreated : Generate temp password
    ExistingUser --> WelcomeBack : Show welcome modal
    
    AccountCreated --> AssessmentStarted : Start assessment
    WelcomeBack --> AssessmentStarted : Continue/start new
    
    AssessmentStarted --> TakingAssessment : Load questions
    TakingAssessment --> Authenticating : Submit answers
    
    Authenticating --> Authenticated : Valid credentials
    Authenticating --> AuthError : Invalid credentials
    
    Authenticated --> ResultsViewed : Show results
    ResultsViewed --> EmailSent : Send login link
    ResultsViewed --> LeadStored : Store as lead
    
    EmailSent --> DashboardAccess : Click email link
    DashboardAccess --> [*]
    
    AuthError --> Authenticating : Retry
    LeadStored --> [*]
```

## 🚀 API Endpoint Authentication Matrix

| Endpoint | Method | Authentication | Purpose |
|----------|--------|----------------|---------|
| `/api/v1/lead-capture/capture-lead` | POST | ❌ None | Create user account |
| `/api/v1/assessment/start` | POST | ❌ None | Start assessment |
| `/api/v1/assessment/data/full` | GET | ❌ None | Load questions |
| `/api/v1/login` | POST | ❌ None | Get JWT token |
| `/api/v1/assessment/submit` | POST | ✅ JWT | Submit answers |
| `/api/v1/assessment/results/{id}` | GET | ✅ JWT | View results |
| `/api/v1/dashboard/*` | GET | ✅ JWT | Dashboard access |
| `/api/v1/email/send-login-link` | POST | ❌ None | Send login email |

## 🔐 Password Security Implementation

```mermaid
graph TD
    A[Generate Temporary Password] --> B[12+ Character Random String]
    B --> C[Include: Letters, Numbers, Symbols]
    C --> D[Hash with bcrypt]
    D --> E[Salt Rounds: 12]
    E --> F[Store Hashed Password Only]
    
    G[User Login Attempt] --> H[Receive Plain Password]
    H --> I[Hash with bcrypt]
    I --> J[Compare with Stored Hash]
    J --> K{Match?}
    K -->|Yes| L[Generate JWT Token]
    K -->|No| M[Return Authentication Error]
    
    L --> N[Set Token Expiration]
    N --> O[Return Token to Client]
    O --> P[Client Stores Token]
    P --> Q[Use Token for Protected Requests]
```

## 📧 Email Login Link Flow

```mermaid
graph TD
    A[User Completes Assessment] --> B[Results Displayed]
    B --> C{Interested in Contact?}
    
    C -->|Yes| D[Generate Login Token]
    C -->|No| E[Store as Lead Only]
    
    D --> F[Base64 Encode Credentials]
    F --> G[Create Secure Login URL]
    G --> H[Generate HTML Email]
    H --> I[Send via SMTP]
    
    I --> J[User Receives Email]
    J --> K[User Clicks Login Link]
    K --> L[Extract Credentials from URL]
    L --> M[Auto-authenticate User]
    M --> N[Redirect to Dashboard]
    
    E --> O[Add to Email Nurturing List]
```

## 🛠️ Implementation Details

### Frontend Authentication State
```javascript
class AssessmentApp {
  constructor() {
    this.userId = null;
    this.assessmentId = null;
    this.temporaryPassword = null;
    this.jwtToken = null;
  }
  
  async authenticate() {
    const response = await fetch('/api/v1/login', {
      method: 'POST',
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: `username=${this.userEmail}&password=${this.temporaryPassword}`
    });
    
    const data = await response.json();
    this.jwtToken = data.access_token;
    return this.jwtToken;
  }
}
```

### Backend Authentication Middleware
```python
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"email": email, "id": payload.get("user_id")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

## 🔍 Testing Authentication Flow

### Manual Testing Steps
1. **Clear Test Data**: Remove existing test users from database
2. **Account Creation**: Test with fresh email address
3. **Assessment Flow**: Verify assessment start works without auth
4. **Submission**: Confirm submission requires authentication
5. **Email Links**: Test login link generation and usage
6. **Dashboard**: Verify authenticated dashboard access

### API Testing Commands
```bash
# 1. Create account
curl -X POST "http://localhost:8000/api/v1/lead-capture/capture-lead" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# 2. Get JWT token
curl -X POST "http://localhost:8000/api/v1/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=TEMP_PASSWORD_FROM_STEP_1"

# 3. Submit assessment (authenticated)
curl -X POST "http://localhost:8000/api/v1/assessment/submit" \
  -H "Authorization: Bearer JWT_TOKEN_FROM_STEP_2" \
  -H "Content-Type: application/json" \
  -d '{"assessment_id": "uuid", "answers": {...}}'
```

---

*Last Updated: 2025-07-14*  
*Version: 2.0 - Complete Authentication Architecture*
