from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ListingForm, ReportForm
from .models import Listing, ListingImage, Report

# A listing goes back to "pending" when this many different users report it.
REPORT_HIDE_THRESHOLD = 3


def home(request):
    query = request.GET.get("q", "").strip()
    listing_type = request.GET.get("type", "").strip()

    listings = (
        Listing.objects.filter(status=Listing.Status.ACTIVE)
        .select_related("category")
        .prefetch_related("images")
    )

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


def listing_detail(request, listing_id):
    listing = get_object_or_404(
        Listing.objects.select_related("category", "owner").prefetch_related("images"),
        id=listing_id,
    )
    user = request.user
    is_owner = user.is_authenticated and listing.owner_id == user.id

    # Only active listings are public. The owner and staff can still see the rest.
    if listing.status != Listing.Status.ACTIVE and not (is_owner or user.is_staff):
        raise Http404

    already_reported = (
        user.is_authenticated and listing.reports.filter(reporter=user).exists()
    )

    return render(
        request,
        "marketplace/listing_detail.html",
        {"listing": listing, "is_owner": is_owner, "already_reported": already_reported},
    )


@login_required
def report_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, status=Listing.Status.ACTIVE)

    if listing.owner_id == request.user.id:
        messages.error(request, "You cannot report your own listing.")
        return redirect("listing_detail", listing_id=listing.id)

    if listing.reports.filter(reporter=request.user).exists():
        messages.info(request, "You have already reported this listing.")
        return redirect("listing_detail", listing_id=listing.id)

    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.listing = listing
            report.reporter = request.user
            report.save()

            open_reports = listing.reports.filter(status=Report.Status.OPEN).count()
            if open_reports >= REPORT_HIDE_THRESHOLD:
                listing.status = Listing.Status.PENDING
                listing.save(update_fields=["status", "updated_at"])

            return redirect("report_thanks")
    else:
        form = ReportForm()

    return render(
        request,
        "marketplace/report_listing.html",
        {"form": form, "listing": listing},
    )


def report_thanks(request):
    return render(request, "marketplace/report_thanks.html")


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
            messages.success(request, "Your listing was submitted and is waiting for review.")
            return redirect("my_listings")
    else:
        form = ListingForm()

    return render(request, "marketplace/add_listing.html", {"form": form})


@login_required
def my_listings(request):
    listings = (
        Listing.objects.filter(owner=request.user)
        .select_related("category")
        .prefetch_related("images")
    )
    return render(request, "marketplace/my_listings.html", {"listings": listings})


@login_required
def edit_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, owner=request.user)
    was_active = listing.status == Listing.Status.ACTIVE

    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            listing = form.save(commit=False)
            if was_active:
                listing.status = Listing.Status.PENDING
            listing.save()
            photo = form.cleaned_data.get("photo")
            if photo:
                ListingImage.objects.create(listing=listing, image=photo)
            if was_active:
                messages.success(
                    request,
                    "Your changes were saved. The listing is waiting for review again.",
                )
            else:
                messages.success(request, "Your listing was updated.")
            return redirect("my_listings")
    else:
        form = ListingForm(instance=listing)

    return render(
        request,
        "marketplace/edit_listing.html",
        {"form": form, "listing": listing},
    )


@login_required
@require_POST
def close_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, owner=request.user)
    listing.status = Listing.Status.CLOSED
    listing.save(update_fields=["status", "updated_at"])
    messages.success(request, "Marked as sold. It is no longer shown publicly.")
    return redirect("my_listings")


@login_required
def delete_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, owner=request.user)

    if request.method == "POST":
        listing.delete()
        messages.success(request, "Your listing was deleted.")
        return redirect("my_listings")

    return render(request, "marketplace/delete_listing.html", {"listing": listing})
def rules(request):
    return render(request, "marketplace/rules.html")


def privacy(request):
    return render(request, "marketplace/privacy.html")


def help_page(request):
    return render(request, "marketplace/help.html")