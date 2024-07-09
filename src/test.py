from pdf.services.pdf_service import PDFService

pdf = PDFService()
###Sample questions
# "How does Active Inference minimize free energy?" paper_8.pdf
# "What is predictive coding?" paper_8.pdf

# pdf = PDFService()
# result = pdf.embed_document(
#     "pdf-articles",
#     "paper_8.pdf",
#     "artificial_intelligence_document"
# )
# print(result)

# result = pdf.search(
#     query="What is predictive coding?"
# )

# print(result)

# summarized = pdf.summarize(
#     query="What is predictive coding?",
#     user_id="danny@gmail.com"   
# )

# print(summarized["result"])