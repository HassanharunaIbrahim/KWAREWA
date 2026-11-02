from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("add-listing/", views.add_listing, name="add_listing"),
    path("my-listings/", views.my_listings, name="my_listings"),
    path("my-listings/<int:listing_id>/edit/", views.edit_listing, name="edit_listing"),
    path("my-listings/<int:listing_id>/delete/", views.delete_listing, name="delete_listing"),
]