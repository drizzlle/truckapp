from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import WaitingListSerializer


def home(request):
    return render(request, "pages/index.html")


def api_docs(request):
    return render(request, "pages/api_docs.html")


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def join_waiting_list(request):
    serializer = WaitingListSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Successfully joined the waiting list! We'll notify you when we launch."
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def handler403(request, exception):
    return render(request, 'errors/403.html', status=403)


def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)


def handler500(request):
    return render(request, 'errors/500.html', status=500)