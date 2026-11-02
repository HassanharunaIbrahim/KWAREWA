from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from .models import Listing
from .forms import ListingForm

def home(request):
    query = request.GET.get("q", "").strip()
    listing_type = request.GET.get("type", "").strip()

    listings = Listing.objects.order_by("-created_at")

    if query:
        listings = listings.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(category__icontains=query)
            | Q(location__icontains=query)
            | Q(listing_type__icontains=query)
        )

    if listing_type in ("service", "product"):
        listings = listings.filter(listing_type=listing_type)

    listings = listings[:12]

    return render(
        request,
        "marketplace/home.html",
        {
            "listings": listings,
            "query": query,
            "listing_type": listing_type,
        },
    )

@login_required
def add_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)

        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            return redirect("home")
    else:
        form = ListingForm()

    return render(
        request,
        "marketplace/add_listing.html",
        {"form": form},
    )
@login_required
def my_listings(request):
    listings = Listing.objects.filter(
        owner=request.user
    ).order_by("-created_at")

    return render(
        request,
        "marketplace/my_listings.html",
        {"listings": listings},
    )
@login_required
def edit_listing(request, listing_id):
    listing = get_object_or_404(
        Listing,
        id=listing_id,
        owner=request.user
    )

    if request.method == "POST":
        form = ListingForm(request.POST, instance=listing)

        if form.is_valid():
            form.save()
            return redirect("my_listings")
    else:
        form = ListingForm(instance=listing)

    return render(
        request,
        "marketplace/edit_listing.html",
        {"form": form, "listing": listing},
    )
@login_required
def delete_listing(request, listing_id):
    listing = get_object_or_404(
        Listing,
        id=listing_id,
        owner=request.user
    )

    if request.method == "POST":
        listing.delete()
        return redirect("my_listings")

    return render(
        request,
        "marketplace/delete_listing.html",
        {"listing": listing},
    )