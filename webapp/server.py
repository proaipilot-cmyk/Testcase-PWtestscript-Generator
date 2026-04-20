from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import subprocess
import json
from pathlib import Path
from datetime import datetime
import time
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
DATA_DIR = PROJECT_ROOT / "data"
TESTS_DIR = PROJECT_ROOT / "tests"
DATA_DIR.mkdir(exist_ok=True)

# Pydantic models for API
class GitPushData(BaseModel):
    url: str
    branch: str = "main"
    files: list = []
    token: str = ""

# State management
state = {
    "current_stage": "Idle",
    "progress": 0,
    "tasks": [
        {"id": "1", "name": "Parser", "status": "Pending", "lastUpdated": ""},
        {"id": "2", "name": "Planner", "status": "Pending", "lastUpdated": ""},
        {"id": "3", "name": "Generator", "status": "Pending", "lastUpdated": ""},
        {"id": "4", "name": "Run", "status": "Pending", "lastUpdated": ""},
        {"id": "5", "name": "Push to Git", "status": "Pending", "lastUpdated": ""}
    ],
    "logs": []
}

def add_log(msg):
    state["logs"].insert(0, {"id": str(time.time()), "message": msg, "time": datetime.now().isoformat()})

def update_task(task_id, status):
    for task in state["tasks"]:
        if task["id"] == task_id:
            task["status"] = status
            task["lastUpdated"] = datetime.now().isoformat()
            break

async def run_pipeline(file_path: Path):
    try:
        state["current_stage"] = "Parser"
        update_task("1", "In Progress")
        add_log(f"Starting Parser with file: {file_path.name}")
        # Mock Parser call
        time.sleep(2) 
        update_task("1", "Completed")
        add_log("Parser completed successfully.")
        state["progress"] = 20

        state["current_stage"] = "Planner"
        update_task("2", "In Progress")
        add_log("Starting Planner...")
        # Mock Planner call
        time.sleep(2)
        update_task("2", "Completed")
        add_log("Planner generated canonical actions.")
        state["progress"] = 40

        state["current_stage"] = "Generator"
        update_task("3", "In Progress")
        add_log("Starting Generator...")
        # Mock Generator call
        time.sleep(2)
        update_task("3", "Completed")
        add_log("Generator scaffolded POM framework.")
        state["progress"] = 60

        state["current_stage"] = "Idle"
        state["progress"] = 100
        add_log("All pipeline tasks completed successfully!")
    except Exception as e:
        error_msg = f"Error in pipeline: {str(e)}"
        add_log(error_msg)
        state["current_stage"] = "Error"
        state["progress"] = 0

@app.post("/api/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        add_log(f"Starting file upload: {file.filename}")
        file_location = DATA_DIR / file.filename
        
        # Close any existing file handle
        if file_location.exists():
            try:
                import os as os_module
                os_module.remove(file_location)
                add_log(f"Removed existing file: {file.filename}")
            except Exception as rm_err:
                add_log(f"Warning: Could not remove existing file: {str(rm_err)}")
        
        # Write file with progress tracking
        try:
            file.file.seek(0)  # Ensure we're at the start of the file
            with open(file_location, "wb") as file_object:
                shutil.copyfileobj(file.file, file_object)
        finally:
            file.file.close()
        
        add_log(f"File uploaded successfully: {file.filename} ({file_location.stat().st_size} bytes)")
        
        # Reset state
        state["progress"] = 0
        for task in state["tasks"]:
            task["status"] = "Pending"
        
        background_tasks.add_task(run_pipeline, file_location)
        add_log("Pipeline processing started in background")
        
        return {"info": f"file '{file.filename}' saved at '{file_location}'"}
    except PermissionError as pe:
        error_msg = f"Permission denied accessing file: {str(pe)}"
        add_log(error_msg)
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"Upload error: {str(e)}"
        add_log(error_msg)
        return {"error": error_msg}

@app.get("/api/progress")
async def get_progress():
    return state

@app.post("/api/run")
async def run_tests(background_tasks: BackgroundTasks):
    async def execute_tests():
        state["current_stage"] = "Run"
        update_task("4", "In Progress")
        add_log("Executing pytest...")
        try:
            # Run subprocess
            result = subprocess.run(["pytest", str(TESTS_DIR)], capture_output=True, text=True)
            add_log(result.stdout)
            if result.stderr:
                add_log(f"Errors: {result.stderr}")
            update_task("4", "Completed")
            add_log("Tests completed successfully")
        except Exception as e:
            add_log(f"Test execution failed: {str(e)}")
            update_task("4", "Failed")
        finally:
            state["current_stage"] = "Idle"

    background_tasks.add_task(execute_tests)
    return {"message": "Tests started"}

@app.post("/api/clear-log")
async def clear_logs():
    state["logs"] = []
    add_log("Logs cleared")
    return {"message": "Logs cleared"}

@app.post("/api/reset")
async def reset_workflow():
    """Reset all workflow state to initial values"""
    state["current_stage"] = "Idle"
    state["progress"] = 0
    for task in state["tasks"]:
        task["status"] = "Pending"
        task["lastUpdated"] = ""
    state["logs"] = []
    add_log("Workflow reset to initial state")
    return {"message": "Workflow reset successfully"}

@app.get("/api/upload")
async def upload_error():
    """Handle incorrect GET requests to /api/upload"""
    return {"error": "Use POST method with FormData containing 'file' field"}

@app.get("/api/run")
async def run_error():
    """Handle incorrect GET requests to /api/run"""
    return {"error": "Use POST method"}

@app.get("/api/push-to-git")
async def git_error():
    """Handle incorrect GET requests to /api/push-to-git"""
    return {"error": "Use POST method"}

@app.get("/api/reset")
async def reset_error():
    """Handle incorrect GET requests to /api/reset"""
    return {"error": "Use POST method to reset workflow"}

import git

@app.post("/api/push-to-git")
async def push_to_git(git_data: GitPushData, background_tasks: BackgroundTasks):
    git_url = git_data.url
    branch = git_data.branch or "main"
    files = git_data.files or []
    token = git_data.token or ""
    
    async def git_op():
        state["current_stage"] = "Push to Git"
        update_task("5", "In Progress")
        add_log(f"Starting Git operation for: {git_url}")
        
        try:
            # Initialize or open repo
            if not (PROJECT_ROOT / ".git").exists():
                add_log("Initializing new Git repository...")
                repo = git.Repo.init(PROJECT_ROOT)
            else:
                repo = git.Repo(PROJECT_ROOT)
            
            # Setup remote
            remote_name = "origin"
            if remote_name in repo.remotes:
                origin = repo.remotes[remote_name]
                origin.set_url(git_url)
            else:
                origin = repo.create_remote(remote_name, git_url)
            
            # Authentication handling (if token provided, inject into URL)
            if token and git_url.startswith("https://"):
                url_with_auth = git_url.replace("https://", f"https://oauth2:{token}@")
                origin.set_url(url_with_auth)
                add_log("Authentication token configured")
            
            # Staging
            if files == ["all"]:
                add_log("Staging all changes...")
                repo.git.add(A=True)
            else:
                for f in files:
                    if f == "tests/pages/": # Handle folder
                        repo.git.add("tests/pages")
                    else:
                        repo.git.add(f)
                add_log(f"Staged {len(files)} files")
            
            # Commit
            if repo.is_dirty(untracked_files=True):
                add_log("Committing changes...")
                repo.index.commit(f"Auto-commit: Test framework update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                add_log("Changes committed")
            else:
                add_log("No changes to commit (repo is clean)")
            
            # Push
            add_log(f"Pushing to branch: {branch}...")
            origin.push(f"HEAD:{branch}")
            add_log(f"Pushed to {branch} successfully!")
            
            update_task("5", "Completed")
        except Exception as e:
            error_msg = f"Git Error: {str(e)}"
            add_log(error_msg)
            update_task("5", "Failed")
        finally:
            state["current_stage"] = "Idle"

    background_tasks.add_task(git_op)
    return {"message": "Git operational sequence started"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
