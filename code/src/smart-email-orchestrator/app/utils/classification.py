import openai
from transformers import pipeline
from app.models import load_config
from app.utils.ocr import extract_text_from_image
import os
import PyPDF2
import docx

CONFIG = load_config("config.json")


# Initialize the text classification pipeline with a more advanced model
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def extract_text_from_attachment(file_path):
    try:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                return " ".join(page.extract_text() for page in reader.pages if page.extract_text())
        elif ext == ".docx":
            doc = docx.Document(file_path)
            return " ".join(para.text for para in doc.paragraphs)
        elif ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
    return ""
    


def classify_email(email_data, UPLOAD_FOLDER):
    """Classifies emails based on request types using a language model."""
    detected_request_type = None
    detected_sub_request_type = None
    confidence_score = 0
    detected_department = None

    content_sources = [email_data["body"]]
    for attachment in email_data["attachments"]:
        attachment_path = os.path.join(UPLOAD_FOLDER, attachment["file_name"])
        content_sources.append(extract_text_from_attachment(attachment_path))
    
    candidate_labels = [req["request_type"] for req in CONFIG["request_types"]]
    if not candidate_labels:
        return {"request_type": "Unknown", "sub_request_type": "Unknown", "confidence_score": 0, "department": "Unknown"}

    for content in content_sources:
        if content:
            result = classifier(content, candidate_labels)
            detected_request_type = result["labels"][0]
            confidence_score = result["scores"][0] * 100

            for req in CONFIG["request_types"]:
                if req["request_type"] == detected_request_type:
                    detected_department = req["department"]
                    if req["sub_request_types"]:
                        sub_result = classifier(content, req["sub_request_types"])
                        detected_sub_request_type = sub_result["labels"][0]
                        confidence_score += sub_result["scores"][0] * 30
                    break

    return {
        "request_type": detected_request_type,
        "sub_request_type": detected_sub_request_type,
        "confidence_score": min(confidence_score, 100),
        "department": detected_department
    }


def generate_intent_and_reasoning(email_body):
    if not email_body:
        return "Unknown", "Insufficient information to determine intent."
    intent_labels = ["Inquiry", "Complaint", "Request", "Follow-up", "Acknowledgment"]
    result = classifier(email_body, intent_labels)
    print(result)
    return result["labels"][0], f"The email is classified as '{result['labels'][0]}' because it discusses {result['labels'][0].lower()} matters."