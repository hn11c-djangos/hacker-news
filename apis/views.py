import re
from django.contrib.auth.models import User
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from news.models import Submission, Comment, Submission_ASK
from news.utils import calculate_score
from .serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from .utils import get_user_from_api_key

class Submission_APIView(APIView):

    @swagger_auto_schema(
        tags=['Submission'],
        operation_description="Get all submissions",
        responses={200: SubmissionSerializer(many=True),
                   400: "Invalid sort parameter"},
        manual_parameters=[openapi.Parameter('sort', openapi.IN_QUERY, description="Sort submissions by point or newest", type=openapi.TYPE_STRING)]
    )
    def get(self, request):
        sort = request.query_params.get('sort', 'point')
        from_domain = request.query_params.get('from', None)
        submissions = Submission.objects.all()

        if from_domain:
            domain_regex = re.compile(
                r'^(?:[a-zA-Z0-9]'  # First character of the domain
                r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)'  # Sub domain + hostname
                r'+[a-zA-Z]{2,6}\.?$'  # First level TLD
            )
            if not domain_regex.match(from_domain):
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Invalid domain parameter'})
            submissions = submissions.filter(domain=from_domain)

        if sort == 'point':
            submissions = sorted(submissions, key=lambda x: calculate_score(x), reverse=True)
        elif sort == 'newest':
            submissions = submissions.order_by('-created')
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Invalid sort parameter'})

        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

    def post(self, request):
        self.authentication_classes = [TokenAuthentication]
        serializer = SubmissionCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Comment_APIView(APIView):
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class SubmissionDetailView(APIView):
    def get(self, request, id):
        submission = get_object_or_404(Submission, id=id)
        serializer = SubmissionSerializer(submission)
        return Response(serializer.data)


class ThreadView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def get(self, request):
        comments = Comment.objects.filter(author=request.user,parent__isnull=True).order_by('-created_at')
        serializer = ThreadSerializer(comments, many=True)
        return Response(serializer.data)

class AskView(APIView):
    def get(self, request):
        asks = Submission_ASK.objects.all()
        serializer = SubmissionSerializer(asks, many=True)
        return Response(serializer.data)

class ProfileView(APIView):
    def get(self, request,id):
        profile = get_object_or_404(Profile, user_id=id)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

class UserSubmissions(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        submissions = Submission.objects.filter(author=user)
        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)