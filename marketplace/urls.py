from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("listing/<int:listing_id>/", views.listing_detail, name="listing_detail"),
    path("listing/<int:listing_id>/report/", views.report_listing, name="report_listing"),
    path("report/thanks/", views.report_thanks, name="report_thanks"),
    path("rules/", views.rules, name="rules"),
    path("privacy/", views.privacy, name="privacy"),
    path("help/", views.help_page, name="help"),
    path("contact/", views.contact, name="contact"),
    path("add-listing/", views.add_listing, name="add_listing"),
    path("my-listings/", views.my_listings, name="my_listings"),
    path("my-listings/<int:listing_id>/edit/", views.edit_listing, name="edit_listing"),
    path("my-listings/<int:listing_id>/sold/", views.close_listing, name="close_listing"),
    path("my-listings/<int:listing_id>/delete/", views.delete_listing, name="delete_listing"),
]
