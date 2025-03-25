# Smart Email Orchestrator - Workflow Diagram

## 📊 Flowchart: Smart Email Orchestrator Workflow

```mermaid
flowchart TD
    A[User Uploads Email] --> B[Web Interface]
    B --> C[Web Server - Flask]
    C --> D[Process Email Content]
    
    subgraph Email_Processing
      D --> E[Extract Subject, Body, Attachments]
      E --> F[OCR for Image Text if any]
      F --> G[Classify Content using AI]
    end
    
    G --> H{Duplicate Email?}
    H --> |Yes| I[Skip or Flag Duplicate]
    H --> |No| J[Generate Output - JSON]
    
    J --> K[Store Data in Database]
    K --> L[Display Results to User]
    L --> M[User Downloads Output]
