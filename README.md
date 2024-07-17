# AI-GRPC-RAG-System Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Directory Structure](#directory-structure)
3. [Installation and Setup](#installation-and-setup)
4. [Running the Project](#running-the-project)
5. [Usage](#usage)
6. [GRPC Services](#grpc-services)
7. [Configuration](#configuration)
8. [Logging](#logging)
9. [Testing](#testing)

## Project Overview

The AI-GRPC-RAG-System is designed to provide functionalities such as uploading, searching, and summarizing PDF documents using a GRPC service. It is built using Python, GRPC, and other supporting libraries and frameworks.

## Directory Structure

```
.
├── Makefile
├── README.md
├── config
│   ├── __init__.py
│   ├── config_helper.py
│   ├── logger.py
│   └── qdrant_client.py
├── env_config
│   └── app_config.yml
├── gen_ai
│   ├── RAGLLM
│   │   ├── __init__.py
│   ├── __init__.py
│   └── prompt
│       └── templates
│           ├── system_template.txt
│           └── user_template.txt
├── pdf_service.proto
├── requirements.txt
├── src
│   ├── client
│   │   └── __init__.py
│   ├── pdf
│   │   ├── services
│   │   │   ├── __init__.py
│   │   │   └── pdf_service.py
│   │   └── uploads
│   │       ├── Education_in_Nigeria_A_Futuristic_Perspective.pdf
│   │       ├── Research_Paper_on_Artificial_Intelligence.pdf
│   │       └── paper_8.pdf
│   ├── proto
│   │   └── pdf_service.proto
│   ├── schemas
│   │   ├── __init__.py
│   │   └── search_schemas.py
│   ├── server
│   │   ├── __init__.py
│   │   ├── pdf_service.py
│   │   ├── pdf_service_pb2.py
│   │   └── pdf_service_pb2_grpc.py
│   └── utils
│       ├── __init__.py
└── summarization_service.proto
```

## Installation and Setup

### Prerequisites

- Python 3.7+
- GRPC tools
- virtualenv

### Steps

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/ai-grpc-rag-system.git
   cd ai-grpc-rag-system
   ```

2. Create a virtual environment:
   ```sh
   python3 -m venv aenv
   source aenv/bin/activate
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Generate GRPC code from protobuf files:
   ```sh
   python -m grpc_tools.protoc -I=src/proto --python_out=src/server --grpc_python_out=src/server src/proto/pdf_service.proto
   ```

## Running the Project

To start the GRPC server, run:

```sh
python src/server/pdf_service.py
```

This will start the server and it will listen on port `50051`.

## Usage

### Upload PDF
<img width="1680" alt="pdf upload" src="https://github.com/user-attachments/assets/b4f29236-fbf6-481f-989b-edf09ed179f2">

<img width="1680" alt="pdf upload 2" src="https://github.com/user-attachments/assets/0169228f-13c9-4ba9-bc0f-c6f3b3260714">

<img width="1680" alt="pdf upload 3" src="https://github.com/user-attachments/assets/cec3bff5-ab3c-4f9f-af7a-3f3ed98bb60e">

<img width="1680" alt="pdf upload 4" src="https://github.com/user-attachments/assets/16d76ede-1043-4ccc-a93f-6da44f488d65">

- Endpoint: `PDFService/UploadPDF`
- Content-Type: application/grpc

#### Request Body:
```json
{
    "collection_name": "pdf-articles",
    "document_type": "artificial_intelligence_document",
    "filename": "paper_8.pdf"
}
```

### Search
<img width="1680" alt="Search 1" src="https://github.com/user-attachments/assets/3d235020-ee69-44bc-8e7b-4c6beba3af81">

<img width="1680" alt="Search 2" src="https://github.com/user-attachments/assets/25e033cb-85d9-49fa-8c27-f2349ff690a1">

- Endpoint: `PDFService/Search`
- Content-Type: application/grpc

#### Request Body:
```json
{
    "query": "How does Active Inference minimize free energy?",
    "filters": "document_type:[artificial_intelligence_document]"
}
```

### Summarize
<img width="1680" alt="Summarized" src="https://github.com/user-attachments/assets/ac0d0241-9587-44f7-abde-d8df3bee586a">

- Endpoint: `PDFService/Summarize`
- Content-Type: application/grpc

#### Request Body:
```json
{
    "query": "How does Active Inference minimize free energy?",
    "filters": "document_type:[artificial_intelligence_document]",
    "user_id":"danny@gmail.com"
}
```

### CI/CD Pipeline
<img width="1680" alt="Screenshot 2024-07-17 at 14 58 34" src="https://github.com/user-attachments/assets/e36dc907-049c-403c-abc4-10f805c34e59">


## GRPC Services

### PDFService

#### UploadPDF

Uploads a PDF file by specifying its filename and associated metadata.

#### Search

Searches the PDF documents based on the provided query and filters.

#### Summarize

Summarizes the content of the PDF documents based on the provided query and filters.

## Configuration

Configuration files are located in the `env_config` directory.

- `app_config.yml`: Contains environment-specific configurations.

## Logging

Logging configuration is defined in `config/logger.py`. The logger is used to log information, warnings, errors, and other runtime details.

## Testing

To run tests, use the `test.py` file located in the `src` directory.
