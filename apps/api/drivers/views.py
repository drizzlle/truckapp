from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from geopy.distance import geodesic
from django.utils import timezone

from apps.users.models import DriverProfile, VehiclePhoto
from .serializers import DriverSearchResultSerializer, DriverAvailabilitySerializer, DriverStatsSerializer, VehiclePhotoSerializer

class AvailableDriversView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DriverSearchResultSerializer
    
    def get_queryset(self):
        pickup_lat = self.request.query_params.get('pickup_lat')
        pickup_lng = self.request.query_params.get('pickup_lng')
        vehicle_type_id = self.request.query_params.get('vehicle_type_id')
        radius_km = float(self.request.query_params.get('radius_km', 20))
        
        if not (pickup_lat and pickup_lng and vehicle_type_id):
            return DriverProfile.objects.none()
            
        pickup_coords = (float(pickup_lat), float(pickup_lng))
        
        queryset = DriverProfile.objects.filter(
            is_available=True,
            # is_approved=True, # Ensure this field exists in model if used
            vehicle_type__id=vehicle_type_id
        ).select_related('user', 'vehicle_type')
        
        # Filter by distance
        nearby_drivers = []
        for driver in queryset:
            if driver.current_location_lat and driver.current_location_lng:
                driver_coords = (driver.current_location_lat, driver.current_location_lng)
                try:
                    distance = geodesic(pickup_coords, driver_coords).km
                    if distance <= radius_km:
                        driver.distance_km = distance # Annotate for serializer
                        nearby_drivers.append(driver)
                except ValueError:
                    pass # Handle invalid coordinates
                    
        # Sort by distance (optional but good UX)
        nearby_drivers.sort(key=lambda x: x.distance_km)
        
        return nearby_drivers

class ToggleAvailabilityView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if request.user.user_type != 'driver':
            return Response({"error": "Only drivers can toggle availability"}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = DriverAvailabilitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            profile = request.user.driver_profile
            profile.is_available = serializer.validated_data['is_available']
            
            if 'current_lat' in serializer.validated_data and 'current_lng' in serializer.validated_data:
                profile.current_location_lat = serializer.validated_data['current_lat']
                profile.current_location_lng = serializer.validated_data['current_lng']
                profile.last_location_update = timezone.now()
                
            profile.save()
            
            return Response({
                "message": "Availability updated",
                "is_available": profile.is_available
            })
        except DriverProfile.DoesNotExist:
            return Response({"error": "Driver profile not found"}, status=status.HTTP_404_NOT_FOUND)

class DriverStatsView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DriverStatsSerializer

    def get_object(self):
        if self.request.user.user_type != 'driver':
            self.permission_denied(self.request, message="Only drivers can access stats")
        return get_object_or_404(DriverProfile, user=self.request.user)

class VehiclePhotosView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.user_type != 'driver':
            return Response({"error": "Only drivers can access vehicle photos"}, status=status.HTTP_403_FORBIDDEN)

        try:
            driver_profile = request.user.driver_profile
            photos = driver_profile.vehicle_photos.all()
            serializer = VehiclePhotoSerializer(photos, many=True)
            return Response(serializer.data)
        except DriverProfile.DoesNotExist:
            return Response({"error": "Driver profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        if request.user.user_type != 'driver':
            return Response({"error": "Only drivers can upload vehicle photos"}, status=status.HTTP_403_FORBIDDEN)

        try:
            driver_profile = request.user.driver_profile
            current_count = driver_profile.vehicle_photos.count()

            if current_count >= 5:
                return Response({"error": "Maximum 5 vehicle photos allowed"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = VehiclePhotoSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            photo = serializer.save(driver_profile=driver_profile)

            if current_count == 0:
                photo.is_primary = True
                photo.save()

            return Response(VehiclePhotoSerializer(photo).data, status=status.HTTP_201_CREATED)
        except DriverProfile.DoesNotExist:
            return Response({"error": "Driver profile not found"}, status=status.HTTP_404_NOT_FOUND)

class VehiclePhotoDetailView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, photo_id):
        if request.user.user_type != 'driver':
            return Response({"error": "Only drivers can delete vehicle photos"}, status=status.HTTP_403_FORBIDDEN)

        try:
            driver_profile = request.user.driver_profile
            photo = get_object_or_404(VehiclePhoto, id=photo_id, driver_profile=driver_profile)
            photo.delete()
            return Response({"message": "Photo deleted successfully"}, status=status.HTTP_200_OK)
        except DriverProfile.DoesNotExist:
            return Response({"error": "Driver profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, photo_id):
        if request.user.user_type != 'driver':
            return Response({"error": "Only drivers can update vehicle photos"}, status=status.HTTP_403_FORBIDDEN)

        try:
            driver_profile = request.user.driver_profile
            photo = get_object_or_404(VehiclePhoto, id=photo_id, driver_profile=driver_profile)

            if 'is_primary' in request.data and request.data['is_primary']:
                VehiclePhoto.objects.filter(driver_profile=driver_profile).update(is_primary=False)

            serializer = VehiclePhotoSerializer(photo, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data)
        except DriverProfile.DoesNotExist:
            return Response({"error": "Driver profile not found"}, status=status.HTTP_404_NOT_FOUND)
