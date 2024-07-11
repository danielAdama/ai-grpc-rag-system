import pathlib
import sys

current_dir = pathlib.Path(__file__).parent
previous_dir = current_dir.parent
sys.path.append(str(previous_dir))

import os
from concurrent import futures
import grpc
from pdf.services.pdf_service import PDFService
from google.protobuf.json_format import MessageToDict
import pdf_service_pb2
import pdf_service_pb2_grpc
from schemas.search_schemas import MatchAnyOrInterval
from config import BASE_DIR
from utils import _parse_filters, _handle_exception
import json

from config.logger import Logger
logger = Logger(__name__)


class PDFServiceServicer(pdf_service_pb2_grpc.PDFServiceServicer):
    def __init__(self):
        self.pdf_service = PDFService()
    def UploadPDF(self, request_iterator, context):
        try:
            collection_name = ""
            document_type = ""
            filename = ""

            for request in request_iterator:
                collection_name = request.collection_name
                document_type = request.document_type
                filename = request.filename

            if not filename:
                raise ValueError("Filename cannot be empty")
            filepath = str(BASE_DIR / "src" / "pdf" / "uploads" / filename)
            
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File {filename} does not exist in the uploads directory")

            result = self.pdf_service.embed_document(
                collection_name,
                filename,
                document_type
            )
            return pdf_service_pb2.UploadPDFResponse(message=result["message"])
        except ValueError as ve:
            logger.error(f"ValueError in UploadPDF: {str(ve)}")
            context.set_details(str(ve))
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return pdf_service_pb2.UploadPDFResponse()
        except FileNotFoundError as fnfe:
            logger.error(f"FileNotFoundError in UploadPDF: {str(fnfe)}")
            context.set_details(str(fnfe))
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return pdf_service_pb2.UploadPDFResponse()
        except Exception as ex:
            return _handle_exception("UploadPDF", context, ex)

    def Search(self, request, context):
        try:
            filters = _parse_filters(request.filters)
            if filters is None:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                return pdf_service_pb2.SearchResponse()
            result = self.pdf_service.search(query=request.query, filters=filters)
            return pdf_service_pb2.SearchResponse(search_result=json.dumps(result), message="Search completed")
        except Exception as ex:
            return _handle_exception("Search", context, ex)

    def Summarize(self, request, context):
        try:
            filters = _parse_filters(request.filters)
            if filters is None:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                return pdf_service_pb2.SearchResponse()
            summarized = self.pdf_service.summarize(query=request.query, filters=filters, user_id=request.user_id)
            return pdf_service_pb2.SummarizeResponse(summary=summarized, message="Summarization completed")
        except Exception as ex:
            return _handle_exception("Summarize", context, ex)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pdf_service_pb2_grpc.add_PDFServiceServicer_to_server(PDFServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info("Rag service started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()