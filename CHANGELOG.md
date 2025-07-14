# Changelog

All notable changes to the Security Assessment API will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.0.0] - 2025-07-14

### Added

- **Seamless Auto-Login and Assessment Flow**: Complete user flow refactor from email entry to assessment completion.
- **Complete Endpoint Coverage**: Over 100 endpoints are now functional, including core user features, a full admin dashboard backend, and system health monitoring.
- **Auto-Account Creation**: Users automatically get accounts with temporary passwords upon email submission.
- **Email Service Integration**: Full SMTP integration with HTML templates and secure login link generation.

### Changed

- **Authentication Architecture**: Proper separation of public and protected endpoints.
- **Assessment Flow**: Sequential flow is now: Create Account → Start Assessment → Load Questions → Submit with Auth.
- **Router Registration**: Cleaned up router registrations, removed duplicates, and fixed prefixes for consistency.
- **User Creation Flow**: Lead capture now returns temporary passwords (API response change).

### Fixed

- **Systematic Import Path Errors**: Corrected all relative import paths across the backend, resolving all module-related startup errors.
- **Async/Await Implementation**: Correctly implemented async patterns and replaced all synchronous `Session` calls with `AsyncSession`.
- **Docker Environment**: Removed obsolete `version` attribute from `docker-compose.yml` and ensured stable container operation.
- **DOM Rendering**: Corrected element ID mismatch in the frontend from `questions-container` to `question-content`.
- **Database Constraints**: Eliminated duplicate key violations caused by test users.
- **Authentication Flow**: Implemented proper credential handling and token management.

### Breaking Changes

- **Assessment Start Endpoint**: Now works *without* authentication to support the new user flow.
- **Frontend Flow**: The frontend has been refactored to support the new API and authentication flow.

### Migration Notes

- Clear existing test users from the database before testing the new flow.
- Update frontend clients to handle the new API response format from the lead capture endpoint.
- Configure SMTP settings for production email delivery.

---

## [2.0.0] - 2024-01-13

### Added

- **Comprehensive Entity Coverage**: Added new database models and full CRUD API endpoints for `UserAnswer`, `CategoryScore`, `Recommendation`, `CustomerInfo`, `EmailNotification`, and `SubscriptionPlan`.
- **Advanced Filtering**: Implemented query parameters for filtering customer info by lead status and subscription plan.
- **Submission Tracking**: Added validation of submission limits based on subscription plans.
- **Multi-language Support**: Included Norwegian priority levels and recommendation text.

### Changed

- **Database Schema**: Enhanced schema with UUID primary keys, proper foreign keys, enums, array support, and cascade deletes.
- **Technical Improvements**: Enforced consistent import paths, full async/await support, and comprehensive error handling.

### Documentation

- **API Documentation**: Updated with all new endpoints, models, and authentication requirements.
- **Database Schema**: Documented all new entities and relationships.

---

## [1.0.0] - 2024-01-01

### Added

- **Initial Release**: Basic assessment system with categories, questions, and options.
- **Lead Capture**: Initial lead capture functionality.
- **User Authentication**: Integrated JWT authentication from the FastAPI boilerplate.
- **Infrastructure**: Docker Compose setup with PostgreSQL, Redis, and automated database migrations.

---

## Roadmap

### Future: Company Sharing & Collaboration

- Company assessment sharing functionality.
- Team collaboration features.
- Bulk assessment management.

### Future: Payment Integration

- Dintero payment processing.
- Subscription management and payment tracking.

### Future: Advanced Admin Features

- Admin user management.
- Advanced analytics dashboard and bulk data operations.

### Future: Enhanced Analytics

- Implementation of dashboard functions.
- Company submission tracking and advanced reporting.
