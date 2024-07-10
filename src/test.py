###Sample questions
# "How does Active Inference minimize free energy?" paper_8.pdf
# "What is predictive coding?" paper_8.pdf

from schemas.search_schemas import MatchAnyOrInterval
from pdf.services.pdf_service import PDFService
import json

pdf = PDFService()
#Upload
# result = pdf.embed_document(
#     "pdf-articles",
#     "paper_8.pdf",
#     "artificial_intelligence_document"
# )
# print(result)

##Metadata need to be stored outside same as Document is, to enable search
filters = {
    "document_type": MatchAnyOrInterval(any=["artificial_intelligence_document"])
}
## Search
result = pdf.search(
    query="What is predictive coding?",
    filters=filters
)

ans = {"data":[json.dumps(doc.dict()) for doc in result["result"]]}
print(ans)

# #Summarize
# summarized = pdf.summarize(
#     query="What is predictive coding?",
#     user_id="danny@gmail.com" 
# )

# print(summarized["result"])