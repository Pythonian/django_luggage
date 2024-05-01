from django.contrib.auth.models import User
from django.template import Context, Template
from django.test import TestCase
from django.utils import timezone

from luggages.templatetags.luggage_tags import display_trip_luggages

from ..models import (
    BagType,
    Bus,
    Customer,
    Luggage,
    LuggageBill,
    ParkLocation,
    State,
    Trip,
    Weight,
)


class TemplateTagTestCase(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            fullname="John Doe",
            email="john@example.com",
            address="123 Main St",
            next_of_kin="Jane Doe",
            next_of_kin_phonenumber="08031234567",
        )
        self.bus = Bus.objects.create(
            plate_number="AAA-111-BBB",
            driver_name="Seyi Pythonian",
            max_luggage_weight=100,
        )
        self.departure_state = State.objects.create(name="Lagos", short_code="LAG")
        self.destination_state = State.objects.create(name="Enugu", short_code="ENU")
        self.departure = ParkLocation.objects.create(
            state=self.departure_state,
            location="Lekki",
            full_address="123 Main St, Los Angeles, CA",
            contact="(123) 456-7890",
        )
        self.destination = ParkLocation.objects.create(
            state=self.destination_state,
            location="Nsukka",
            full_address="123 Main St, Los Angeles, CA",
            contact="(123) 456-7890",
        )
        self.trip = Trip.objects.create(
            name="LAG-to-ENU-01-05-2024",
            bus=self.bus,
            departure=self.departure,
            destination=self.destination,
            date_of_journey=timezone.now(),
        )
        self.user = User.objects.create(username="testuser")
        self.luggage_bill = LuggageBill.objects.create(
            customer=self.customer,
            trip=self.trip,
            added_by=self.user,
        )
        self.weight = Weight.objects.create(name="Heavy", min_weight=50, price=10.50)
        self.bag_type = BagType.objects.create(name="Backpack", size="M")
        self.luggage_item1 = Luggage.objects.create(
            luggagebill=self.luggage_bill,
            weight=self.weight,
            bag_type=self.bag_type,
            quantity=2,
        )

    def test_display_trip_luggages(self):
        rendered = display_trip_luggages(self.trip.id)
        self.assertIn("luggages", rendered)
        self.assertIn("trip", rendered)
        self.assertEqual(rendered["trip"], self.trip)
        self.assertIn(self.luggage_bill, rendered["luggages"])

    def test_template_rendering(self):
        # Create a test template containing the template tag
        template_to_render = Template("{% load luggage_tags %}{% display_trip_luggages trip.id %}")

        # Render the template with a context containing the trip
        rendered_template = template_to_render.render(Context({"trip": self.trip}))

        # Assert that the trip's luggages are in the rendered template
        self.assertIn(self.luggage_bill.customer.fullname, rendered_template)
