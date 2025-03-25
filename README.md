# 🚀 SMART EMAIL Orchestrator

## 📌 Table of Contents
- [Introduction](#introduction)
- [Demo](#demo)
- [Inspiration](#inspiration)
- [What It Does](#what-it-does)
- [How We Built It](#how-we-built-it)
- [Challenges We Faced](#challenges-we-faced)
- [How to Run](#how-to-run)
- [Tech Stack](#tech-stack)
- [Team](#team)

---

## 🎯 Introduction

The Smart Email Orchestrator is a web-based system that automates the classification of emails using AI techniques. It extracts email content, performs text classification, and applies OCR for image attachments. This document outlines the architecture, data flow, and design considerations.
The system also handles complex email scenarios, including:
- Multi-request Emails with Primary Intent Detection: Identifies and processes emails containing multiple requests while determining the sender's main intent.
- Duplicate Email Detection: Recognizes duplicate emails from multiple replies or forwards within the same thread to reduce redundancy.
- Priority-based Extraction: Prioritizes extraction rules to ensure critical information is processed first, such as extracting numerical fields from attachments.

## 🎥 Demo
🔗 [Live Demo](#) (if applicable)  
📹 [Video Demo](#) (if applicable)  
🖼️ Screenshots:

![Screenshot 1](link-to-image)

## 💡 Inspiration
- Automate the extraction and classification of email content.
- Use a zero-shot AI model for flexible and accurate categorization.
- Extract text from image attachments via OCR.
- Provide a user-friendly web interface for uploading, classifying, and downloading results.

## ⚙️ What It Does

- Email Extraction: Parse .eml files to extract subject, body, and attachments.
- AI-based Classification: Classify emails into predefined categories using the facebook/bart-large-mnli model.
- Optical Character Recognition (OCR): Extract text from images in email attachments.
- User Interface: A web interface for email upload, result viewing, and data download.

## 🛠️ How We Built It

1. **Web Interface (Frontend)**
   - Technologies: HTML, CSS (Bootstrap), JavaScript (DataTables)
   - Functions: 
     - Upload .eml files.
     - Display classification results.
     - Provide options to download structured output (JSON).

2. **Web Server (Backend)**
   - Framework: Flask (Python)
   - Functions: 
     - Handle HTTP requests (upload, process, display results).
     - Route endpoints for data operations.
     - Manage application state and configurations.

3. **Email Processor**
   - Components: 
     - `email_extraction.py`: Parses .eml content (subject, body, attachments).
     - `ocr.py`: Extracts text from image attachments.

4. **AI Classifier**
   - Model: facebook/bart-large-mnli (Zero-shot classification via Hugging Face Transformers)
   - Function: 
     - Classifies extracted email content.
     - Uses `config.json` for categories and subcategories.
     - Handles multi-intent emails by detecting and prioritizing the primary intent for accurate routing.
     - Identifies duplicate emails within a conversation thread to prevent redundant processing.

### Example Initialization:
```python
from transformers import pipeline
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
```

### Multi-Intent Handling Strategy:
- Extracts and analyzes multiple intents within a single email.
- Applies a scoring mechanism to prioritize and route based on the primary intent.
- Logs secondary intents for future reference or manual review.

5. **Data Handler**
   - Libraries: pandas, numpy
   - Function: 
     - Analyze, structure, and store classified data.
     - Output results as `output.json`.

## 🏃 How to Run

1. Clone the repository: 
   ```bash
   git clone https://github.com/yourusername/smart-email-orchestrator.git
   ```
2. Navigate to the project directory:
   ```bash
   cd smart-email-orchestrator
   ```
3. Install dependencies: 
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application: 
   ```bash
   python app/main.py
   ```
5. Access the app: 
   ```bash
   http://localhost:5000
   ```

## 🏗️ Tech Stack
- 🔹 Frontend: HTML, CSS (Bootstrap), JavaScript (DataTables)
- 🔹 Backend: Flask (Python)
- 🔹 AI Model: facebook/bart-large-mnli (Zero-shot classification via Hugging Face Transformers)
- 🔹 Other: pandas, numpy

## 👥 Team
- **Your Name** - [GitHub](#) | [LinkedIn](#)
- **Teammate 2** - [GitHub](#) | [LinkedIn](#)