# main.py
from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from processor import process_file
from dotenv import load_dotenv
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
import traceback



# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Specify the path to the Tesseract executable


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# In-memory storage for task results (for demonstration purposes)
task_results = {}

# Create a ThreadPoolExecutor for blocking calls
executor = ThreadPoolExecutor()



@app.post("/upload/", status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    custom_prompt: str = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    task_id = str(uuid.uuid4())  # Generate a unique ID for the task
    logging.info("Received file: %s", file.filename)
    logging.info("Custom prompt: %s", custom_prompt)

    # Store the initial state of the task
    task_results[task_id] = {"status": "processing", "result": None}

    # Read the file contents
    file_contents = await file.read()  # Read the file contents asynchronously

    # Add the processing task to the background
    background_tasks.add_task(process_file, file_contents, file.content_type, custom_prompt, task_id)
    logging.info("Request submitted for File Name : %s with Task ID: %s", file.filename,task_id)
    return {"task_id": task_id}  # Return the task ID



@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id in task_results:
        return task_results[task_id]
    else:
        return JSONResponse(content={"error": "Task ID not found"}, status_code=404)

# Run the application with: uvicorn main:app --reload