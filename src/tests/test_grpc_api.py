import pytest
import grpc
import pathlib
import sys

current_dir = pathlib.Path(__file__).parent.parent
previous_dir = current_dir.parent
sys.path.append(str(previous_dir))

from src.server.pdf_service_pb2 import UploadPDFRequest, UploadPDFResponse, SearchRequest, SearchResponse, SummarizeRequest, SummarizeResponse
from src.server import  pdf_service_pb2_grpc

# from pdf.services.pdf_service import PDFService
# from src.server.pdf_service import PDFServiceServicer
# from src.server.pdf_service_pb2 import UploadPDFRequest, UploadPDFResponse, SearchRequest, SearchResponse, SummarizeRequest, SummarizeResponse

from config.logger import Logger
logger = Logger(__name__)


@pytest.fixture(scope="module")
def grpc_add_to_server():
    from src.server.pdf_service_pb2 import add_PDFServiceServicer_to_server

    return add_PDFServiceServicer_to_server

@pytest.fixture(scope="module")
def grpc_servicer():
    from src.server import PDFServiceServicer

    return PDFServiceServicer()

@pytest.fixture(scope="module")
def grpc_stub(self, grpc_channel):
    from src.server.pdf_service_pb2_grpc import PDFServiceStub

    stub = PDFServiceStub(grpc_channel)
    return stub

@pytest.fixture(scope="module")
def grpc_channel():
    channel = grpc.insecure_channel('localhost:50051')
    yield channel
    channel.close()

    # def test_upload_pdf(self, grpc_stub):
    #     filename="paper_8.pdf"
    #     request = UploadPDFRequest(
    #         collection_name="test_collection",
    #         document_type="artificial_intelligence_document",
    #         filename=filename
    #     )
    #     response = grpc_stub.UploadPDF(request)
    #     assert isinstance(response, UploadPDFResponse)
    #     assert response.message == f"{filename} embedded successfully"

    # def test_search(self, grpc_stub):
    #     request = SearchRequest(
    #         collection_name="test_collection",
    #         query="How does Active Inference minimize free energy?",
    #         filters="document_type:[artificial_intelligence_document]"
    #     )
    #     response = grpc_stub.Search(request)
    #     assert isinstance(response, SearchResponse)
    #     assert response.message == "Search completed"
    #     assert len(response.search_result) > 0

    # def test_summarize(self, grpc_stub):
    #     request = SummarizeRequest(
    #         collection_name="test_collection",
    #         query="How does Active Inference minimize free energy?",
    #         filters="document_type:[artificial_intelligence_document]"
    #     )
    #     response = grpc_stub.Summarize(request)
    #     assert isinstance(response, SummarizeResponse)
    #     assert response.message == "Summarization completed"
    #     assert len(response.summary) > 0

# if __name__ == "__main__":
#     pytest.main()
