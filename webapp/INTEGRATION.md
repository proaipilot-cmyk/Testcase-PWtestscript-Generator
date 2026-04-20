# Frontend-Backend Integration Guide

## Overview
The web application provides a complete workflow for test automation with integrated frontend UI and FastAPI backend.

## Workflow Stages

### 1. **Upload** (Stage 1 - Parser)
- **Frontend**: Sidebar upload button triggers file selection
- **Backend**: `/api/upload` (POST) receives FormData with file
- **Process**:
  - Removes existing file if locked
  - Saves uploaded file to `data/` directory
  - Triggers pipeline parsing in background
  - Logs file size and progress
- **Next Step**: Automatically starts Parser task

### 2. **Parse** (Stage 1 - Parser)
- **Backend**: Parses uploaded CSV/JSON file
- **Status**: Shows "In Progress" → "Completed"
- **Progress**: Updates to 20%
- **Logs**: Records parser completion

### 3. **Plan** (Stage 2 - Planner)
- **Backend**: Generates test plan from parsed data
- **Status**: Shows "In Progress" → "Completed"
- **Progress**: Updates to 40%
- **Logs**: Records planner actions

### 4. **Generate** (Stage 3 - Generator)
- **Backend**: Scaffolds POM framework
- **Status**: Shows "In Progress" → "Completed"
- **Progress**: Updates to 60%
- **Logs**: Records generator completion
- **Unlock**: Run button becomes enabled

### 5. **Run Tests** (Stage 4 - Run)
- **Frontend**: ControlPanel "Run Automation" button enabled after Generator completion
- **Backend**: `/api/run` (POST) executes pytest
- **Process**:
  - Runs pytest in background
  - Captures stdout/stderr
  - Logs test output
- **Status**: Shows "In Progress" → "Completed"
- **Next Step**: Git push becomes available after completion

### 6. **Push to Git** (Stage 5 - Push to Git)
- **Frontend**: GitStage component with URL, branch, token, and file selection
- **Backend**: `/api/push-to-git` (POST) receives GitPushData model
- **Process**:
  - Initializes or opens existing Git repository
  - Configures remote origin with URL
  - Optionally injects authentication token
  - Stages selected files (individual file, folder, or all)
  - Commits changes with timestamp
  - Pushes to target branch
- **Status**: Shows "In Progress" → "Completed"

## API Endpoints

### GET /api/progress
Returns current state:
```json
{
  "current_stage": "Idle",
  "progress": 0,
  "tasks": [...],
  "logs": [...]
}
```

### POST /api/upload
- **Content-Type**: multipart/form-data
- **Parameters**: file (UploadFile)
- **Response**: {"info": "file saved"} or {"error": "..."}

### POST /api/run
- **Response**: {"message": "Tests started"}

### POST /api/push-to-git
- **Content-Type**: application/json
- **Body**: 
```json
{
  "url": "https://github.com/user/repo.git",
  "branch": "main",
  "files": ["tests/test_automation.py"],
  "token": "optional_token"
}
```
- **Response**: {"message": "Git operational sequence started"}

### POST /api/clear-log
- **Response**: {"message": "Logs cleared"}

## State Management

### Frontend (React Context)
- **WorkflowContext**: Manages global state for all components
- **useWorkflow Hook**: Provides access to:
  - `tasks`: Array of pipeline tasks with status
  - `logs`: Array of log entries
  - `currentStage`: Current processing stage
  - `handleUpload`: Upload file handler
  - `handleRun`: Test execution handler
  - `handleGitPush`: Git push handler
  - `refreshData`: Manual data refresh

### Backend (FastAPI State)
- Global `state` dictionary maintains:
  - `current_stage`: Active stage name
  - `progress`: Percentage (0-100)
  - `tasks`: Array with status for each stage
  - `logs`: Array of log messages with timestamps

## UI Constraints

1. **Upload Button**: Disabled while any stage is processing
2. **Run Button**: Only enabled after Generator (stage 3) completes
3. **Git Push Button**: Only enabled after Run (stage 4) completes
4. **Input Fields**: All Git fields disabled until Run completes

## Error Handling

- **Upload Errors**: Permission denied → Removed existing file → Retry
- **Run Errors**: Captured in logs, status set to "Failed"
- **Git Errors**: Logged with full exception details
- **Frontend**: Error banner with "Retry" button displays issues

## Polling

Frontend polls `/api/progress` every 2 seconds to update:
- Task statuses
- Progress percentage
- Logs
- Current stage

## To Test Locally

1. Backend: `cd webapp && uvicorn server:app --reload`
2. Frontend: `cd webapp && npm run dev`
3. Navigate to `http://localhost:5173/`
4. Follow the workflow: Upload → Run → Push to Git

## File Progress Tracking

During upload and processing, logs show:
- File size in bytes
- Upload completion
- Each pipeline stage with percentage
- Task status changes
- Git operations details
