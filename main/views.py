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
from automotive.sns_email import send_sns_email


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
            listing_form = ListingForm(request.POST,request.FILES)
            location_form = LocationForm(request.POST,)
            
            if listing_form.is_valid() and location_form.is_valid():
                listing = listing_form.save(commit=False)
                listing_location = location_form.save()
                listing.seller = request.user.profile
                listing.location = listing_location
                listing.save()
                messages.info(request,f'{listing.model} Listing Posted Successfully!')
                return redirect('home')
            else:
                raise Exception()
        except Exception as e:
            print(e)
            messages.error(request,'Oops! An error occured while listing')
    elif request.method == 'GET':
        
        listing_form = ListingForm()
        location_form = LocationForm()
    return render (request, 'views/list.html',{'listing_form':listing_form,'location_form':location_form,})

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
        if listing is None:
            raise Exception
        if request.method == 'POST':
            listing_form = ListingForm(
                request.POST, request.FILES, instance=listing)
            location_form = LocationForm(
                request.POST, instance=listing.location)
            if listing_form.is_valid and location_form.is_valid:
                listing_form.save()
                location_form.save()
                messages.info(request, f'Listing {id} updated successfully!')
                return redirect('home')
            else:
                messages.error(
                    request, f'An error occured while trying to edit the listing.')
                return reload()
        else:
            listing_form = ListingForm(instance=listing)
            location_form = LocationForm(instance=listing.location)
        context = {
            'location_form': location_form,
            'listing_form': listing_form
        }
        return render(request, 'views/edit.html', context)
    except Exception as e:
        messages.error(
            request, f'An error occured while trying to access the edit page.')
        return redirect('home')

@login_required
def enquire_listing_by_email(request, id):
    listing = get_object_or_404(Listing, id=id)
    try:
        email_subject = f"{request.user.username} is interested in {listing.model}"
        email_message = (
            f"Hello {listing.seller.user.username},\n\n"
            f"{request.user.username} has expressed interest in your {listing.model} listed on AutoVerse.\n"
            f"Please get in touch with them via their contact information.\n\n"
            "Thank you for using AutoVerse!"
        )

        response = send_sns_email(email_subject, email_message)

        if response:
            return JsonResponse({"success": True, "message": "Email sent successfully!"})
        else:
            return JsonResponse({"success": False, "message": "Failed to send email."}, status=500)
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({"success": False, "message": str(e)}, status=500)