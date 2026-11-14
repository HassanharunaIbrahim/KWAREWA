from datetime import timedelta
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ContactForm, ListingForm, ReportForm
from .models import Category, ContactMessage, Listing, ListingImage, Report

# A listing goes back to "pending" when this many different users report it.
REPORT_HIDE_THRESHOLD = 3

# Number of listings shown per page on the homepage.
PAGE_SIZE = 12

# Abuse limits (per user, per rolling 24 hours). Staff are exempt from the listing limit.
MAX_LISTINGS_PER_DAY = 5
MAX_CONTACTS_PER_DAY = 5

ORDERINGS = {
    "newest": ("-created_at",),
    "oldest": ("created_at",),
    "price_low": (F("price").asc(nulls_last=True), "-created_at"),
    "price_high": (F("price").desc(nulls_last=True), "-created_at"),
}


def _decimal_or_none(value):
    """Turn user input into a Decimal, or None when it is empty or invalid."""
    if not value:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def _last_24_hours():
    return timezone.now() - timedelta(days=1)


def home(request):
    query = request.GET.get("q", "").strip()
    listing_type = request.GET.get("type", "").strip()
    category_slug = request.GET.get("category", "").strip()
    location = request.GET.get("location", "").strip()
    min_price_raw = request.GET.get("min_price", "").strip()
    max_price_raw = request.GET.get("max_price", "").strip()
    sort = request.GET.get("sort", "newest")
    if sort not in ORDERINGS:
        sort = "newest"

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

    if category_slug:
        listings = listings.filter(category__slug=category_slug)

    if location:
        listings = listings.filter(location__icontains=location)

    min_price = _decimal_or_none(min_price_raw)
    max_price = _decimal_or_none(max_price_raw)
    if min_price is not None:
        listings = listings.filter(price__gte=min_price)
    if max_price is not None:
        listings = listings.filter(price__lte=max_price)

    listings = listings.order_by(*ORDERINGS[sort])

    paginator = Paginator(listings, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    # Keep the filters in the "Previous / Next" links.
    params = request.GET.copy()
    params.pop("page", None)

    return render(
        request,
        "marketplace/home.html",
        {
            "listings": page_obj,
            "page_obj": page_obj,
            "paginator": paginator,
            "querystring": params.urlencode(),
            "query": query,
            "listing_type": listing_type,
            "categories": Category.objects.all(),
            "selected_category": category_slug,
            "location": location,
            "min_price": min_price_raw,
            "max_price": max_price_raw,
            "sort": sort,
            "has_filters": bool(
                query
                or listing_type
                or category_slug
                or location
                or min_price_raw
                or max_price_raw
            ),
        },
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
        posted_today = Listing.objects.filter(
            owner=request.user, created_at__gte=_last_24_hours()
        ).count()
        if posted_today >= MAX_LISTINGS_PER_DAY and not request.user.is_staff:
            messages.error(
                request,
                f"You can publish up to {MAX_LISTINGS_PER_DAY} listings per day. "
                "Please try again tomorrow.",
            )
            return redirect("my_listings")

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


@login_required
def contact(request):
    if request.method == "POST":
        sent_today = ContactMessage.objects.filter(
            user=request.user, created_at__gte=_last_24_hours()
        ).count()
        if sent_today >= MAX_CONTACTS_PER_DAY:
            messages.error(
                request,
                "You have reached today's limit of messages. Please try again tomorrow.",
            )
            return redirect("contact")

        form = ContactForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = request.user
            message.save()
            messages.success(request, "Thank you. Your message was sent to the team.")
            return redirect("help")
    else:
        form = ContactForm(initial={"name": request.user.get_username()})

    return render(request, "marketplace/contact.html", {"form": form})
