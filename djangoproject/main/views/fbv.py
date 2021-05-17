
from django.http import JsonResponse,HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from main.serializers import CommentSerializer
from main.models import Comment


@api_view(['GET', 'POST'])
def comment_replies(request, pk1, pk2):
    try:
        comment = Comment.objects.get(id=pk2)
    except Comment.DoesNotExist as e:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        replies = comment.replies
        serializer = CommentSerializer(replies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    if request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user, directed_to_id=pk2, post_id=pk1)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
