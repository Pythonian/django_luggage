from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

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


class CustomerModelTestCase(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            fullname="Seyi Pythonian",
            email="seyi@pythonian.com",
            address="123 Main St",
            next_of_kin="Madabevel",
            next_of_kin_phonenumber="08031234567",
        )

    def test_string_representation(self):
        self.assertEqual(str(self.customer), "Seyi Pythonian")

    def test_phone_number_validator(self):
        # Valid phone number
        self.customer.next_of_kin_phonenumber = "08031234567"
        self.customer.full_clean()  # Should not raise a validation error

        # Invalid phone number
        with self.assertRaises(ValidationError):
            self.customer.next_of_kin_phonenumber = "12345678901"
            self.customer.full_clean()


class BusModelTestCase(TestCase):
    def setUp(self):
        self.bus = Bus.objects.create(plate_number="ABC-123-DEF", driver_name="Alice Smith", max_luggage_weight=100)

    def test_string_representation(self):
        self.assertEqual(str(self.bus), "ABC-123-DEF")

    def test_plate_number_validator(self):
        # Valid plate number
        self.bus.plate_number = "ABC-123-DEF"
        self.bus.full_clean()  # Should not raise a validation error

        # Invalid plate number
        with self.assertRaises(ValidationError):
            self.bus.plate_number = "123-ABC-456"
            self.bus.full_clean()

    def test_max_luggage_weight_blank_or_null(self):
        # Max luggage weight blank
        self.bus.max_luggage_weight = None
        self.bus.full_clean()  # Should not raise a validation error

        # Max luggage weight null
        self.bus.max_luggage_weight = ""
        self.bus.full_clean()  # Should not raise a validation error

    def test_max_luggage_weight_positive_integer(self):
        # Valid max luggage weight
        self.bus.max_luggage_weight = 100
        self.bus.full_clean()  # Should not raise a validation error

        # Negative max luggage weight
        with self.assertRaises(ValidationError):
            self.bus.max_luggage_weight = -50
            self.bus.full_clean()

        # Zero max luggage weight
        with self.assertRaises(ValidationError):
            self.bus.max_luggage_weight = 0
            self.bus.full_clean()


class StateModelTestCase(TestCase):
    def setUp(self):
        self.state = State.objects.create(name="California", short_code="CAL")

    def test_string_representation(self):
        self.assertEqual(str(self.state), "California")

    def test_short_code_max_length(self):
        # Valid short code length
        self.state.short_code = "ABC"
        self.state.full_clean()  # Should not raise a validation error

        # Invalid short code length
        with self.assertRaises(ValidationError):
            self.state.short_code = "ABCD"
            self.state.full_clean()


class ParkLocationModelTestCase(TestCase):
    def setUp(self):
        self.state = State.objects.create(name="California", short_code="CAL")
        self.park_location = ParkLocation.objects.create(
            state=self.state,
            location="Lekki",
            full_address="123 Main St, Lekki, CA",
            contact="(123) 456-7890",
        )

    def test_string_representation(self):
        self.assertEqual(str(self.park_location), "Lekki")

    def test_unique_location(self):
        # Valid unique location
        self.park_location.full_clean()  # Should not raise a validation error

        # Invalid duplicate location
        with self.assertRaises(IntegrityError):
            ParkLocation.objects.create(
                state=self.state,
                location="Lekki",
                full_address="456 Oak St, Lekki, CA",
                contact="(456) 789-0123",
            )

    def test_relationship_with_state(self):
        # Ensure the park location is associated with the correct state
        self.assertEqual(self.park_location.state, self.state)

    def test_full_address_max_length(self):
        # Valid full address length
        self.park_location.full_address = "A" * 255
        self.park_location.full_clean()  # Should not raise a validation error

        # Invalid full address length
        with self.assertRaises(ValidationError):
            self.park_location.full_address = "A" * 256
            self.park_location.full_clean()


class WeightModelTestCase(TestCase):
    def setUp(self):
        self.weight = Weight.objects.create(name="Heavy", min_weight=50, price=10.50)

    def test_string_representation(self):
        self.assertEqual(str(self.weight), "Heavy")

    def test_min_weight_positive_integer(self):
        # Valid min weight
        self.weight.min_weight = 50
        self.weight.full_clean()  # Should not raise a validation error

        # Negative min weight
        with self.assertRaises(ValidationError):
            self.weight.min_weight = -50
            self.weight.full_clean()

        # Zero min weight
        with self.assertRaises(ValidationError):
            self.weight.min_weight = 0
            self.weight.full_clean()

    def test_price_decimal_field(self):
        # Valid price
        self.weight.price = 10.50
        self.weight.full_clean()  # Should not raise a validation error

        # Invalid price
        with self.assertRaises(ValidationError):
            self.weight.price = -10.50
            self.weight.full_clean()


class BagTypeModelTestCase(TestCase):
    def setUp(self):
        self.bag_type = BagType.objects.create(name="Backpack", size="M", description="A medium-sized backpack.")

    def test_string_representation(self):
        self.assertEqual(str(self.bag_type), "Backpack - Medium")

    def test_size_choices(self):
        # Valid size choices
        self.assertIn(self.bag_type.size, ["S", "M", "L"])

        # Invalid size
        with self.assertRaises(ValidationError):
            self.bag_type.size = "XL"
            self.bag_type.full_clean()

    def test_description_can_be_null(self):
        # Valid null description
        self.bag_type.description = None
        self.bag_type.full_clean()  # Should not raise a validation error

        # Valid blank description
        self.bag_type.description = ""
        self.bag_type.full_clean()  # Should not raise a validation error


class TripModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="Arie")
        self.state_lagos = State.objects.create(name="Lagos", short_code="LAG")
        self.state_enugu = State.objects.create(name="Enugu", short_code="ENU")
        self.departure_location = ParkLocation.objects.create(
            state=self.state_lagos,
            location="Ikeja",
            full_address="123 Ikeja Rd, Lagos",
            contact="(123) 456-7890",
        )
        self.destination_location = ParkLocation.objects.create(
            state=self.state_enugu,
            location="Nsukka",
            full_address="456 Nsukka St, Enugu",
            contact="(987) 654-3210",
        )
        self.bus = Bus.objects.create(
            plate_number="ABC-123-DEF",
            driver_name="Seyi Pythonian",
            max_luggage_weight=100,
        )
        self.customer = Customer.objects.create(
            fullname="Seyi Pythonian",
            email="seyi@pythonian.com",
            address="123 Main St",
            next_of_kin="Madabevel",
            next_of_kin_phonenumber="08031234567",
        )
        self.trip = Trip.objects.create(
            bus=self.bus,
            departure=self.departure_location,
            destination=self.destination_location,
            date_of_journey=timezone.now(),
        )
        self.luggage_bill = LuggageBill.objects.create(
            customer=self.customer,
            trip=self.trip,
            added_by=self.user,
        )
        self.weight = Weight.objects.create(name="Heavy", min_weight=50, price=100)
        self.bag_type = BagType.objects.create(name="Backpack", size="M")
        self.luggage_item = Luggage.objects.create(
            luggagebill=self.luggage_bill,
            weight=self.weight,
            bag_type=self.bag_type,
            quantity=1,
        )

    def test_string_representation(self):
        expected_string = f"{self.departure_location.state.short_code}-to-{self.destination_location.state.short_code}-{self.trip.date_of_journey.strftime('%d-%m-%Y')}"
        self.assertEqual(str(self.trip), expected_string)

    def test_save_method(self):
        # Test if save method generates the name field correctly
        expected_name = f"{self.departure_location.state.short_code}-to-{self.destination_location.state.short_code}-{self.trip.date_of_journey.strftime('%d-%m-%Y')}"
        self.assertEqual(self.trip.name, expected_name)

    def test_total_luggage_amount_method(self):
        # Test if total_luggage_amount method calculates correctly
        self.luggage_bill.total_amount = 100  # Mocking total amount
        self.assertEqual(self.trip.total_luggage_amount(), 100)


class LuggageBillModelTestCase(TestCase):
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
        self.luggage_item2 = Luggage.objects.create(
            luggagebill=self.luggage_bill,
            weight=self.weight,
            bag_type=self.bag_type,
            quantity=3,
        )

    def test_string_representation(self):
        expected_string = f"Luggage Bill for {self.customer}"
        self.assertEqual(str(self.luggage_bill), expected_string)

    def test_total_amount_calculation(self):
        expected_total_amount = (self.luggage_item1.weight.price * self.luggage_item1.quantity) + (
            self.luggage_item2.weight.price * self.luggage_item2.quantity
        )
        self.assertEqual(self.luggage_bill.total_amount(), expected_total_amount)

    def test_total_weight_per_customer_calculation(self):
        expected_total_weight_per_customer = (
            self.luggage_item1.weight.min_weight + self.luggage_item2.weight.min_weight
        )
        self.assertEqual(self.luggage_bill.total_weight_per_customer(), expected_total_weight_per_customer)


class LuggageModelTestCase(TestCase):
    def setUp(self):
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
        self.weight = Weight.objects.create(name="Heavy", min_weight=50, price=10.50)
        self.bag_type = BagType.objects.create(name="Backpack", size="M")
        self.customer = Customer.objects.create(
            fullname="John Doe",
            email="john@example.com",
            address="123 Main St",
            next_of_kin="Jane Doe",
            next_of_kin_phonenumber="08031234567",
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
        self.luggage = Luggage.objects.create(
            luggagebill=self.luggage_bill,
            weight=self.weight,
            bag_type=self.bag_type,
            quantity=2,
        )

    def test_string_representation(self):
        self.assertEqual(str(self.luggage), str(self.luggage.id))

    def test_amount_method(self):
        expected_amount = self.weight.price * self.luggage.quantity
        self.assertEqual(self.luggage.amount(), expected_amount)

    def test_quantity_positive_integer(self):
        # Valid quantity
        self.luggage.quantity = 2
        self.luggage.full_clean()  # Should not raise a validation error

        # Negative quantity
        with self.assertRaises(ValidationError):
            self.luggage.quantity = -2
            self.luggage.full_clean()

        # Zero quantity
        with self.assertRaises(ValidationError):
            self.luggage.quantity = 0
            self.luggage.full_clean()

    def test_relationship_with_weight(self):
        # Ensure the luggage is associated with the correct weight
        self.assertEqual(self.luggage.weight, self.weight)

    def test_relationship_with_bag_type(self):
        # Ensure the luggage is associated with the correct bag type
        self.assertEqual(self.luggage.bag_type, self.bag_type)
