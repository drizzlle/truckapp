from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from apps.jobs.models import Job
from .serializers import JobSerializer, JobCreateSerializer

class JobListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return JobCreateSerializer
        return JobSerializer

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'customer':
            return Job.objects.filter(customer=user).order_by('-created_at')
        elif user.user_type == 'driver':
            return Job.objects.filter(driver=user).order_by('-created_at')
        return Job.objects.none()

    def create(self, request, *args, **kwargs):
        if request.user.user_type != 'customer':
            return Response({"error": "Only customers can create jobs"}, status=403)

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

class DriverJobRequestsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = JobSerializer
    
    def get_queryset(self):
        # Logic to find open jobs matching driver criteria
        # For MVP, just showing pending jobs that have no driver or specific driver = me
        user = self.request.user
        if user.user_type != 'driver':
            return Job.objects.none()
            
        # Simple matching: Pending jobs where driver is None OR driver is me (direct request)
        return Job.objects.filter(
            status='pending'
        ).filter(driver=None) | Job.objects.filter(status='pending', driver=user)

class JobDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = JobSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'customer':
            return Job.objects.filter(customer=user)
        elif user.user_type == 'driver':
            return Job.objects.filter(driver=user) | Job.objects.filter(status='pending', driver=None)
        return Job.objects.none()

class AcceptJobView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        job = get_object_or_404(Job, id=pk, status='pending')
        if request.user.user_type != 'driver':
            return Response({"error": "Only drivers can accept jobs"}, status=403)

        if job.driver and job.driver != request.user:
            return Response({"error": "Job already assigned to another driver"}, status=400)

        try:
            job.change_status('driver_assigned', request.user)
            job.driver = request.user
            job.driver_assigned_at = timezone.now()
            job.save()

            return Response({"message": "Job accepted successfully", "job": JobSerializer(job).data})
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

class RejectJobView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        job = get_object_or_404(Job, id=pk, driver=request.user, status='pending')
        # If driver was pre-assigned, they can reject.
        # Logic: Remove driver assignment
        job.driver = None
        job.save()
        return Response({"message": "Job declined"})

class DriverConfirmPickupView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        job = get_object_or_404(Job, id=pk, driver=request.user, status='driver_assigned')
        # In some flows, driver confirms -> status changes or waits for customer. 
        # Doc says: "Pickup confirmed. Waiting for customer confirmation." status stays driver_assigned? 
        # Or maybe explicit status? Doc response says "status": "driver_assigned". 
        # Actually typically this might trigger a notification.
        
        # Use status 'pickup_confirmed' if no double confirmation needed, but doc implies customer confirms too.
        # I'll keep status as is or maybe intermediate state if model supported it. 
        # Model has 'pickup_confirmed'.
        # I'll set it to 'pickup_confirmed' for simplicity unless customer MUST confirm separately.
        # Doc 5.4 says Customer Confirm Pickup -> status: 'pickup_confirmed'.
        # So Driver Confirm is just a signal.
        
        return Response({"message": "Pickup confirmed. Waiting for customer confirmation.", "status": job.status})

class CustomerConfirmPickupView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        job = get_object_or_404(Job, id=pk, customer=request.user)

        try:
            job.change_status('pickup_confirmed', request.user)
            job.pickup_confirmed_at = timezone.now()
            job.save()
            return Response({"message": "Pickup confirmed", "status": job.status})
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

class StartDeliveryView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        job = get_object_or_404(Job, id=pk, driver=request.user)

        try:
            job.change_status('in_transit', request.user)
            return Response({"message": "Delivery started", "status": job.status})
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

class MarkDeliveredView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        job = get_object_or_404(Job, id=pk, driver=request.user)

        try:
            job.change_status('delivered', request.user)
            job.delivered_at = timezone.now()
            job.save()
            return Response({"message": "Marked as delivered", "status": job.status})
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

class ConfirmDeliveryView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        job = get_object_or_404(Job, id=pk, customer=request.user)

        try:
            job.change_status('completed', request.user)
            job.completed_at = timezone.now()
            job.save()
            return Response({"message": "Delivery confirmed", "status": job.status})
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

class CancelJobView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        job = get_object_or_404(Job, id=pk)

        if user != job.customer and user != job.driver:
            return Response({"error": "You are not authorized to cancel this job"}, status=403)

        if user == job.customer:
            new_status = 'cancelled_by_customer'
        else:
            new_status = 'cancelled_by_driver'

        try:
            reason = request.data.get('reason')
            job.change_status(new_status, user, reason)
            job.cancelled_at = timezone.now()
            job.cancellation_reason = reason
            job.save()
            return Response({"message": "Job cancelled", "status": job.status})
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

class DisputeJobView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        job = get_object_or_404(Job, id=pk)

        if user != job.customer and user != job.driver:
            return Response({"error": "You are not authorized to dispute this job"}, status=403)

        try:
            reason = request.data.get('reason')
            job.change_status('disputed', user, reason)
            job.dispute_reason = reason
            job.save()
            return Response({"message": "Dispute submitted", "status": job.status})
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

class UpdateLocationView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        from apps.jobs.models import DriverLocationHistory

        if request.user.user_type != 'driver':
            return Response({"error": "Only drivers can update location"}, status=403)

        job = get_object_or_404(Job, id=pk, driver=request.user)

        if job.status not in ['driver_assigned', 'pickup_confirmed', 'in_transit']:
            return Response({"error": "Cannot update location for job in this status"}, status=400)

        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        if not latitude or not longitude:
            return Response({"error": "latitude and longitude are required"}, status=400)

        DriverLocationHistory.objects.create(
            job=job,
            driver=request.user,
            latitude=latitude,
            longitude=longitude,
            accuracy=request.data.get('accuracy'),
            speed=request.data.get('speed')
        )

        if hasattr(request.user, 'driver_profile'):
            profile = request.user.driver_profile
            profile.current_location_lat = latitude
            profile.current_location_lng = longitude
            profile.last_location_update = timezone.now()
            profile.save()

        return Response({"message": "Location updated"})

