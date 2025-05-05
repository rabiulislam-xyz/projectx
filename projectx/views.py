from django.shortcuts import redirect
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view()
@permission_classes((AllowAny,))
def home(request):
    # base_url = f"{request.scheme}://{request.get_host()}{request.path}"
    # doc_url = base_url + 'api/v1/docs/'
    # api_root_url = base_url + 'api/v1/'
    #
    # return Response(
    #     {
    #         "api_root": api_root_url,
    #         "docs": doc_url,
    #     },
    #     status=status.HTTP_200_OK)
    return redirect('/api/v1/docs/')


@api_view()
@permission_classes((AllowAny,))
def ping(request):

    return Response(
        {
            "status": "ok",
            "is_authenticated": request.user.is_authenticated,
            "timestamp": timezone.now().isoformat(),
        },
        status=status.HTTP_200_OK)
