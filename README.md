# AI gRPC RAG System

A gRPC service for working with PDF documents: upload them, search them in natural language and get LLM-written summaries. Documents are chunked and embedded into Qdrant, and a CI/CD pipeline builds and ships the container.

![Search results](https://github.com/user-attachments/assets/3d235020-ee69-44bc-8e7b-4c6beba3af81)

## Features

- **UploadPDF:** ingest a PDF with metadata (collection and document type), then chunk and embed it.
- **Search:** semantic search across documents, with metadata filters.
- **Summarize:** an LLM-written summary of the passages that answer a query.

## Built with

Python · gRPC · Protocol Buffers · Qdrant · LLMs · Docker · GitHub Actions

## Getting started

### Prerequisites

- Python 3.10+
- A running Qdrant instance (local or cloud)
- Docker (optional)

### 1. Clone and install

```bash
git clone https://github.com/danielAdama/ai-grpc-rag-system.git
cd ai-grpc-rag-system

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Generate the gRPC code

```bash
python -m grpc_tools.protoc -I=src/proto \
  --python_out=src/server --grpc_python_out=src/server \
  src/proto/pdf_service.proto
```

### 3. Configure

Settings, including the Qdrant connection, live in `env_config/app_config.yml`.

### 4. Run the server

```bash
python src/server/pdf_service.py
```

The server listens on port `50051`.

### Or run with Docker

```bash
docker build -t ai-grpc-rag-system .
docker run -p 50051:50051 ai-grpc-rag-system
```

## Usage

All calls are on `PDFService` with `Content-Type: application/grpc`. The screenshots below show each call made from a gRPC client.

### UploadPDF

Uploads a PDF by filename, with metadata used later for filtering.

```json
{
  "collection_name": "pdf-articles",
  "document_type": "artificial_intelligence_document",
  "filename": "paper_8.pdf"
}
```

![Upload request](https://github.com/user-attachments/assets/b4f29236-fbf6-481f-989b-edf09ed179f2)

<details>
<summary>More upload screenshots</summary>

![Upload 2](https://github.com/user-attachments/assets/0169228f-13c9-4ba9-bc0f-c6f3b3260714)
![Upload 3](https://github.com/user-attachments/assets/cec3bff5-ab3c-4f9f-af7a-3f3ed98bb60e)
![Upload 4](https://github.com/user-attachments/assets/16d76ede-1043-4ccc-a93f-6da44f488d65)

</details>

### Search

Finds the most relevant passages for a question, filtered by document type.

```json
{
  "query": "How does Active Inference minimize free energy?",
  "filters": "document_type:[artificial_intelligence_document]"
}
```

![Search results](https://github.com/user-attachments/assets/25e033cb-85d9-49fa-8c27-f2349ff690a1)

### Summarize

Answers the question with a summary of the matching passages.

```json
{
  "query": "How does Active Inference minimize free energy?",
  "filters": "document_type:[artificial_intelligence_document]",
  "user_id": "user@example.com"
}
```

![Summary](https://github.com/user-attachments/assets/ac0d0241-9587-44f7-abde-d8df3bee586a)

## CI/CD

A GitHub Actions workflow builds and ships the service. See `.github/workflows/`.

![CI/CD pipeline](https://github.com/user-attachments/assets/e36dc907-049c-403c-abc4-10f805c34e59)

## Project structure

```
ai-grpc-rag-system/
├── .github/workflows/     # CI/CD pipeline
├── config/                # Config helper, logger, Qdrant client
├── env_config/            # app_config.yml
├── gen_ai/
│   ├── RAGLLM/            # Retrieval and LLM logic
│   └── prompt/templates/  # System and user prompt templates
├── src/
│   ├── proto/             # pdf_service.proto
│   ├── server/            # gRPC server and generated code
│   ├── client/            # Client
│   ├── pdf/               # PDF services and sample uploads
│   ├── schemas/           # Search schemas
│   └── utils/
├── Dockerfile
├── Makefile
└── requirements.txt
```

## Logging

Logging is configured in `config/logger.py` and records information, warnings and errors at runtime.

## Testing

```bash
python src/test.py
```

## Contact

Daniel Enemona Adama · [adamadaniel321@gmail.com](mailto:adamadaniel321@gmail.com) · [Portfolio](https://daniel-adama.vercel.app)
