from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .upload_ingest import ingest_uploaded_pdf


class UploadPdfApi(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            return Response(
                {"error": "No file uploaded."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not uploaded_file.name.lower().endswith(".pdf"):
            return Response(
                {"error": "Only PDF files are allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Run PDF processing pipeline
        chunks = ingest_uploaded_pdf(uploaded_file)

        return Response(
            {
                "filename": uploaded_file.name,
                "chunk_count": len(chunks),
                "preview": chunks[:2],  # return first 2 chunks for testing
            },
            status=status.HTTP_200_OK,
        )