# Tathya - Case Management System

## Overview

Tathya is a comprehensive case management system built with Streamlit for handling legal/compliance cases within an organization. The system provides role-based access control with different user interfaces for Initiators, Reviewers, Approvers, Legal Reviewers, Action Closure Authorities, and Administrators. It manages the complete lifecycle of cases from creation to closure with proper audit trails and document management.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (July 26, 2025)
- Fixed plotly visualization errors in analytics dashboard
- Updated login page layout with proper logo placement (Tathya left, login form right, ABCL top-right)
- Reorganized sidebar navigation (Navigation section appears first, then user welcome)
- Renamed "Closure Panel" to "🔒 Action Closure Panel" in navigation
- Removed Analytics from main navigation for cleaner interface
- Added custom logo support with fallback to text logos
- Fixed pandas date range deprecation warnings

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application
- **UI Pattern**: Multi-page application with role-based navigation
- **Layout**: Wide layout with responsive columns and tabs
- **State Management**: Streamlit session state for authentication and user context
- **Navigation**: Sidebar-based navigation with role-specific menu options

### Backend Architecture
- **Application Layer**: Python-based business logic with modular page structure
- **Authentication**: Custom authentication system with session management
- **Authorization**: Role-based access control with decorators
- **Database Layer**: SQLite database with context manager pattern
- **File Management**: Local file system for document uploads

### Data Storage
- **Primary Database**: SQLite for case data, user management, and audit logs
- **File Storage**: Local filesystem with organized directory structure
- **Session Storage**: Streamlit session state for user authentication

## Key Components

### Authentication & Authorization
- **Problem**: Secure access control for different user roles
- **Solution**: Custom authentication with password hashing and session management
- **Roles**: Admin, Initiator, Reviewer, Approver, Legal Reviewer, Action Closure Authority
- **Security**: SHA-256 password hashing with role-based decorators

### Case Management Workflow
- **Problem**: Track cases through multiple approval stages
- **Solution**: Status-based workflow system with role-specific interfaces
- **Statuses**: Draft, Submitted, Under Review, Approved, Rejected, Legal Review, Closed
- **Features**: Case creation, document upload, comments, status transitions

### Document Management
- **Problem**: Handle supporting documents for cases
- **Solution**: File upload system with unique naming and metadata storage
- **Storage**: Local uploads directory with UUID-based naming
- **Metadata**: File size, original filename, upload timestamp tracking

### Audit System
- **Problem**: Track all case modifications and user actions
- **Solution**: Comprehensive audit logging with timestamps and user attribution
- **Coverage**: Case creation, status changes, comments, document uploads

### Analytics & Reporting
- **Problem**: Provide insights into case management performance
- **Solution**: Interactive dashboards with Plotly visualizations
- **Features**: Case statistics, status distribution, export capabilities

## Data Flow

1. **Case Creation**: Initiators create cases with supporting documents
2. **Review Process**: Reviewers examine cases and provide feedback
3. **Approval Workflow**: Approvers make final decisions on reviewed cases
4. **Legal Review**: Legal reviewers handle compliance aspects
5. **Case Closure**: Action Closure Authorities finalize completed cases
6. **Audit Trail**: All actions logged with user attribution and timestamps

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework
- **SQLite3**: Database connectivity
- **Pandas**: Data manipulation for analytics
- **Plotly**: Interactive visualization charts
- **Hashlib**: Password security

### File System Dependencies
- **uploads/**: Directory for case documents
- **exports/**: Directory for exported reports
- **case_management.db**: SQLite database file

## Deployment Strategy

### Local Development
- **Database**: SQLite file-based database
- **Files**: Local filesystem storage
- **Configuration**: Environment-based settings

### Production Considerations
- **Database**: Could be migrated to PostgreSQL for scalability
- **File Storage**: Could use cloud storage services
- **Authentication**: Could integrate with enterprise SSO
- **Scalability**: Multi-user concurrent access support

### Security Features
- **Password Protection**: SHA-256 hashing
- **Session Management**: Streamlit session state
- **Role Validation**: Decorator-based access control
- **Audit Logging**: Complete action tracking

### Backup & Recovery
- **Database**: SQLite file backup
- **Documents**: File system backup of uploads directory
- **Configuration**: Version-controlled application settings