# SSO-Enabled File Explorer (Python FastAPI)

A full-stack file explorer application with Single Sign-On (SSO) authentication built with Python FastAPI backend and React frontend.

## Features

- ✅ SSO Authentication (Google & Microsoft)
- ✅ File Upload/Download/Delete
- ✅ Folder Creation and Navigation
- ✅ Drag & Drop Interface
- ✅ RESTful API with FastAPI automatic documentation
- ✅ Dockerized Development Environment
- ✅ User-isolated file storage
- ✅ Security protection against path traversal

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Runtime**: Python 3.11
- **Authentication**: JWT with Google/Microsoft OAuth
- **File Handling**: aiofiles for async file operations
- **Documentation**: Automatic OpenAPI/Swagger

### Frontend
- **Framework**: React 18
- **Authentication**: Google OAuth & Microsoft MSAL
- **File Upload**: React Dropzone
- **UI**: Custom components with React Icons

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd file-explorer
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your OAuth credentials
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Alternative API docs: http://localhost:8000/redoc

## Environment Setup

### Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select a project and enable Google+ API
3. Create OAuth 2.0 credentials
4. Add `http://localhost:3000` to authorized origins

### Microsoft OAuth Setup
1. Go to [Azure Portal](https://portal.azure.com/)
2. Register a new application
3. Configure redirect URIs for `http://localhost:3000`
4. Generate client secret

### Required Environment Variables
```env
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret
JWT_SECRET=your_jwt_secret_key
```

## Development

### Running Backend Locally
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Running Frontend Locally
```bash
cd frontend
npm install
npm start
