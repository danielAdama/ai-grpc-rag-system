from config.qdrant_client import QdrantVectorDB
from pdf.services.pdf_service import PDFService

pdf = PDFService()
vector_db = QdrantVectorDB(
    is_batch=True
)

documents = pdf.clean_text("pdf-articles")
result = vector_db.run(documents)
print(result)