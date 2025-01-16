# main.py
from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import openai
import PyPDF2
from PIL import Image
import pytesseract
import io
import os
from dotenv import load_dotenv
import httpx  # Import httpx for making HTTP requests
import logging
import json
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor
from documents.standard_documents import Resume, EmployerDetail, Invoice, Receipt, Report
from pydantic import ValidationError

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

# Set your Azure OpenAI API settings from environment variables
openai.api_type = os.getenv("AZURE_OPENAI_API_TYPE")
openai.api_base = os.getenv("AZURE_OPENAI_API_BASE")
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")

# Determine the model type
model_type = os.getenv("MODEL_TYPE")

# Specify the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# In-memory storage for task results (for demonstration purposes)
task_results = {}

# Create a ThreadPoolExecutor for blocking calls
executor = ThreadPoolExecutor()

def extract_text_from_pdf(file_stream: io.BytesIO) -> str:
    reader = PyPDF2.PdfReader(file_stream)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_image(file_stream: io.BytesIO) -> str:
    image = Image.open(file_stream)
    text = pytesseract.image_to_string(image)
    return text

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

async def run_openai_api(prompt: str, text: str):
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(executor, lambda: openai.ChatCompletion.create(
        engine="YOUR_GPT_MODEL_NAME",
        messages=[
            {"role": "user", "content": f"{prompt}\n\n{text}"}
        ]
    ))
    return response

async def process_file(file_contents: bytes, content_type: str, custom_prompt: str, task_id: str):
    try:
        file_stream = io.BytesIO(file_contents)

        # Extract text based on file type
        if content_type == "application/pdf":
            text = extract_text_from_pdf(file_stream)
        elif content_type in ["image/jpeg", "image/png"]:
            text = extract_text_from_image(file_stream)
        else:
            raise ValueError("Unsupported file type")

        logging.info("Extracted text from file: %s", text[:100])  # Log the first 100 characters of the extracted text

        # Convert text to English if necessary
        convert_prompt = f"Translate the following text to English:\n{text}"
        if model_type == "ollama":
            translated_text = await call_local_ollama_model(convert_prompt, text)  # Use Ollama for translation
        elif model_type == "azure":
            translated_text = await run_openai_api(convert_prompt, text)  # Use Azure OpenAI for translation

        logging.info("Translated text: %s", translated_text[:100])  # Log the first 100 characters of the translated text

        # If a custom prompt is provided, call the appropriate model
        if custom_prompt:
            if model_type == "ollama":
                response = await call_local_ollama_model(custom_prompt, translated_text)  # Await the async call
                task_results[task_id]["result"] = response
            elif model_type == "azure":
                response = await run_openai_api(custom_prompt, translated_text)  # Await the OpenAI API call
                task_results[task_id]["result"] = response.choices[0].message['content']
        else:
            # If no custom prompt is provided, identify the document type
            identify_prompt = "Return only the document type without any explanation. Identify the type of document based on the following text:\n"
            if model_type == "ollama":
                document_type_response = await call_local_ollama_model(identify_prompt, translated_text)  # Use Ollama to identify document type
            elif model_type == "azure":
                document_type_response = await run_openai_api(identify_prompt, translated_text)  # Use Azure OpenAI to identify document type

            # Assuming the response contains the document type
            document_type = document_type_response.strip().lower()  # Normalize the document type
            logging.info("Identified document type: %s", document_type)  # Log the identified document type

            # Extract details based on identified document type
            try:
                if "resume" in document_type:
                    resume_data = Resume.model_validate_json(text)  # Validate against Resume schema
                    task_results[task_id]["result"] = resume_data.model_dump()
                elif "invoice" in document_type:
                    invoice_data = Invoice.model_validate_json(text)  # Validate against Invoice schema
                    task_results[task_id]["result"] = invoice_data.model_dump()
                elif "receipt" in document_type:
                    receipt_data = Receipt.model_validate_json(text)  # Validate against Receipt schema
                    task_results[task_id]["result"] = receipt_data.model_dump()
                elif "report" in document_type:
                    report_data = Report.model_validate_json(text)  # Validate against Report schema
                    task_results[task_id]["result"] = report_data.model_dump()
                else:
                    # If no schema is available for the identified document type
                    task_results[task_id]["result"] = {"message": "Document type not supported."}
                    logging.warning("Document type '%s' is not supported.", document_type)  # Log warning for unsupported types
            except ValidationError as e:
                # Handle the case where the text does not match the expected schema
                task_results[task_id]["status"] = "failed"
                task_results[task_id]["result"] = str(e)
                logging.error("Validation error: %s", str(e))  # Log the validation error

            # Update the task status
            task_results[task_id]["status"] = "completed"
    except Exception as e:
        task_results[task_id]["status"] = "failed"
        task_results[task_id]["result"] = str(e)
        logging.error("An error occurred: %s", str(e))  # Log the error

async def call_local_ollama_model(prompt: str, text: str) -> str:
    ollama_url = "http://localhost:11434/api/generate"  # Update with your actual Ollama endpoint
    payload = {
        "model": "mistral",  # Specify the model name
        "prompt": f"If non english is identified convert it to english.\n {prompt}\n\n{text}",  # Combine the prompt and extracted text
        "stream": False  # Set stream to boolean false
    }

    async with httpx.AsyncClient() as client:
        try:
            # Send the request asynchronously
            response = await client.post(ollama_url, json=payload)
            response.raise_for_status()  # Raise an error for bad responses
            
            # Log the full response
            logging.info("Full response from Ollama model: %s", response.text)
            
            # Attempt to parse JSON
            try:
                json_response = response.json()  # Use response.json() to parse the response
                return json_response.get("response", "No response from Ollama model")
            except ValueError:
                # Handle the case where the response is not JSON
                return response.text  # Return the raw text response

        except httpx.HTTPStatusError as e:
            return f"Error calling local Ollama model: {e.response.text}"
        except Exception as e:
            return f"An error occurred: {str(e)}"

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id in task_results:
        return task_results[task_id]
    else:
        return JSONResponse(content={"error": "Task ID not found"}, status_code=404)

# Run the application with: uvicorn main:app --reload