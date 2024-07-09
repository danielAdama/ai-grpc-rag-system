from pdf.services.pdf_service import PDFService

###Sample questions
# "How does Active Inference minimize free energy?" paper_8.pdf

# pdf = PDFService()
# result = pdf.embed_document(
#     "pdf-articles",
#     "paper_8.pdf",
#     "artificial_intelligence_document"
# )
# print(result)

pdf = PDFService()

result = pdf.search(
    query="How does Active Inference minimize free energy?"
)

print(result)