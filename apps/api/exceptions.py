from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework.views import exception_handler


def handler(exc, context):
    if isinstance(exc, IntegrityError):
        return Response({"detail": "Violação de integridade da base de dados."}, status=409)
    if isinstance(exc, PermissionError):
        return Response({"detail": str(exc)}, status=403)
    return exception_handler(exc, context)
