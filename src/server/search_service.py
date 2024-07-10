import pathlib
import sys

current_dir = pathlib.Path(__file__).parent
previous_dir = current_dir.parent
sys.path.append(str(previous_dir))

from concurrent import futures
import grpc
import search_service_pb2
import search_service_pb2_grpc
from pdf.services.pdf_service import PDFService
from google.protobuf.json_format import MessageToDict
import json

from config.logger import Logger
logger = Logger(__name__)

class SearchService(search_service_pb2_grpc.SearchServiceServicer):
    def SearchDocuments(self, request, context):
        try:
            pdf = PDFService()
            result = pdf.search(request.query)
            doc_dict = [
                doc.dict() for doc in result["result"]
            ]
            response_dict = {"data": doc_dict}
            return search_service_pb2.SearchResponse(search_result=json.dumps(response_dict))
        except Exception as e:
            logger.error(f"Error in SearchDocuments: {str(e)}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.UNKNOWN)
            return search_service_pb2.SearchResponse()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    search_service_pb2_grpc.add_SearchServiceServicer_to_server(SearchService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info("Search service started on port 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()