import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, message="Support for class-based `config` is deprecated")

import pytest
from concurrent import futures
from unittest.mock import patch, MagicMock
import pathlib
import sys

current_dir = pathlib.Path(__file__).parent.parent
previous_dir = current_dir.parent
sys.path.append(str(previous_dir))

from src.server.pdf_service_pb2 import (
    UploadPDFRequest, 
    UploadPDFResponse, 
    SearchRequest, 
    SearchResponse,
    SummarizeRequest, 
    SummarizeResponse
)
from src.server.pdf_service import PDFServiceServicer
from pdf.services.pdf_service import PDFService
from src.server import pdf_service_pb2, pdf_service_pb2_grpc
from grpc import StatusCode, RpcError

from config.logger import Logger
logger = Logger(__name__)

class TestPDFServiceServicer:
    def setup_method(self):
        self.pdf_service_servicer = PDFServiceServicer()

    @patch.object(PDFService, 'embed_document', return_value={"message": "test.pdf embedded successfully"})
    def test_upload_pdf_success(self, mock_embed_document):
        request = UploadPDFRequest(
            collection_name="test_collection",
            document_type="test_document",
            filename="test.pdf"
        )
        response = self.pdf_service_servicer.UploadPDF(iter([request]), None)
        assert response.message == "test.pdf embedded successfully"

    @patch("pdf.services.pdf_service.os.path.exists", return_value=False)
    def test_upload_pdf_file_not_found(self, mock_exists):
        request = UploadPDFRequest(
            collection_name="test_collection",
            document_type="test_document",
            filename="non_existent_file.pdf"
        )
        context = MagicMock()
        response = self.pdf_service_servicer.UploadPDF(iter([request]), context)
        assert context.set_code.call_args[0][0] == StatusCode.NOT_FOUND
        assert "File non_existent_file.pdf does not exist in the uploads directory" in context.set_details.call_args[0][0]

    @patch.object(PDFService, 'search', return_value={"data": ["Test search result"]})
    def test_search_success(self, mock_search):
        request = SearchRequest(query="test_query", filters="document_type:[artificial_intelligence_document]")
        context = MagicMock()
        response = self.pdf_service_servicer.Search(request, context)
        assert response.message == "Search completed"
        assert response.search_result == '{"data": ["Test search result"]}'

    @patch("pdf.services.pdf_service.vector_db.search", side_effect=RpcError("Test RPC error"))
    def test_search_rpc_error(self, mock_search):
        request = SearchRequest(query="test_query", filters="document_type:[artificial_intelligence_document]")
        context = MagicMock()
        response = self.pdf_service_servicer.Search(request, context)
        assert context.set_code.call_args[0][0] == StatusCode.UNKNOWN
        assert "Test RPC error" in context.set_details.call_args[0][0]

    @patch.object(PDFService, 'summarize', return_value="Test summary")
    def test_summarize_success(self, mock_summarize):
        request = SummarizeRequest(query="test_query", filters="document_type:[artificial_intelligence_document]", user_id="test-user")
        context = MagicMock()
        response = self.pdf_service_servicer.Summarize(request, context)
        assert response.message == "Summarization completed"
        assert response.summary == "Test summary"

    @patch("pdf.services.pdf_service.vector_db.search", side_effect=RpcError("Test RPC error"))
    def test_summarize_rpc_error(self, mock_search):
        request = SummarizeRequest(query="test_query", filters="document_type:[artificial_intelligence_document]", user_id="test-user")
        context = MagicMock()
        response = self.pdf_service_servicer.Summarize(request, context)
        assert context.set_code.call_args[0][0] == StatusCode.UNKNOWN
        assert "Test RPC error" in context.set_details.call_args[0][0]