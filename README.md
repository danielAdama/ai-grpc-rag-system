# AI gRPC RAG System

A gRPC service for working with PDF documents: upload them, search them in natural language and get summaries. Documents are embedded into Qdrant, answers come from an LLM, and results are cached in Redis. A CI/CD pipeline builds and ships the container.

![Search](docs/screenshots/search-1.png)

## Features

- **UploadPDF:** ingest a PDF with metadata (collection and document type), then chunk and embed it.
- **Search:** semantic search across documents, with metadata filters.
- **Summarize:** an LLM-written summary of the passages that answer a query.

## Built with

Python · gRPC · Qdrant · Redis · Groq · Docker · GitHub Actions

## Getting started

### Prerequisites

- Python 3.10+
- `grpcio-tools`
- A running Qdrant instance and Redis (or Docker)

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

Settings live in `env_config/app_config.yml`.

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

All calls are on `PDFService` with `Content-Type: application/grpc`.

### UploadPDF

```json
{
  "collection_name": "pdf-articles",
  "document_type": "artificial_intelligence_document",
  "filename": "paper_8.pdf"
}
```

![Upload](docs/screenshots/upload-1.png)

### Search

```json
{
  "query": "How does Active Inference minimize free energy?",
  "filters": "document_type:[artificial_intelligence_document]"
}
```

### Summarize

```json
{
  "query": "How does Active Inference minimize free energy?",
  "filters": "document_type:[artificial_intelligence_document]",
  "user_id": "user@example.com"
}
```

![Summarize](docs/screenshots/summarize-1.png)

## CI/CD

GitHub Actions builds and deploys the service on every push to `main`. See `.github/workflows/`.

![CI/CD pipeline](docs/screenshots/cicd.png)

## Project structure

```
ai-grpc-rag-system/
├── config/            # Config helpers, logger, Qdrant client
├── env_config/        # app_config.yml
├── gen_ai/            # RAG + LLM logic and prompt templates
├── src/
│   ├── proto/         # pdf_service.proto
│   ├── server/        # gRPC server and generated code
│   ├── client/        # Example client
│   ├── pdf/           # PDF services and sample uploads
│   ├── schemas/       # Request/response schemas
│   └── utils/
├── Dockerfile
├── Makefile
└── requirements.txt
```

## Logging

Logging is configured in `config/logger.py`.

## Testing

```bash
python src/test.py
```

## Contact

Daniel Enemona Adama · adamadaniel321@gmail.com · [Portfolio](https://daniel-adama.vercel.app)
