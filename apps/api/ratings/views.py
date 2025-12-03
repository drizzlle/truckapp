from rest_framework import generics, permissions, views, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from apps.ratings.models import Rating
from apps.jobs.models import Job
from django.contrib.auth import get_user_model
from .serializers import RatingSerializer, RatingCreateSerializer

User = get_user_model()

class RateUserView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RatingCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        job_id = serializer.validated_data.pop('job_id')
        job = get_object_or_404(Job, id=job_id)
        
        # Determine rater and ratee
        rater = request.user
        if rater == job.customer:
            ratee = job.driver
            rater_type = 'customer'
        elif rater == job.driver:
            ratee = job.customer
            rater_type = 'driver'
        else:
            return Response({"error": "You are not part of this job"}, status=403)
            
        if not ratee:
             return Response({"error": "No user to rate"}, status=400)

        rating = Rating.objects.create(
            job=job,
            rater=rater,
            ratee=ratee,
            rater_type=rater_type,
            **serializer.validated_data
        )
        
        return Response(RatingSerializer(rating).data, status=status.HTTP_201_CREATED)

class UserRatingsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated] # Or AllowAny if public
    
    def get(self, request, user_id):
        ratings = Rating.objects.filter(ratee__id=user_id, is_visible=True)
        avg_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0.0
        count = ratings.count()
        
        # Breakdown (Mock logic or manual aggregation)
        breakdown = {
            "5_stars": ratings.filter(rating=5).count(),
            "4_stars": ratings.filter(rating=4).count(),
            "3_stars": ratings.filter(rating=3).count(),
            "2_stars": ratings.filter(rating=2).count(),
            "1_star": ratings.filter(rating=1).count(),
        }
        
        return Response({
            "average_rating": round(avg_rating, 1),
            "total_ratings": count,
            "rating_breakdown": breakdown,
            "recent_reviews": RatingSerializer(ratings.order_by('-created_at')[:5], many=True).data
        })

