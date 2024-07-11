# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import pdf_service_pb2 as pdf__service__pb2

GRPC_GENERATED_VERSION = '1.64.1'
GRPC_VERSION = grpc.__version__
EXPECTED_ERROR_RELEASE = '1.65.0'
SCHEDULED_RELEASE_DATE = 'June 25, 2024'
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    warnings.warn(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in pdf_service_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
        + f' This warning will become an error in {EXPECTED_ERROR_RELEASE},'
        + f' scheduled for release on {SCHEDULED_RELEASE_DATE}.',
        RuntimeWarning
    )


class PDFServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.UploadPDF = channel.stream_unary(
                '/pdfservice.PDFService/UploadPDF',
                request_serializer=pdf__service__pb2.UploadPDFRequest.SerializeToString,
                response_deserializer=pdf__service__pb2.UploadPDFResponse.FromString,
                _registered_method=True)
        self.Search = channel.unary_unary(
                '/pdfservice.PDFService/Search',
                request_serializer=pdf__service__pb2.SearchRequest.SerializeToString,
                response_deserializer=pdf__service__pb2.SearchResponse.FromString,
                _registered_method=True)
        self.Summarize = channel.unary_unary(
                '/pdfservice.PDFService/Summarize',
                request_serializer=pdf__service__pb2.SummarizeRequest.SerializeToString,
                response_deserializer=pdf__service__pb2.SummarizeResponse.FromString,
                _registered_method=True)


class PDFServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def UploadPDF(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Search(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Summarize(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_PDFServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'UploadPDF': grpc.stream_unary_rpc_method_handler(
                    servicer.UploadPDF,
                    request_deserializer=pdf__service__pb2.UploadPDFRequest.FromString,
                    response_serializer=pdf__service__pb2.UploadPDFResponse.SerializeToString,
            ),
            'Search': grpc.unary_unary_rpc_method_handler(
                    servicer.Search,
                    request_deserializer=pdf__service__pb2.SearchRequest.FromString,
                    response_serializer=pdf__service__pb2.SearchResponse.SerializeToString,
            ),
            'Summarize': grpc.unary_unary_rpc_method_handler(
                    servicer.Summarize,
                    request_deserializer=pdf__service__pb2.SummarizeRequest.FromString,
                    response_serializer=pdf__service__pb2.SummarizeResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pdfservice.PDFService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pdfservice.PDFService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class PDFService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def UploadPDF(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_unary(
            request_iterator,
            target,
            '/pdfservice.PDFService/UploadPDF',
            pdf__service__pb2.UploadPDFRequest.SerializeToString,
            pdf__service__pb2.UploadPDFResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Search(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/pdfservice.PDFService/Search',
            pdf__service__pb2.SearchRequest.SerializeToString,
            pdf__service__pb2.SearchResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Summarize(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/pdfservice.PDFService/Summarize',
            pdf__service__pb2.SummarizeRequest.SerializeToString,
            pdf__service__pb2.SummarizeResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)