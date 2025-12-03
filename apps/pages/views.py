from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import WaitingListSerializer


def home(request):
    return render(request, "pages/index.html")


def api_docs(request):
    return render(request, "pages/api_docs.html")


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