from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Category, Listing, Report

PASSWORD = "Pass12345!x"


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.owner = User.objects.create_user("owner", password=PASSWORD)
        cls.other = User.objects.create_user("other", password=PASSWORD)
        cls.category = Category.objects.create(name="Tailors", slug="tailors")

    def make_listing(self, **kwargs):
        data = dict(
            owner=self.owner,
            title="Test listing",
            listing_type=Listing.ListingType.SERVICE,
            category=self.category,
            description="Test description",
            location="Zaria",
            contact_phone="2348012345678",
        )
        data.update(kwargs)
        return Listing.objects.create(**data)


class ListingWorkflowTests(BaseTestCase):
    def test_new_listing_is_pending(self):
        self.assertEqual(self.make_listing().status, Listing.Status.PENDING)

    def test_pending_listing_hidden_from_home(self):
        self.make_listing(title="Hidden one")
        response = self.client.get(reverse("home"))
        self.assertNotContains(response, "Hidden one")

    def test_active_listing_shown_on_home(self):
        self.make_listing(title="Visible one", status=Listing.Status.ACTIVE)
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Visible one")

    def test_search_by_category_name(self):
        self.make_listing(title="Suit sewing", status=Listing.Status.ACTIVE)
        response = self.client.get(reverse("home"), {"q": "tailor"})
        self.assertContains(response, "Suit sewing")

    def test_add_listing_requires_login(self):
        response = self.client.get(reverse("add_listing"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_owner_can_open_edit_page(self):
        listing = self.make_listing()
        self.client.login(username="owner", password=PASSWORD)
        response = self.client.get(reverse("edit_listing", args=[listing.id]))
        self.assertEqual(response.status_code, 200)

    def test_other_user_cannot_edit(self):
        listing = self.make_listing()
        self.client.login(username="other", password=PASSWORD)
        response = self.client.get(reverse("edit_listing", args=[listing.id]))
        self.assertEqual(response.status_code, 404)

    def test_other_user_cannot_delete(self):
        listing = self.make_listing()
        self.client.login(username="other", password=PASSWORD)
        response = self.client.post(reverse("delete_listing", args=[listing.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Listing.objects.filter(id=listing.id).exists())


class DetailPageTests(BaseTestCase):
    def test_active_listing_detail_is_public(self):
        listing = self.make_listing(title="Public ad", status=Listing.Status.ACTIVE)
        response = self.client.get(reverse("listing_detail", args=[listing.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Public ad")

    def test_pending_listing_detail_hidden_from_visitors(self):
        listing = self.make_listing()
        response = self.client.get(reverse("listing_detail", args=[listing.id]))
        self.assertEqual(response.status_code, 404)

    def test_owner_can_see_own_pending_listing(self):
        listing = self.make_listing()
        self.client.login(username="owner", password=PASSWORD)
        response = self.client.get(reverse("listing_detail", args=[listing.id]))
        self.assertEqual(response.status_code, 200)


class ReportTests(BaseTestCase):
    def setUp(self):
        self.listing = self.make_listing(status=Listing.Status.ACTIVE)
        self.url = reverse("report_listing", args=[self.listing.id])

    def test_report_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_user_can_report_a_listing(self):
        self.client.login(username="other", password=PASSWORD)
        response = self.client.post(self.url, {"reason": "scam", "details": "Asked for money first"})
        self.assertRedirects(response, reverse("report_thanks"))
        self.assertEqual(Report.objects.count(), 1)

    def test_owner_cannot_report_own_listing(self):
        self.client.login(username="owner", password=PASSWORD)
        self.client.post(self.url, {"reason": "scam"})
        self.assertEqual(Report.objects.count(), 0)

    def test_same_user_cannot_report_twice(self):
        self.client.login(username="other", password=PASSWORD)
        self.client.post(self.url, {"reason": "scam"})
        self.client.post(self.url, {"reason": "fake"})
        self.assertEqual(Report.objects.count(), 1)

    def test_three_reports_hide_the_listing(self):
        User = get_user_model()
        for name in ("a", "b", "c"):
            User.objects.create_user(name, password=PASSWORD)
            self.client.login(username=name, password=PASSWORD)
            self.client.post(self.url, {"reason": "scam"})
            self.client.logout()
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.status, Listing.Status.PENDING)
class LifecycleTests(BaseTestCase):
    def valid_data(self):
        return {
            "title": "Edited title",
            "listing_type": "service",
            "category": self.category.id,
            "description": "New text",
            "price": "",
            "location": "Zaria",
            "contact_phone": "2348012345678",
            "contact_whatsapp": "",
        }

    def test_editing_active_listing_sends_it_back_to_pending(self):
        listing = self.make_listing(status=Listing.Status.ACTIVE)
        self.client.login(username="owner", password=PASSWORD)
        self.client.post(reverse("edit_listing", args=[listing.id]), self.valid_data())
        listing.refresh_from_db()
        self.assertEqual(listing.status, Listing.Status.PENDING)
        self.assertEqual(listing.title, "Edited title")

    def test_owner_can_mark_listing_as_sold(self):
        listing = self.make_listing(title="Sold item", status=Listing.Status.ACTIVE)
        self.client.login(username="owner", password=PASSWORD)
        self.client.post(reverse("close_listing", args=[listing.id]))
        listing.refresh_from_db()
        self.assertEqual(listing.status, Listing.Status.CLOSED)
        self.assertNotContains(self.client.get(reverse("home")), "Sold item")

    def test_other_user_cannot_mark_listing_as_sold(self):
        listing = self.make_listing(status=Listing.Status.ACTIVE)
        self.client.login(username="other", password=PASSWORD)
        response = self.client.post(reverse("close_listing", args=[listing.id]))
        self.assertEqual(response.status_code, 404)
        listing.refresh_from_db()
        self.assertEqual(listing.status, Listing.Status.ACTIVE)

    def test_mark_sold_requires_post(self):
        listing = self.make_listing(status=Listing.Status.ACTIVE)
        self.client.login(username="owner", password=PASSWORD)
        response = self.client.get(reverse("close_listing", args=[listing.id]))
        self.assertEqual(response.status_code, 405)
class InfoPageTests(TestCase):
    def test_info_pages_load(self):
        for name in ("rules", "privacy", "help"):
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)