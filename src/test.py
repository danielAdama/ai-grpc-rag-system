from config.qdrant_client import vector_db
from pdf.services.pdf_service import PDFService

pdf = PDFService()

document = pdf.clean_text("test")
vector_db.run(document)

