# DocumentIntelligence

# FastAPI File Upload and Text Extraction

This project is a FastAPI application that allows users to upload PDF or image files and extract text from them. It can optionally process the extracted text with a custom prompt using either Azure OpenAI or a local Ollama model.

## Features

- Upload PDF or image files.
- Extract text from uploaded files.
- Optionally process the extracted text with a custom prompt.
- Supports both Azure OpenAI and local Ollama model.

## Requirements

- Python 3.7 or higher
- FastAPI
- Uvicorn
- python-multipart
- openai
- PyPDF2
- Pillow
- pytesseract
- httpx

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the project root and add your configuration:

   ```plaintext
   AZURE_OPENAI_API_TYPE=azure
   AZURE_OPENAI_API_BASE=YOUR_AZURE_OPENAI_ENDPOINT
   AZURE_OPENAI_API_KEY=YOUR_AZURE_OPENAI_API_KEY
   AZURE_OPENAI_API_VERSION=2023-05-15
   MODEL_TYPE=azure  # Change to 'ollama' for local Ollama model
   ```

6. Install Tesseract OCR on your system and add it to your PATH. Follow the instructions [here](https://github.com/UB-Mannheim/tesseract/wiki) for Windows installation.

## Usage

1. Run the FastAPI application:

   ```bash
   uvicorn main:app --reload
   ```

2. Access the API documentation at `http://127.0.0.1:8000/docs` to test the endpoints.

3. To upload a file and optionally provide a custom prompt, use the `/upload/` endpoint. You can use tools like Postman or cURL to send a POST request:

   - **Example cURL command**:
     ```bash
     curl -X POST "http://127.0.0.1:8000/upload/" -F "file=@path/to/your/file.pdf" -F "custom_prompt=Your custom prompt here"
     ```

## Logging

The application includes logging to help debug issues. Logs will be printed to the console, showing received files, custom prompts, and any errors encountered.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License. See the LICENSE file for details.