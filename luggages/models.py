from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

User = settings.AUTH_USER_MODEL


class TimestampedModel(models.Model):
    """A model with timestamp fields for creation and last update."""

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Customer(TimestampedModel):
    """Model representing a customer instance."""

    phone_number_validator = RegexValidator(
        regex=r"^(0803|0806|0809|0703|0706|0709|0813|0816|0819)\d{7}$",
        message="Phone number must start with 0803, 0806, 0809, 0703, 0706, 0709, 0813, 0816, or 0819 and be 11 digits long.",
    )

    fullname = models.CharField(
        _("Full Name"),
        max_length=150,
        unique=True,
        help_text=_("Full name of the customer."),
    )
    email = models.EmailField(
        _("Email Address"),
    )
    address = models.CharField(
        _("Address"),
        max_length=100,
    )
    next_of_kin = models.CharField(
        _("Next of Kin"),
        max_length=150,
    )
    next_of_kin_phonenumber = models.CharField(
        _("Next of Kin Phone Number"),
        max_length=11,
        validators=[phone_number_validator],
    )

    class Meta:
        ordering = ["fullname"]
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")

    def __str__(self):
        """String representation of the Customer model."""
        return self.fullname


class Bus(TimestampedModel):
    """Model representing a bus instance."""

    plate_number_validator = RegexValidator(
        regex=r"^[A-Z]{3}-\d{3}-[A-Z]{3}$",
        message="Plate number must be in the format: AAA-111-AAA",
    )

    plate_number = models.CharField(
        _("Plate Number"),
        max_length=11,
        unique=True,
        validators=[plate_number_validator],
    )
    driver_name = models.CharField(
        _("Driver's Name"),
        max_length=150,
    )
    max_luggage_weight = models.PositiveIntegerField(
        _("Maximum Luggage Weight"),
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        ordering = ["created"]
        verbose_name = _("Bus")
        verbose_name_plural = _("Buses")

    def __str__(self):
        """String representation of the Bus model."""
        return self.plate_number


class State(TimestampedModel):
    """Model representing a state instance."""

    name = models.CharField(
        _("Name"),
        max_length=20,
        unique=True,
    )
    short_code = models.CharField(_("Short Code"), max_length=3, help_text=_("3-letter state shortcode."))

    class Meta:
        ordering = ["created"]
        verbose_name = _("State")
        verbose_name_plural = _("States")

    def __str__(self):
        """String representation of the State model."""
        return self.name


class ParkLocation(TimestampedModel):
    """Model representing a park location instance."""

    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        verbose_name=_("State"),
    )
    location = models.CharField(
        _("Location"),
        max_length=50,
        unique=True,
        help_text=_("The city the park is located in."),
    )
    full_address = models.CharField(
        _("Full Address"),
        max_length=255,
    )
    contact = models.TextField(
        _("Contact"),
    )

    class Meta:
        ordering = ["state"]
        verbose_name = _("Park Location")
        verbose_name_plural = _("Park Locations")

    def __str__(self):
        """String representation of the ParkLocation model."""
        return self.location


class Weight(TimestampedModel):
    """Model representing a weight instance."""

    name = models.CharField(
        _("Name"),
        max_length=20,
    )
    min_weight = models.PositiveIntegerField(
        _("Minimum Weight"),
        validators=[MinValueValidator(1)],
    )
    price = models.DecimalField(
        _("Price"), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )

    class Meta:
        ordering = ["created"]
        verbose_name = _("Weight")
        verbose_name_plural = _("Weights")

    def __str__(self):
        """String representation of the Weight model."""
        return self.name


class BagType(TimestampedModel):
    """Model representing a bag type instance."""

    class SizeOption(models.TextChoices):
        """Choices for bag size options."""

        SMALL = "S", _("Small")
        MEDIUM = "M", _("Medium")
        LARGE = "L", _("Large")

    name = models.CharField(
        _("Name"),
        max_length=50,
    )
    size = models.CharField(
        _("Size"),
        max_length=1,
        choices=SizeOption.choices,
    )
    description = models.TextField(
        _("Description"),
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = _("Bag Type")
        verbose_name_plural = _("Bag Types")

    def __str__(self):
        """String representation of the BagType model."""
        return f"{self.name} - {self.get_size_display()}"


class Trip(TimestampedModel):
    """Model representing a trip instance."""

    name = models.CharField(
        _("Trip"),
        max_length=50,
        unique=True,
        help_text=_("Format: ENU-to-LAG-01-01-2000"),
    )
    bus = models.ForeignKey(
        Bus,
        on_delete=models.CASCADE,
        verbose_name=_("Bus"),
    )
    departure = models.ForeignKey(
        ParkLocation,
        on_delete=models.CASCADE,
        related_name="departures",
        verbose_name=_("Departure"),
    )
    destination = models.ForeignKey(
        ParkLocation,
        on_delete=models.CASCADE,
        related_name="arrivals",
        verbose_name=_("Destination"),
    )
    date_of_journey = models.DateTimeField(
        _("Date of Journey"),
    )

    def __str__(self):
        """String representation of the Trip model."""
        return self.name

    def save(self, *args, **kwargs):
        """Override save method to automatically generate Trip name."""
        # Format trip name based on departure and destination location
        self.name = f"{self.departure.state.short_code}-to-{self.destination.state.short_code}-{self.date_of_journey.strftime('%d-%m-%Y')}"
        super().save(*args, **kwargs)

    def clean(self):
        """Ensure departure and destination locations are different."""
        if self.departure_id == self.destination_id:
            raise ValidationError("Departure and destination locations must be different.")

    def total_luggage_amount(self):
        """Calculate the total luggage amount for the trip."""
        return sum(luggage_bill.total_amount() for luggage_bill in self.luggagebills.all())


class LuggageBill(TimestampedModel):
    """Model representing a luggage bill instance."""

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        verbose_name=_("Customer"),
    )
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name="luggagebills",
        verbose_name=_("Trip"),
    )
    added_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Added by"),
    )

    class Meta:
        ordering = ["-created"]
        verbose_name = _("Luggage Bill")
        verbose_name_plural = _("Luggage Bills")

    def __str__(self):
        """String representation of the LuggageBill model."""
        return f"Luggage Bill for {self.customer}"

    def total_amount(self):
        """Calculate the total amount for the luggage bill."""
        return sum(item.amount() for item in self.items.all())

    def total_weight_per_customer(self):
        """Calculate the total weight per customer for the luggage bill."""
        return sum(item.weight.min_weight for item in self.items.all())


class Luggage(TimestampedModel):
    """Model representing a piece of luggage."""

    luggagebill = models.ForeignKey(
        LuggageBill,
        related_name="items",
        on_delete=models.CASCADE,
        verbose_name=_("Luggage Bill"),
    )
    weight = models.ForeignKey(
        Weight,
        on_delete=models.CASCADE,
        verbose_name=_("Weight"),
    )
    bag_type = models.ForeignKey(
        BagType,
        on_delete=models.CASCADE,
        verbose_name=_("Bag Type"),
    )
    quantity = models.PositiveIntegerField(
        _("Quantity"),
        default=1,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        ordering = ["-created"]
        verbose_name = _("Luggage")
        verbose_name_plural = _("Luggages")

    def __str__(self):
        """String representation of the Luggage model."""
        return str(self.id)

    def amount(self):
        """Calculate the amount for the luggage."""
        return self.weight.price * self.quantity
