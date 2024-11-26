from django import forms
from .models import Listing
from .s3_utils import upload_to_s3

class ListingForm(forms.ModelForm):
    image = forms.ImageField()

    class Meta:
        model = Listing
        fields = ['brand', 'model', 'vin', 'mileage', 'color', 'description', 'engine', 'transmission', 'image']

    def save(self, commit=True):
        listing = super().save(commit=False)
        image_file = self.cleaned_data['image']

        # Upload image to S3 and set the image URL
        file_name = f"listings/{listing.seller.user.username}/{image_file.name}"
        uploaded_url = upload_to_s3(image_file, file_name)
        if uploaded_url:
            listing.image = uploaded_url  # Store the S3 URL in the model field
        else:
            raise Exception("Failed to upload image to S3")

        if commit:
            listing.save()
        return listing
