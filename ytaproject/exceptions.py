from rest_framework.response import Response
from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    print(exc, context)
    response = exception_handler(exc, context)

    if response is not None:
        return response

    exc_list = str(exc).split("DETAIL: ")
    return Response({"error": exc_list[-1]}, status=403)
