from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from listings.models import Listing, Amenity, Booking, Review
from faker import Faker
import random
from datetime import datetime, timedelta

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Seeds the database with sample listings data'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=5, help='Number of users to create')
        parser.add_argument('--listings', type=int, default=10, help='Number of listings to create')
        parser.add_argument('--bookings', type=int, default=20, help='Number of bookings to create')
        parser.add_argument('--reviews', type=int, default=30, help='Number of reviews to create')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))
        
        # Create amenities if they don't exist
        amenities = self.create_amenities()
        
        # Create users
        users = self.create_users(options['users'])
        
        # Create listings
        listings = self.create_listings(options['listings'], users, amenities)
        
        # Create bookings
        bookings = self.create_bookings(options['bookings'], users, listings)
        
        # Create reviews
        self.create_reviews(options['reviews'], users, listings)
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))

    def create_amenities(self):
        amenities_data = [
            {'name': 'WiFi', 'icon': 'fa-wifi'},
            {'name': 'Pool', 'icon': 'fa-swimming-pool'},
            {'name': 'Kitchen', 'icon': 'fa-utensils'},
            {'name': 'Parking', 'icon': 'fa-parking'},
            {'name': 'Air Conditioning', 'icon': 'fa-snowflake'},
            {'name': 'TV', 'icon': 'fa-tv'},
        ]
        
        amenities = []
        for data in amenities_data:
            amenity, created = Amenity.objects.get_or_create(**data)
            amenities.append(amenity)
            if created:
                self.stdout.write(f'Created amenity: {amenity.name}')
        
        return amenities

    def create_users(self, count):
        users = []
        for i in range(count):
            user = User.objects.create_user(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                password='testpass123',
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )
            users.append(user)
            self.stdout.write(f'Created user: {user.username}')
        return users

    def create_listings(self, count, users, amenities):
        property_types = ['Apartment', 'House', 'Villa', 'Cottage', 'Loft']
        listings = []
        
        for i in range(count):
            host = random.choice(users)
            listing = Listing.objects.create(
                host=host,
                title=f"{random.choice(property_types)} in {fake.city()}",
                description=fake.paragraph(nb_sentences=5),
                address=fake.street_address(),
                price_per_night=random.randint(50, 500),
                max_guests=random.randint(1, 10),
                bedrooms=random.randint(1, 5),
                bathrooms=random.randint(1, 3),
                is_active=random.choice([True, False])
            )
            
            # Add random amenities
            listing.amenities.set(random.sample(amenities, k=random.randint(1, len(amenities))))
            listings.append(listing)
            self.stdout.write(f'Created listing: {listing.title}')
        
        return listings

    def create_bookings(self, count, users, listings):
        bookings = []
        for i in range(count):
            user = random.choice(users)
            listing = random.choice(listings)
            
            # Generate random dates in the future
            today = datetime.now().date()
            check_in = today + timedelta(days=random.randint(1, 30))
            check_out = check_in + timedelta(days=random.randint(1, 14))
            
            booking = Booking.objects.create(
                user=user,
                listing=listing,
                check_in=check_in,
                check_out=check_out,
                status=random.choice(['pending', 'confirmed', 'cancelled'])
            )
            bookings.append(booking)
            self.stdout.write(f'Created booking: {user.username} booked {listing.title}')
        
        return bookings

    def create_reviews(self, count, users, listings):
        for i in range(count):
            user = random.choice(users)
            listing = random.choice(listings)
            
            Review.objects.create(
                user=user,
                listing=listing,
                rating=random.randint(1, 5),
                comment=fake.paragraph(nb_sentences=2)
            )
            self.stdout.write(f'Created review: {user.username} rated {listing.title}')