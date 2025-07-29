# Streamlit Cloud Deployment Guide

## Common Deployment Issues and Solutions

### 1. Dependencies Issue
**Problem**: Duplicate or conflicting packages in requirements.txt
**Solution**: Use the clean requirements file:

```
streamlit>=1.47.1
pandas>=2.3.1
plotly>=6.2.0
google-genai>=0.3.0
reportlab>=4.0.0
requests>=2.31.0
```

### 2. Environment Variables
**Problem**: Missing GEMINI_API_KEY in Streamlit Cloud
**Solution**: 
1. Go to your Streamlit Cloud app dashboard
2. Click on "Settings" → "Secrets"
3. Add: `GEMINI_API_KEY = "your_api_key_here"`

### 3. Database Initialization
**Problem**: Database not initialized on first deployment
**Solution**: The app automatically creates the database on first run

### 4. File Paths
**Problem**: Absolute paths breaking in cloud environment
**Solution**: All paths are already relative (./uploads, ./exports, etc.)

### 5. Missing Directories
**Problem**: Upload/export directories not created
**Solution**: The app creates directories automatically

## Deployment Steps

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Deploy to Streamlit Cloud"
   git push origin main
   ```

2. **Connect to Streamlit Cloud**:
   - Go to https://share.streamlit.io/
   - Connect your GitHub repository
   - Set main file as: `app.py`

3. **Set Secrets**:
   - Add `GEMINI_API_KEY` in app settings

4. **Deploy**:
   - Click "Deploy" and wait for build completion

## Troubleshooting

### Build Fails
1. Check requirements.txt for conflicts
2. Ensure all imports are available
3. Check for syntax errors in Python files

### App Crashes on Start
1. Verify GEMINI_API_KEY is set correctly
2. Check database initialization
3. Review error logs in Streamlit Cloud

### Features Not Working
1. Confirm all environment variables are set
2. Check file permissions for uploads
3. Verify database tables are created

## Testing Locally Before Deployment

```bash
# Test dependencies
pip install -r requirements_for_deployment.txt

# Test the app
streamlit run app.py

# Check for errors
python setup.py
```