import httpx  # Import httpx for making HTTP requests
import logging
import os
import io
import openai
import asyncio
import main
from pydantic import ValidationError
from documents.schemas import resume_schema, invoice_schema, receipt_schema, report_schema, passport_schema, driver_license_schema, national_id_schema, voter_id_schema, military_id_schema, green_card_schema  # Import schemas
import traceback
import PyPDF2
import pytesseract
from PIL import Image

# Set your Azure OpenAI API settings from environment variables
openai.api_type = os.getenv("AZURE_OPENAI_API_TYPE")
openai.api_base = os.getenv("AZURE_OPENAI_API_BASE")
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")

# Determine the model type
model_type = os.getenv("MODEL_TYPE")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#pytesseract.pytesseract.tesseract_cmd = os.getenv("tesseract_path")
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_pdf(file_stream: io.BytesIO) -> str:
    reader = PyPDF2.PdfReader(file_stream)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    logging.debug("Extracted text %s", text[:100])
    return text

def extract_text_from_image(file_stream: io.BytesIO) -> str:
    try:
        logging.debug("File stream contents (first 100 bytes): %s", file_stream.read(100))
        image = Image.open(file_stream)
        text = pytesseract.image_to_string(image)
        logging.debug("Extracted text %s", text[:100])
        return text
    except IOError as e:
        logging.error("Error opening image: %s", str(e))
        raise ValueError(f"Error opening image: {str(e)}")



async def process_file(file_contents: bytes, content_type: str, custom_prompt: str, task_id: str):
    logging.info("Processing Task : %s",task_id)
    try:
        file_stream = io.BytesIO(file_contents)
        logging.info("Processing File of Size : %s bytes",len(file_contents))
        # Extract text based on file type
        if content_type == "application/pdf":
            text = extract_text_from_pdf(file_stream)
        elif content_type in ["image/jpeg", "image/png"]:
            text = extract_text_from_image(file_stream)
        else:
            raise ValueError("Unsupported file type")

        logging.info("Extracted text from file: %s", text[:100])  # Log the first 100 characters of the extracted text

        # Convert text to English if necessary
        # convert_prompt = f"Translate the following text to English:\n{text}"
        # if model_type == "ollama":
        #     translated_text = await call_local_ollama_model(convert_prompt, text)  # Use Ollama for translation
        # elif model_type == "azure":
        #     translated_text = await run_openai_api(convert_prompt, text)  # Use Azure OpenAI for translation
        translated_text = text
        logging.debug("Translated text: %s", translated_text[:100])  # Log the first 100 characters of the translated text

        # Identify the document type
        identify_prompt = "Identify the type of document based on the following text:\n"
        if model_type == "ollama":
            document_type_response = await call_local_ollama_model(identify_prompt, translated_text)
        elif model_type == "azure":
            document_type_response = await run_openai_api(identify_prompt, translated_text)

        document_type = document_type_response.strip().lower()  # Normalize the document type
        logging.info("Identified document type: %s", document_type)  # Log the identified document type

        # Extract details based on identified document type
        try:
            document_type_lower = document_type.strip().lower()  # Normalize the document type
            if "resume" in document_type_lower:
                json_prompt = f"Extract the following information from the resume text and return it in JSON format and only json with no explanation :\n{text}\n\nJSON Schema:\n{resume_schema}"
                if model_type == "ollama":
                    json_response = await call_local_ollama_model(json_prompt, translated_text)
                elif model_type == "azure":
                    json_response = await run_openai_api(json_prompt, translated_text)
                main.task_results[task_id]["result"] = json_response

            elif "invoice" in document_type_lower:
                json_prompt = f"Extract the following information from the invoice text and return it in JSON format:\n{text}\n\nJSON Schema:\n{invoice_schema}"
                if model_type == "ollama":
                    json_response = await call_local_ollama_model(json_prompt, translated_text)
                elif model_type == "azure":
                    json_response = await run_openai_api(json_prompt, translated_text)
                main.task_results[task_id]["result"] = json_response

            elif "receipt" in document_type_lower:
                json_prompt = f"Extract the following information from the receipt text and return it in JSON format:\n{text}\n\nJSON Schema:\n{receipt_schema}"
                if model_type == "ollama":
                    json_response = await call_local_ollama_model(json_prompt, translated_text)
                elif model_type == "azure":
                    json_response = await run_openai_api(json_prompt, translated_text)
                main.task_results[task_id]["result"] = json_response

            elif "report" in document_type_lower:
                json_prompt = f"Extract the following information from the report text and return it in JSON format:\n{text}\n\nJSON Schema:\n{report_schema}"
                if model_type == "ollama":
                    json_response = await call_local_ollama_model(json_prompt, translated_text)
                elif model_type == "azure":
                    json_response = await run_openai_api(json_prompt, translated_text)
                main.task_results[task_id]["result"] = json_response

            elif "passport" in document_type_lower:
                json_prompt = f"Extract the following information from the passport text and return it in JSON format:\n{text}\n\nJSON Schema:\n{passport_schema}"
                if model_type == "ollama":
                    json_response = await call_local_ollama_model(json_prompt, translated_text)
                elif model_type == "azure":
                    json_response = await run_openai_api(json_prompt, translated_text)
                main.task_results[task_id]["result"] = json_response

            elif "driver license" in document_type_lower or "driving license" in document_type_lower:
                json_prompt = f"Extract the following information from the driver license text and return it in JSON format:\n{text}\n\nJSON Schema:\n{driver_license_schema}"
                if model_type == "ollama":
                    json_response = await call_local_ollama_model(json_prompt, translated_text)
                elif model_type == "azure":
                    json_response = await run_openai_api(json_prompt, translated_text)
                main.task_results[task_id]["result"] = json_response

            elif "national id" in document_type_lower:
                json_prompt = f"Extract the following information from the national ID text and return it in JSON format:\n{text}\n\nJSON Schema:\n{national_id_schema}"
                if model_type == "ollama":
                    json_response = await call_local_ollama_model(json_prompt, translated_text)
                elif model_type == "azure":
                    json_response = await run_openai_api(json_prompt, translated_text)
                main.task_results[task_id]["result"] = json_response

            elif "voter id" in document_type_lower:
                json_prompt = f"Extract the following information from the voter ID text and return it in JSON format:\n{text}\n\nJSON Schema:\n{voter_id_schema}"
                if model_type == "ollama":
                    json_response = await call_local_ollama_model(json_prompt, translated_text)
                elif model_type == "azure":
                    json_response = await run_openai_api(json_prompt, translated_text)
                main.task_results[task_id]["result"] = json_response

            elif "military id" in document_type_lower:
                json_prompt = f"Extract the following information from the military ID text and return it in JSON format:\n{text}\n\nJSON Schema:\n{military_id_schema}"
                if model_type == "ollama":
                    json_response = await call_local_ollama_model(json_prompt, translated_text)
                elif model_type == "azure":
                    json_response = await run_openai_api(json_prompt, translated_text)
                main.task_results[task_id]["result"] = json_response

            elif "green card" in document_type_lower:
                json_prompt = f"Extract the following information from the green card text and return it in JSON format:\n{text}\n\nJSON Schema:\n{green_card_schema}"
                if model_type == "ollama":
                    json_response = await call_local_ollama_model(json_prompt, translated_text)
                elif model_type == "azure":
                    json_response = await run_openai_api(json_prompt, translated_text)
                main.task_results[task_id]["result"] = json_response

            else:
                # If no schema is available for the identified document type
                main.task_results[task_id]["result"] = {"message": "Document type not supported. "+document_type_lower}
                logging.warning("Document type '%s' is not supported.", document_type_lower)  # Log warning for unsupported types

        except ValidationError as e:
            # Handle the case where the text does not match the expected schema
            main.task_results[task_id]["status"] = "failed"
            main.task_results[task_id]["result"] = str(e)
            logging.error("Validation error: %s %s", str(e), traceback.format_exc())  # Log the validation error

        # Update the task status
        main.task_results[task_id]["status"] = "completed"
    except Exception as e:
        main.task_results[task_id]["status"] = "failed"
        main.task_results[task_id]["result"] = str(e)
        logging.error("An error occurred: %s %s", str(e),traceback.format_exc())  # Log the error

async def call_local_ollama_model(prompt: str, text: str) -> str:
    ollama_url = "http://localhost:11434/api/generate"  # Update with your actual Ollama endpoint
    payload = {
        "model": "llama3.2",  # Specify the model name
        "prompt": f"{prompt}\n\n{text}",  # Combine the prompt and extracted text
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
            logging.error("Error calling local Ollama model: %s", traceback.format_exc())
            return f"Error calling local Ollama model: {e.response.text}"
        except Exception as e:
            logging.error("An error occurred:  %s", traceback.format_exc())
            return f"An error occurred: {str(e)}"

async def run_openai_api(prompt: str, text: str):
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(main.executor, lambda: openai.ChatCompletion.create(
        model="YOUR_GPT_MODEL_NAME",
        messages=[
            {"role": "user", "content": f"{prompt}\n\n{text}"}
        ]
    ))
    return response.choices[0].message['content']

