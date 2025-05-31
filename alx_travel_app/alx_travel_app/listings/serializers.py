from rest_framework import serializers
from .models import Listing, Booking, Amenity
from django.contrib.auth import get_user_model

User = get_user_model()

# Helper serializer for nested User representation
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

# Serializer for Amenity
class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ['id', 'name', 'icon']

# Main Listing Serializer
class ListingSerializer(serializers.ModelSerializer):
    host = UserSerializer(read_only=True)  # Nested host details
    amenities = AmenitySerializer(many=True, read_only=True)  # Nested amenities
    
    class Meta:
        model = Listing
        fields = [
            'id', 'host', 'title', 'description', 'address', 
            'price_per_night', 'max_guests', 'bedrooms', 
            'bathrooms', 'amenities', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'host', 'created_at']

# Booking Serializer
class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Nested user details
    listing = serializers.PrimaryKeyRelatedField(queryset=Listing.objects.all())  # Accept listing ID
    
    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'listing', 'check_in', 'check_out', 
            'total_price', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'total_price', 'created_at']

    def validate(self, data):
        """Validate booking dates (e.g., check_out > check_in)."""
        if data['check_out'] <= data['check_in']:
            raise serializers.ValidationError("Check-out date must be after check-in.")
        return data