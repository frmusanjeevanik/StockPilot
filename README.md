# Tathya - Case Management System

A comprehensive AI-powered case management system for legal and investigative workflows.

## Features

- Role-based access control (Admin, Initiator, Reviewer, Approver, Legal Reviewer, Investigator, Actioner)
- AI-powered case analysis and document generation using Google Gemini
- Investigation panel with comprehensive tracking
- Analytics dashboard with performance metrics
- Document management and audit trails
- Gamified achievement system

## Deployment

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
export GEMINI_API_KEY=your_gemini_api_key_here
```

3. Initialize the system:
```bash
python setup.py
```

4. Run the application:
```bash
streamlit run app.py
```

### Streamlit Cloud Deployment

1. Push your code to GitHub
2. Connect your GitHub repository to Streamlit Cloud
3. Set the following secrets in Streamlit Cloud:
   - `GEMINI_API_KEY`: Your Google Gemini API key
4. Deploy with main file: `app.py`

## Environment Variables

- `GEMINI_API_KEY`: Required for AI functionality

## Project Structure

- `app.py`: Main Streamlit application
- `auth.py`: Authentication system
- `database.py`: Database operations
- `models.py`: Data models
- `pages/`: Individual page modules
- `uploads/`: File storage directory
- `exports/`: Report export directory

## User Roles

- **Admin**: Full system access and user management
- **Initiator**: Create and submit cases
- **Reviewer**: Review submitted cases
- **Approver**: Approve reviewed cases
- **Legal Reviewer**: Handle legal compliance
- **Investigator**: Conduct investigations
- **Actioner**: Close completed cases

## AI Features

- Smart case analysis and risk assessment
- Automated document generation
- Interactive chat assistance
- Enhanced case descriptions
- Investigation insights

## Support

For technical support or deployment issues, contact the development team.