# main.py
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import openai
import PyPDF2
from PIL import Image
import pytesseract
import io

app = FastAPI()

# CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set your Azure OpenAI API key and endpoint
openai.api_type = "azure"
openai.api_base = "YOUR_AZURE_OPENAI_ENDPOINT"
openai.api_key = "YOUR_AZURE_OPENAI_API_KEY"
openai.api_version = "2023-05-15"  # Update to the latest version if needed

def extract_text_from_pdf(file: UploadFile) -> str:
    reader = PyPDF2.PdfReader(file.file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_image(file: UploadFile) -> str:
    image = Image.open(file.file)
    text = pytesseract.image_to_string(image)
    return text

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    custom_prompt: str = Form(None)
):
    if file.content_type not in ["application/pdf", "image/jpeg", "image/png"]:
        return JSONResponse(content={"error": "Invalid file type"}, status_code=400)

    # Extract text based on file type
    if file.content_type == "application/pdf":
        text = extract_text_from_pdf(file)
    else:
        text = extract_text_from_image(file)

    # If a custom prompt is provided, call GPT-4o Mini
    if custom_prompt:
        response = openai.ChatCompletion.create(
            engine="YOUR_GPT_MODEL_NAME",
            messages=[
                {"role": "user", "content": f"{custom_prompt}\n\n{text}"}
            ]
        )
        return JSONResponse(content={"response": response.choices[0].message['content']})

    return JSONResponse(content={"extracted_text": text})

# Run the application with: uvicorn main:app --reload