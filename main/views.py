from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Listing
from .forms import ListingForm
from users.forms import LocationForm
from .filters import ListingFilter
from django.core.mail import EmailMessage  # Use EmailMessage for dynamic sender email
from django.conf import settings
import logging  # Add this to set up logging

# Set up logger
logger = logging.getLogger(__name__)

def main_view(request):
    logger.info("Main page accessed.")
    return render(request, "views/main.html", {"name": "AutoVerse"})


@login_required
def home_view(request):
    try:
        listings = Listing.objects.all()
        listing_filter = ListingFilter(request.GET, queryset=listings)
        context = {
            'listing_filter': listing_filter
        }
        logger.info(f"Home page accessed by user: {request.user.username}.")
        return render(request, "views/home.html", context)
    except Exception as e:
        logger.error(f"Error accessing home page: {str(e)}")
        messages.error(request, "An error occurred.")
        return redirect('main')


@login_required
def list_view(request):
    if request.method == 'POST':
        try:
            listing_form = ListingForm(request.POST, request.FILES)
            location_form = LocationForm(request.POST)

            if listing_form.is_valid() and location_form.is_valid():
                listing = listing_form.save(commit=False)
                location = location_form.save()
                listing.seller = request.user.profile
                listing.location = location
                listing.save()
                logger.info(f"New listing created by user {request.user.username}: {listing.model}")
                messages.success(request, f'{listing.model} listed successfully!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid data. Please correct the errors.')
                logger.warning(f"Invalid data provided by user {request.user.username} while creating a listing.")
        except Exception as e:
            logger.error(f"Error creating listing by user {request.user.username}: {str(e)}")
            messages.error(request, f"An error occurred: {e}")
    else:
        listing_form = ListingForm()
        location_form = LocationForm()

    return render(request, 'views/list.html', {'listing_form': listing_form, 'location_form': location_form})


@login_required
def listing_view(request, id):
    try:
        listing = Listing.objects.get(id=id)
        if listing is None:
            raise Exception
        logger.info(f"Listing {id} accessed by user {request.user.username}.")
        return render(request, 'views/listing.html', {'listing': listing})
    except Exception as e:
        logger.error(f"Error accessing listing {id}: {str(e)}")
        messages.error(request, f'Invalid UID {id} was provided.')
        return redirect('home')


@login_required
def edit_view(request, id):
    try:
        listing = Listing.objects.get(id=id)
        if not listing:
            raise Exception("Listing not found")

        if request.method == 'POST':
            listing_form = ListingForm(request.POST, request.FILES, instance=listing)
            location_form = LocationForm(request.POST, instance=listing.location)

            if location_form.is_valid() and listing_form.is_valid():
                listing_form.save()
                location_form.save()
                logger.info(f"Listing {id} updated successfully by user {request.user.username}.")
                messages.success(request, f'Listing {id} updated successfully!')
                return redirect('home')
            else:
                messages.error(request, 'Error while updating listing. Please check the details.')
                logger.warning(f"Invalid update attempt on listing {id} by user {request.user.username}.")
        else:
            listing_form = ListingForm(instance=listing)
            location_form = LocationForm(instance=listing.location)

        context = {
            'listing_form': listing_form,
            'location_form': location_form
        }
        return render(request, 'views/edit.html', context)
    except Exception as e:
        logger.error(f"Error updating listing {id} by user {request.user.username}: {str(e)}")
        messages.error(request, f"An error occurred: {e}")
        return redirect('home')


@login_required
def enquire_listing_by_email(request, id):
    listing = get_object_or_404(Listing, id=id)
    try:
        # Sender email
        sender_email = request.user.email

        # Recipient email
        recipient_email = listing.seller.user.email

        # Email details
        subject = f"Interest in Your Listing: {listing.model}"
        message = (
            f"Hello {listing.seller.user.username},\n\n"
            f"{request.user.username} ({sender_email}) is interested in your car listing for {listing.model}.\n"
            f"Please contact them directly at {sender_email} for further communication.\n\n"
            "Thank you for using AutoVerse!"
        )

        # Creating the email object
        email = EmailMessage(
            subject,
            message,
            sender_email,  
            [recipient_email],  
        )

        # Send email
        email.send(fail_silently=False)
        logger.info(f"Inquiry email sent for listing {id} by user {request.user.username}.")
        return JsonResponse({"success": True, "message": "Email sent successfully!"})
    except Exception as e:
        logger.error(f"Error sending inquiry email for listing {id} by user {request.user.username}: {str(e)}")
        return JsonResponse({"success": False, "message": f"Failed to send email: {str(e)}"}, status=500)
