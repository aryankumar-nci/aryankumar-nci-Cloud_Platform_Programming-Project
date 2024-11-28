from django import forms
from .models import Listing
from .s3_utils import upload_to_s3

class ListingForm(forms.ModelForm):
    image = forms.ImageField(required=False)

    class Meta:
        model = Listing
        fields = ['brand', 'model', 'vin', 'mileage', 'color', 'description', 'engine', 'transmission', 'image']

    
