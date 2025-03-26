import json
import os
import re
import email
import hashlib
from email import policy
from email.parser import BytesParser
from email.header import decode_header
from app.utils.classification import classify_email, generate_intent_and_reasoning
from app.models import load_config
from app import app


CONFIG = load_config("config.json")
duplicateData = []

def getDupliactes():
    return duplicateData

def resetDupliactes():
    duplicateData.clear()
    return duplicateData

def extract_email_details(eml_file_path):
    """Extracts subject, body, and attachments from an .eml file."""
    with open(eml_file_path, "rb") as file:
        msg = BytesParser(policy=policy.default).parse(file)

    email_data = {
        "subject": msg["subject"],
        "body": get_email_body(msg),
        "attachments": extract_attachments(msg),
        "hash": generate_email_hash(msg)
    }

    return email_data

def get_email_body(msg):
    """Extract plain-text email body."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode(errors="ignore")
    return msg.get_payload(decode=True).decode(errors="ignore")

def extract_attachments(msg):
    attachments = []
    current_directory = os.getcwd()  # Get the current working directory
    attachment_folder = os.path.join(current_directory, app.config["UPLOAD_FOLDER"])

    # Create 'attc' folder if it doesn't exist
    os.makedirs(attachment_folder, exist_ok=True)
    
    for part in msg.walk():
        content_disposition = part.get("Content-Disposition")
        if content_disposition and "attachment" in content_disposition.lower():
            filename = part.get_filename()
            
            # Decode the filename if it is encoded
            if filename:
                decoded_filename = decode_header(filename)
                filename = "".join(
                    part.decode(encoding or "utf-8") if isinstance(part, bytes) else part
                    for part, encoding in decoded_filename
                )

                filepath = os.path.join(attachment_folder, filename)
                
                # Ensure unique filenames to avoid overwriting
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(filepath):
                    filepath = os.path.join(attachment_folder, f"{base}_{counter}{ext}")
                    counter += 1
                
                # Save the file
                try:
                    with open(filepath, "wb") as f:
                        f.write(part.get_payload(decode=True))
                    attachments.append(filepath)  # Store full file path for reference
                except Exception as e:
                    print(f"Error saving attachment {filename}: {e}")
    
    return attachments

def generate_email_hash(msg):
    email_content = f"{msg['subject']}{msg['from']}{msg['date']}{get_email_body(msg)}"
    return hashlib.md5(email_content.encode()).hexdigest()

def extract_fields(email_body):
    """Extract predefined fields dynamically from email body using regex."""
    extracted_data = {}
    fields = CONFIG["email_processing"]["extract_fields"]

    regex_patterns = {
    "amount": r"(?i)\b(?:amount|total):?\s?\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\b",
    "due_date": r"(?i)\b(?:due date|payment date):?\s?(\d{1,2}/\d{1,2}/\d{2,4})\b",
    "customer_id": r"(?i)\b(?:customer ID|account ID):?\s?(\w+)\b",
    "account_number": r"(?i)\b(?:account number|acc no):?\s?(\d+)\b",
    "loan_number": r"(?i)\b(?:loan number|loan ID):?\s?(\d+)\b",
    "disbursement_date": r"(?i)\b(?:disbursement date):?\s?(\d{1,2}/\d{1,2}/\d{2,4})\b",
    "old_address": r"(?i)\bold address:?\s?(.+)",
    "new_address": r"(?i)\bnew address:?\s?(.+)",
    "contact_number": r"(?i)\b(?:contact number|phone):?\s?(\d{10,15})\b",
    "old_contact_number": r"(?i)\bold contact number:?\s?(\d{10,15})\b",
    "new_contact_number": r"(?i)\bnew contact number:?\s?(\d{10,15})\b",
    "email": r"(?i)\b(?:email|email address):?\s?([\w.-]+@[\w.-]+)\b",
    "old_email": r"(?i)\bold email:?\s?([\w.-]+@[\w.-]+)\b",
    "new_email": r"(?i)\bnew email:?\s?([\w.-]+@[\w.-]+)\b",
    "name": r"(?i)\b(?:name|customer name):?\s?([A-Za-z .']+)\b",
    "branch": r"(?i)\bbranch:?\s?([A-Za-z0-9 &.-]+)\b",
    "Insurance": r"(?i)\b(?:insurance|insurance type):?\s?([A-Za-z ]+)\b",
    "Policy Number": r"(?i)\bpolicy number:?\s?(\w+)\b",
    "Claim Number": r"(?i)\bclaim number:?\s?(\w+)\b",
    "Claim Amount": r"(?i)\bclaim amount:?\s?\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\b",
    "Claim Type": r"(?i)\bclaim type:?\s?([A-Za-z ]+)\b",
    "Claim Date": r"(?i)\bclaim date:?\s?(\d{1,2}/\d{1,2}/\d{2,4})\b",
    "Claim Status": r"(?i)\bclaim status:?\s?([A-Za-z ]+)\b",
    "pending_amount": r"(?i)\bpending amount:?\s?\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\b",
    "pending_date": r"(?i)\bpending date:?\s?(\d{1,2}/\d{1,2}/\d{2,4})\b",
    "pending_status": r"(?i)\bpending status:?\s?([A-Za-z ]+)\b",
    "status": r"(?i)\bstatus:?\s?([A-Za-z ]+)\b",
    "transaction_id": r"(?i)\btransaction ID:?\s?(\w+)\b",
    "transaction_date": r"(?i)\btransaction date:?\s?(\d{1,2}/\d{1,2}/\d{2,4})\b",
    "transaction_amount": r"(?i)\btransaction amount:?\s?\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\b",
    "payment_reference_number": r"(?i)\bpayment reference number:?\s?(\w+)\b",
    "payment_date": r"(?i)\bpayment date:?\s?(\d{1,2}/\d{1,2}/\d{2,4})\b",
    "payment_status": r"(?i)\bpayment status:?\s?([A-Za-z ]+)\b",
    "payment_method": r"(?i)\bpayment method:?\s?([A-Za-z ]+)\b",
    "ifsc_code": r"(?i)\bIFSC code:?\s?([A-Z]{4}0[0-9A-Z]{6})\b",
    "swift_code": r"(?i)\bswift code:?\s?([A-Za-z0-9]+)\b",
    "bank_name": r"(?i)\bbank name:?\s?([A-Za-z0-9 &.-]+)\b",
    "bank_branch": r"(?i)\bbank branch:?\s?([A-Za-z0-9 &.-]+)\b",
    "bank_address": r"(?i)\bbank address:?\s?(.+)",
    "bank_account_number": r"(?i)\bbank account number:?\s?(\d+)\b",
    "bank_account_type": r"(?i)\bbank account type:?\s?([A-Za-z ]+)\b",
    "bank_account_holder_name": r"(?i)\bbank account holder name:?\s?([A-Za-z .']+)\b",
    "bank_account_holder_type": r"(?i)\bbank account holder type:?\s?([A-Za-z ]+)\b",
    "card_number": r"(?i)\bcard number:?\s?(\d{4} \d{4} \d{4} \d{4}|\d{16})\b",
    "emi_amount": r"(?i)\bEMI amount:?\s?\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\b",
    "emi_due_date": r"(?i)\bEMI due date:?\s?(\d{1,2}/\d{1,2}/\d{2,4})\b",
    "emi_status": r"(?i)\bEMI status:?\s?([A-Za-z ]+)\b",
    "interest_rate": r"(?i)\binterest rate:?\s?(\d+(?:\.\d+)?%)\b",
    "maturity_date": r"(?i)\bmaturity date:?\s?(\d{1,2}/\d{1,2}/\d{2,4})\b",
    "tenure": r"(?i)\btenure:?\s?(\d+ (?:months|years))\b",
    "total_outstanding": r"(?i)\btotal outstanding:?\s?\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\b",
    "available_balance": r"(?i)\bavailable balance:?\s?\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\b",
    "last_payment_date": r"(?i)\blast payment date:?\s?(\d{1,2}/\d{1,2}/\d{2,4})\b",
    "last_payment_amount": r"(?i)\blast payment amount:?\s?\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\b",
    "statement_period": r"(?i)\bstatement period:?\s?([A-Za-z0-9/ -]+)\b",
    "relationship_number": r"(?i)\brelationship number:?\s?(\w+)\b",
    "credit_score": r"(?i)\bcredit score:?\s?(\d{3})\b",
    "credit_limit": r"(?i)\bcredit limit:?\s?\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\b",
    "investment_folio_number": r"(?i)\binvestment folio number:?\s?(\w+)\b",
    "investment_scheme_name": r"(?i)\binvestment scheme name:?\s?([A-Za-z0-9 &.-]+)\b",
    "investment_amount": r"(?i)\binvestment amount:?\s?\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\b",
    "investment_date": r"(?i)\binvestment date:?\s?(\d{1,2}/\d{1,2}/\d{2,4})\b",
    "nominee_name": r"(?i)\bnominee name:?\s?([A-Za-z .']+)\b",
    "nominee_relationship": r"(?i)\bnominee relationship:?\s?([A-Za-z ]+)\b",
    "escalation_contact": r"(?i)\bescalation contact:?\s?(\d{10,15})\b"
    }

    for field in fields:
        pattern = regex_patterns.get(field)
        if pattern:
            match = re.search(pattern, email_body)
            if match:
                extracted_data[field] = match.group(1)

    return extracted_data

def process_emails(upload_folder, config):
    """Processes uploaded .eml files."""
    results = []
    seen_hashes = set()
    
    for filename in os.listdir(upload_folder):
        if filename.endswith(".eml"):
            
            eml_path = os.path.join(upload_folder, filename)
            email_data = extract_email_details(eml_path)

            if email_data["hash"] in seen_hashes:
                print(f"Duplicate email detected: {filename}")
                duplicateData.append(os.path.basename(filename))
                continue  # Skip duplicate emails
            
            seen_hashes.add(email_data["hash"])
            classification = classify_email(email_data,upload_folder)
            #classification = advanced_classify_email(email_data)
            try:
                extracted_fields = extract_fields(email_data["body"])
            except Exception as e:
                print(f"Error extracting fields from email body: {e}")
                extracted_fields = {}
            sender_intent, reasoning = generate_intent_and_reasoning(email_data["body"])
            
# Handle list of attachments
            attachment_filenames = [os.path.basename(attachment) for attachment in email_data["attachments"]]
            result = {
               "file": filename, "subject": email_data["subject"],
                "request_type": classification["request_type"], "sub_request_type": classification["sub_request_type"],
                "confidence_score": classification["confidence_score"], "attachments": attachment_filenames,
                "senders_intent": sender_intent, "department": classification["department"],"reasoning": reasoning,
                **extracted_fields
            }

            results.append(result)

    with open(config["OUTPUT_FILE"], "w") as file:
        json.dump(results, file, indent=2)

    return results

