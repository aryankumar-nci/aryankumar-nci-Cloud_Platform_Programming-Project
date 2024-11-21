from django.urls import path
from django.conf import settings
from .views import main_view,home_view,list_view,listing_view,edit_view,enquire_listing_by_email
urlpatterns = [
    path('',main_view,name='main'),
    path('home/',home_view,name='home'),
    path('list/', list_view, name='list'),
    path('listing/<str:id>/',listing_view,name='listing'),
    path('listing/<str:id>/edit/',edit_view,name='edit'),
    path('listing/<str:id>/enquire/',enquire_listing_by_email,name='enquire_listing'), 
      
    
    
]
