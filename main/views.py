from django.shortcuts import redirect, render,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Listing
from .forms import ListingForm
from users.forms import LocationForm 
from .filters import ListingFilter
from django.core.mail import send_mail
from django.conf import settings
from main.sns_email import send_sns_email
import boto3



def main_view(request):
    return render(request,"views/main.html",{"name":"AutoVerse"})

@login_required
def home_view(request):
    #to show the listing from database
    listings = Listing.objects.all()
    listing_filter = ListingFilter(request.GET,queryset=listings)
    
    context = {
        
        'listing_filter':listing_filter
    }
    return render(request, "views/home.html",context)
    
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
                messages.success(request, f'{listing.model} listed successfully!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid data. Please correct the errors.')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
    else:
        listing_form = ListingForm()
        location_form = LocationForm()

    return render(request, 'views/list.html', {'listing_form': listing_form, 'location_form': location_form})

@login_required
def listing_view(request,id):
    try:
        listing = Listing.objects.get(id=id)
        if listing is None:
            raise Exception
        return render (request,'views/listing.html',{'listing': listing,})
    except Exception as e:
        messages.error(request,f'Invalid UID {id} was provided.')
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
            #print("Listing form", listing_form.is_valid(), listing_form )
            # print("Location form", location_form.is_valid(), location_form)
            
            
            
            if location_form.is_valid():
                listing_form.save()
                location_form.save()
                messages.success(request, f'Listing {id} updated successfully!')
                return redirect('home')
            else:
                
                messages.error(request, 'Error while updating listing. Please check the details.')
        else:
            listing_form = ListingForm(instance=listing)
            location_form = LocationForm(instance=listing.location)

        context = {
            'listing_form': listing_form,
            'location_form': location_form
        }
        return render(request, 'views/edit.html', context)
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect('home')
@login_required
def enquire_listing_by_email(request, id):
    listing = get_object_or_404(Listing, id=id)
    try:
        # Email details
        subject = f"Interest in Your Listing: {listing.model}"
        message = (
            f"Hello {listing.seller.user.username},\n\n"
            f"{request.user.username} is interested in your car listing for {listing.model}.\n"
            f"Please contact them at {request.user.email} for further communication.\n\n"
            "Thank you for using AutoVerse!"
        )
        sender_email = settings.DEFAULT_FROM_EMAIL
        recipient_email = [listing.seller.user.email]  # Seller's email

        # Send email using SES
        send_mail(
            subject,
            message,
            sender_email,
            recipient_email,
            fail_silently=False,
        )

        return JsonResponse({"success": True, "message": "Email sent successfully!"})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Failed to send email: {str(e)}"}, status=500)