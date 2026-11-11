from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Category, Listing


class ListingWorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.owner = User.objects.create_user("owner", password="Pass12345!x")
        cls.other = User.objects.create_user("other", password="Pass12345!x")
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
        self.client.login(username="owner", password="Pass12345!x")
        response = self.client.get(reverse("edit_listing", args=[listing.id]))
        self.assertEqual(response.status_code, 200)

    def test_other_user_cannot_edit(self):
        listing = self.make_listing()
        self.client.login(username="other", password="Pass12345!x")
        response = self.client.get(reverse("edit_listing", args=[listing.id]))
        self.assertEqual(response.status_code, 404)

    def test_other_user_cannot_delete(self):
        listing = self.make_listing()
        self.client.login(username="other", password="Pass12345!x")
        response = self.client.post(reverse("delete_listing", args=[listing.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Listing.objects.filter(id=listing.id).exists())