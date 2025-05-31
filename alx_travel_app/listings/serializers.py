from rest_framework import serializers
from .models import Listing, Booking, Review
from django.contrib.auth.models import User

class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    listing = serializers.StringRelatedField(read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(), source='listing', write_only=True
    )

    class Meta:
        model = Booking
        fields = ['id', 'user', 'listing', 'listing_id', 'check_in', 'check_out',
                  'number_of_guests', 'total_price', 'created_at']
        read_only_fields = ['id', 'user', 'listing', 'total_price', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        listing = validated_data.pop('listing')
        check_in = validated_data.get('check_in')
        check_out = validated_data.get('check_out')
        number_of_guests = validated_data.get('number_of_guests')

        # Calculate total price
        duration = (check_out - check_in).days
        total_price = listing.price_per_night * duration * number_of_guests

        booking = Booking.objects.create(
            user=user,
            listing=listing,
            check_in=check_in,
            check_out=check_out,
            number_of_guests=number_of_guests,
            total_price=total_price
        )
        return booking


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    listing = serializers.StringRelatedField(read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(), source='listing', write_only=True
    )

    class Meta:
        model = Review
        fields = ['id', 'user', 'listing', 'listing_id', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'listing', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        listing = validated_data.pop('listing')
        rating = validated_data.get('rating')
        comment = validated_data.get('comment')

        review = Review.objects.create(
            user=user,
            listing=listing,
            rating=rating,
            comment=comment
        )
        return review