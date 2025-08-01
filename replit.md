# Tathya - Case Management System

## Overview

Tathya is a comprehensive case management system built with Streamlit for handling legal/compliance cases within an organization. The system provides role-based access control with different user interfaces for Initiators, Reviewers, Approvers, Legal Reviewers, Action Closure Authorities, and Administrators. It manages the complete lifecycle of cases from creation to closure with proper audit trails and document management.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (July 28, 2025)
- Enhanced Case Entry form with comprehensive demographic details:
  - Customer Name, Date of Birth, PAN, Address, Mobile Number, Email ID
  - Branch/Location, Loan Amount, Disbursement Date
- Implemented comprehensive User Master system with fields:
  - User ID, Password, Name, Team, Functional Designation, System Role, Referred By
  - Auto-fill "Referred By" in case entry based on user's stored referred_by value
  - Bulk imported 29 users from master list including:
    - Investigation team members (TLs, Managers, Executives)
    - Process & Analytics team members 
    - Regional and Location Investigation Managers
    - All users have proper team assignments and referral mappings
- Updated login system to use User ID/password authentication only:
  - Removed old username/password system completely
  - Implemented flexible role-based access control:
    - Users can login with assigned role only (default behavior)
    - Admin can assign "All Roles Access" to specific users
    - Users with all roles access can login as any role except Admin
    - Admin role access remains restricted to Admin users only
  - Clear error messages for unauthorized role access attempts
  - Removed old test users (initiator, reviewer, approver, etc.)
- Enhanced Admin functionality:
  - Admin can now assign/revoke "All Roles Access" to users
  - User management shows access level (specific role vs "All Roles")
  - Granted all roles access to 12 specified users for testing flexibility
- Promoted bg407629 to Admin role with full system access
- Removed "Address" field from all sections throughout the system
- Added TAT (Turn Around Time) metrics to dashboard:
  - Average TAT for Review, Approval, Legal Review, and Closure processes
  - TAT trend charts and SLA compliance metrics
- Changed nomenclature from "Action Closure Authority" to "Actioner" throughout system
- Removed Quick Access section from sidebar (kept only Navigation, User Info, and Logout)
- Enhanced User Management system for Admin users:
  - Comprehensive user profiles with all master fields
  - View all users with detailed information (Name, Team, Designation, etc.)
  - Add/edit users with complete profile information
  - Soft delete users (deactivate instead of permanent deletion)
- Enhanced validation for case entry:
  - PAN format validation (10 characters alphanumeric)
  - Mobile number validation (10 digits)
  - Email format validation
  - Loan amount validation (must be greater than 0)
- Enhanced Dashboard functionality:
  - Added Case ID and LAN columns to Recent Cases section
  - Added Case ID and LAN columns to Cases Requiring Approval section
  - Cases Requiring Review section now shows actual submitted cases
  - Cases Requiring Approval section now shows actual cases under review
- Implemented Advanced Gemini-Powered AI Assistant:
  - Integrated Google Gemini AI for intelligent case analysis and document generation
  - Smart Case Analysis: AI-powered analysis with risk assessment and investigation priorities
  - AI Document Generator: Automatically creates professional legal documents with context
  - Interactive AI Chat: Real-time assistance for investigation procedures and compliance guidance
  - Uses provided Gemini API key for secure, authenticated AI responses
  - Comprehensive analysis frameworks for all fraud types with intelligent insights
- Implemented AI-powered auto-suggestions/completion:
  - Quick remarks in all review stages (Review, Approval, Legal, Closure)
  - Predefined templates for common fraud scenarios and investigation findings
  - Context-aware suggestions based on case type and stage
  - Separate AI Assistant page for comprehensive case analysis and document generation
- Enhanced user experience with smart features:
  - Auto-completion for case descriptions and remarks
  - Consistent "AI Assistant" terminology throughout system
  - Interactive suggestion buttons in all comment fields
  - Template-based quick input across all workflow stages
- Updated database schema to support all user master fields
- Fixed LSP errors in user management and form validation
- Created New Investigator Role System (Latest Update):
  - Added new "Investigator" role with comprehensive access permissions
  - Investigators can access Case Entry, Reviewer Panel, and specialized Investigation Panel
  - Built complete Investigation Panel with four main tabs:
    - Case Management: Quick case entry and case review functionality
    - Investigation Details: Comprehensive investigation forms with document verification
    - Investigation Analytics: Status tracking and verification success rate metrics
    - PDF Report Generation: Professional investigation reports using ReportLab
  - Extended AI Assistant access to include Investigator role
  - Implemented detailed investigation workflow with verification tracking
  - Added professional PDF report generation for investigation documentation
- Enhanced AI Assistant User Experience:
  - Removed duplicate "Show Cause Notice Template" section
  - Added "Enhance Description" feature for case summaries using AI
  - Implemented hidden label with app navigation terms for system reference
  - Added professional footer "Powered by Fraud Risk Management Unit" in ABCL red color
  - Improved case description enhancement with AI-powered suggestions
- Integrated AI Enhancement in Case Entry Form:
  - Added "Enhance Description" feature directly in Case Entry form
  - AI-powered case description improvement using Gemini
  - Users can type basic description and get professionally enhanced version
  - Maintains original case entry workflow while adding AI assistance
  - Updated UI with concise instruction: "Tip: Type your case summary. Click 'Enhance Description' to improve it using AI."
  - Compact "✨ Enhance" button positioned in bottom-right corner with proper styling
  - Post-login AI tip popup appears for Initiator, Investigator, and Admin roles (session-based, shows once per login)
- Enhanced Investigation Panel with Comprehensive Case Auto-Fetch:
  - Implemented auto-fetch functionality: Enter Case ID and click "🔍 Fetch Details" to populate all fields
  - Auto-populates: LAN, Customer Name, Mobile Number, Email, PAN, Date of Birth, Loan Amount, Branch/Location, Case Description, Case Type, Product, Region, Referred By, Case Date, Disbursement Date
  - Comprehensive investigation details form with document verification tracking
  - Save investigation findings to database with complete reviewer workflow integration
  - Investigation data automatically added to case comments for reviewer access
  - Auto-updates case status based on investigation completion (Draft → Submitted → Under Review)
  - Complete demographic data flow from Investigation Panel to reviewer workflow
  - Professional investigation tracking with audit trail and status management
- Implemented Auto-Generated Case ID System:
  - Standardized Case ID format: CASE20250728CE806A (CASE + YYYYMMDD + 2 letters + 3 digits + 1 letter)
  - Auto-generation in Case Entry form with "🔄 Generate New ID" button
  - Auto-generation in Investigation Panel for new cases
  - Consistent Case ID format across all pages including Dashboard, Reviewer Panel, Approver Panel
  - Case ID displayed and tracked throughout complete workflow from creation to closure
  - Unique ID ensures no duplicates and maintains professional case tracking standards

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