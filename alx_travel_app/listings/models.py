from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model() 

class Listing(models.Model):
    """Property listing (e.g., apartment, house)."""
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=200)
    description = models.TextField()
    address = models.CharField(max_length=255)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    max_guests = models.PositiveIntegerField()
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()
    amenities = models.ManyToManyField('Amenity', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} (Host: {self.host.username})"

class Booking(models.Model):
    """Reservation for a listing."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Calculate total_price before saving."""
        nights = (self.check_out - self.check_in).days
        self.total_price = nights * self.listing.price_per_night
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} → {self.listing.title} ({self.check_in} to {self.check_out})"

class Review(models.Model):
    """User review for a listing."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'listing')  # Prevent duplicate reviews

    def __str__(self):
        return f"{self.user.username} rated {self.listing.title} {self.rating}/5"

class Amenity(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)  # FontAwesome class or image path

    def __str__(self):
        return self.name