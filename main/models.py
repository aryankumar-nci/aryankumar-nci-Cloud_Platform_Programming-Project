from django.db import models
import uuid
from users.models import Profile, Location
from .consts import CARS_BRANDS, TRANSMISSION_OPTIONS

class Listing(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # User can have many listings, but a listing will have only one user (one-to-many relationship)
    seller = models.ForeignKey(Profile, on_delete=models.CASCADE)
    brand = models.CharField(max_length=25, choices=CARS_BRANDS, default=None)
    model = models.CharField(max_length=64)
    vin = models.CharField(max_length=18)
    mileage = models.IntegerField(default=0)
    color = models.CharField(max_length=24, default='White')
    description = models.TextField()
    engine = models.CharField(max_length=24)
    transmission = models.CharField(
        max_length=24, choices=TRANSMISSION_OPTIONS, default=None)
    location = models.OneToOneField(
        Location, on_delete=models.SET_NULL, null=True)
    
    # Updated field to store the image URL
    image = models.URLField(max_length=2048)

    def __str__(self):
        return f"{self.seller.user.username}'s Listing - {self.model}"
