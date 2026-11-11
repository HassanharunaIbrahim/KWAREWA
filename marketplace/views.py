from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ListingForm
from .models import Listing, ListingImage


def home(request):
    query = request.GET.get("q", "").strip()
    listing_type = request.GET.get("type", "").strip()

    listings = Listing.objects.filter(
        status=Listing.Status.ACTIVE
    ).select_related("category")

    if query:
        listings = listings.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
            | Q(location__icontains=query)
        )

    if listing_type in Listing.ListingType.values:
        listings = listings.filter(listing_type=listing_type)

    listings = listings[:12]

    return render(
        request,
        "marketplace/home.html",
        {"listings": listings, "query": query, "listing_type": listing_type},
    )


@login_required
def add_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            photo = form.cleaned_data.get("photo")
            if photo:
                ListingImage.objects.create(listing=listing, image=photo)
            return redirect("home")
    else:
        form = ListingForm()

    return render(request, "marketplace/add_listing.html", {"form": form})


@login_required
def my_listings(request):
    listings = Listing.objects.filter(owner=request.user).select_related("category")
    return render(request, "marketplace/my_listings.html", {"listings": listings})


@login_required
def edit_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, owner=request.user)

    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            photo = form.cleaned_data.get("photo")
            if photo:
                ListingImage.objects.create(listing=listing, image=photo)
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
    listing = get_object_or_404(Listing, id=listing_id, owner=request.user)

    if request.method == "POST":
        listing.delete()
        return redirect("my_listings")

    return render(request, "marketplace/delete_listing.html", {"listing": listing})