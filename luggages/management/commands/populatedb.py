import random
import string
import time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from ...models import (
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


class Command(BaseCommand):
    help = "Seed the database"

    def handle(self, *args, **kwargs):
        fake = Faker()
        start_time = time.time()

        # Create superuser
        self.stdout.write("Creating superuser...")
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@admin.com", "admin")
            self.stdout.write(self.style.SUCCESS("Superuser created successfully."))
        else:
            self.stdout.write(self.style.SUCCESS("Superuser already exists."))

        # Populate Customer
        self.stdout.write("Populating Customers...")
        for _ in range(100):
            fullname = fake.name()
            email = fake.email()
            address = fake.address()
            next_of_kin = fake.name()
            # Generate a Nigerian phone number with the required prefix
            prefix = random.choice(["0803", "0806", "0809", "0703", "0706", "0709", "0813", "0816", "0819"])
            # Generate the remaining 7 digits randomly
            remaining_digits = "".join(random.choices(string.digits, k=7))
            next_of_kin_phonenumber = f"{prefix}{remaining_digits}"
            Customer.objects.create(
                fullname=fullname,
                email=email,
                address=address,
                next_of_kin=next_of_kin,
                next_of_kin_phonenumber=next_of_kin_phonenumber,
            )

        # Populate Bus
        self.stdout.write("Populating Buses...")
        for _ in range(20):
            # Generate random letters for the plate number
            letters1 = "".join(random.choices(string.ascii_uppercase, k=3))
            letters2 = "".join(random.choices(string.ascii_uppercase, k=3))
            # Generate random numbers for the plate number
            numbers = random.randint(100, 999)
            # Concatenate the parts to form the plate number
            plate_number = f"{letters1}-{numbers}-{letters2}"
            driver_name = fake.name()
            max_luggage_weight = random.randint(100, 500)
            if not Bus.objects.filter(plate_number=plate_number).exists():
                Bus.objects.create(
                    plate_number=plate_number,
                    driver_name=driver_name,
                    max_luggage_weight=max_luggage_weight,
                )

        # Populate State
        self.stdout.write("Populating States...")
        states = [
            "Abia",
            "Adamawa",
            "Akwa Ibom",
            "Anambra",
            "Bauchi",
            "Bayelsa",
            "Benue",
            "Borno",
            "Cross River",
            "Delta",
            "Ebonyi",
            "Edo",
            "Ekiti",
            "Enugu",
            "Gombe",
            "Imo",
            "Jigawa",
            "Kaduna",
            "Kano",
            "Katsina",
            "Kebbi",
            "Kogi",
            "Kwara",
            "Lagos",
            "Nasarawa",
            "Niger",
            "Ogun",
            "Ondo",
            "Osun",
            "Oyo",
            "Plateau",
            "Rivers",
            "Sokoto",
            "Taraba",
            "Yobe",
            "Zamfara",
            "FCT",
        ]
        for state_name in states:
            # Check if a state with the same name already exists
            if not State.objects.filter(name=state_name).exists():
                # Generate short code
                short_code = state_name[:3].upper()
                State.objects.create(name=state_name, short_code=short_code)

        # Populate ParkLocation
        self.stdout.write("Populating Park Locations...")
        for _ in range(50):
            state = random.choice(State.objects.all())
            location = fake.city()
            full_address = fake.address()
            contact = fake.phone_number()
            if not ParkLocation.objects.filter(location=location).exists():
                ParkLocation.objects.create(
                    state=state,
                    location=location,
                    full_address=full_address,
                    contact=contact,
                )

        # Populate Weight
        self.stdout.write("Populating Weights...")
        weights = {
            "Two Kilogramme": 2,
            "Three Kilogramme": 3,
            "Four Kilogramme": 4,
            "Five Kilogramme": 5,
        }
        for name, min_weight in weights.items():
            price = random.randint(500, 5000)
            Weight.objects.create(
                name=name,
                min_weight=min_weight,
                price=price,
            )

        # Populate BagType
        self.stdout.write("Populating Bag Types...")
        names = ["Backpack", "Suitcase", "Duffel bag", "Tote bag", "Ghana-Must-Go"]
        for name in names:
            description = fake.text()
            for size in BagType.SizeOption.choices:
                BagType.objects.create(
                    name=name,
                    size=size[0],
                    description=description,
                )

        # Populate Trip
        self.stdout.write("Populating Trips...")
        for _ in range(50):
            bus = random.choice(Bus.objects.all())
            departure = random.choice(ParkLocation.objects.all())
            # Ensure departure and destination states are different
            destination = random.choice(ParkLocation.objects.exclude(pk=departure.pk))
            date_of_journey = fake.date_time_this_year(tzinfo=timezone.get_current_timezone())
            # Format trip name
            name = f"{departure.state.short_code}-to-{destination.state.short_code}-{date_of_journey.strftime('%d-%m-%Y')}"
            if not Trip.objects.filter(name=name).exists():
                Trip.objects.create(
                    name=name,
                    bus=bus,
                    departure=departure,
                    destination=destination,
                    date_of_journey=date_of_journey,
                )

        # Populate LuggageBill
        self.stdout.write("Populating Luggage Bills...")
        for _ in range(100):
            customer = random.choice(Customer.objects.all())
            trip = random.choice(Trip.objects.all())
            added_by = User.objects.get(username="admin")
            LuggageBill.objects.create(
                customer=customer,
                trip=trip,
                added_by=added_by,
            )

        # Populate Luggage
        self.stdout.write("Populating Luggages...")
        for luggage_bill in LuggageBill.objects.all():
            for _ in range(random.randint(1, 3)):
                weight = random.choice(Weight.objects.all())
                bag_type = random.choice(BagType.objects.all())
                quantity = random.randint(1, 3)
                Luggage.objects.create(
                    luggagebill=luggage_bill,
                    weight=weight,
                    bag_type=bag_type,
                    quantity=quantity,
                )

        end_time = time.time()
        # Round to 2 decimal places
        execution_time = round(end_time - start_time, 2)
        # Format as a string with 2 decimal places
        execution_time_str = f"{execution_time:.2f}"
        self.stdout.write(
            self.style.SUCCESS(f"Initial data population complete. Time taken: {execution_time_str} seconds")
        )
