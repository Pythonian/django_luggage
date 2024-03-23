from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

User = settings.AUTH_USER_MODEL


class Customer(models.Model):
    """Model representing a customer instance."""

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
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["fullname"]
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")

    def __str__(self):
        """String representation of the Customer model."""
        return self.fullname


class Bus(models.Model):
    """Model representing a bus instance."""

    plate_number = models.CharField(
        _("Plate Number"),
        max_length=20,
        unique=True,
    )
    driver_name = models.CharField(
        _("Driver's Name"),
        max_length=150,
    )
    max_luggage_weight = models.PositiveIntegerField(
        _("Maximum Luggage Weight"),
        blank=True,
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created"]
        verbose_name = _("Bus")
        verbose_name_plural = _("Buses")

    def __str__(self):
        """String representation of the Bus model."""
        return self.plate_number


class State(models.Model):
    """Model representing a state instance."""

    name = models.CharField(
        _("Name"),
        max_length=20,
    )
    short_code = models.CharField(
        _("Short Code"),
        max_length=3,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created"]
        verbose_name = _("State")
        verbose_name_plural = _("States")

    def __str__(self):
        """String representation of the State model."""
        return self.name


class ParkLocation(models.Model):
    """Model representing a park location instance."""

    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        verbose_name=_("State"),
    )
    location = models.CharField(
        _("Location"),
        max_length=50,
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


class Weight(models.Model):
    """Model representing a weight instance."""

    name = models.CharField(
        _("Name"),
        max_length=20,
    )
    min_weight = models.PositiveIntegerField(
        _("Minimum Weight"),
    )
    price = models.DecimalField(
        _("Price"),
        max_digits=10,
        decimal_places=2,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created"]
        verbose_name = _("Weight")
        verbose_name_plural = _("Weights")

    def __str__(self):
        """String representation of the Weight model."""
        return self.name


class BagType(models.Model):
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


class Trip(models.Model):
    """Model representing a trip instance."""

    name = models.CharField(
        _("Trip"),
        max_length=50,
        unique=True,
        help_text=_("Format: EN-to-LA-01-01-2000"),
    )
    bus = models.ForeignKey(
        Bus,
        on_delete=models.CASCADE,
        verbose_name=_("Bus"),
    )
    departure = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name="departures",
        verbose_name=_("Departure"),
    )
    destination = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name="arrivals",
        verbose_name=_("Destination"),
    )
    date_of_journey = models.DateTimeField(
        _("Date of Journey"),
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """String representation of the Trip model."""
        return self.name

    def total_luggage_amount(self):
        """Calculate the total luggage amount for the trip."""
        return sum(luggage_bill.total_amount() for luggage_bill in self.luggagebills.all())


class LuggageBill(models.Model):
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
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

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


class Luggage(models.Model):
    """Model representing a piece of luggage."""

    luggage = models.ForeignKey(
        LuggageBill,
        related_name="items",
        on_delete=models.CASCADE,
        verbose_name=_("Luggage"),
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
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

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
