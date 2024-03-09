from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

User = settings.AUTH_USER_MODEL


class Customer(models.Model):
    fullname = models.CharField(
        _("fullname"),
        max_length=150,
        unique=True,
    )
    email = models.EmailField(
        _("email address"),
    )
    address = models.CharField(
        _("address"),
        max_length=100,
    )
    next_of_kin = models.CharField(
        _("next of kin"),
        max_length=150,
    )
    next_of_kin_phonenumber = models.CharField(
        _("next of kin phonenumber"),
        max_length=11,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["fullname"]
        verbose_name = _("customer")
        verbose_name_plural = _("customers")

    def __str__(self):
        """Return a string representation of the Customer model"""
        return self.fullname


class Bus(models.Model):
    plate_number = models.CharField(
        _("plate number"),
        max_length=20,
        unique=True,
    )
    driver_name = models.CharField(
        _("Driver's name"),
        max_length=150,
    )
    max_luggage_weight = models.PositiveIntegerField(
        _("maximum luggage weight"),
        blank=True,
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created"]
        verbose_name = _("bus")
        verbose_name_plural = _("buses")

    def __str__(self):
        """Return a string representation of the Bus model"""
        return self.plate_number


class State(models.Model):
    name = models.CharField(
        _("name"),
        max_length=20,
    )
    short_code = models.CharField(
        _("short code"),
        max_length=3,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created"]
        verbose_name = _("state")
        verbose_name_plural = _("states")

    def __str__(self):
        """Return a string representation of the State model"""
        return self.name


class ParkLocation(models.Model):
    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        verbose_name=_("state"),
    )
    location = models.CharField(
        _("location"),
        max_length=50,
    )
    full_address = models.CharField(
        _("full address"),
        max_length=255,
    )
    contact = models.TextField(
        _("contact"),
    )

    class Meta:
        ordering = ["state"]
        verbose_name = _("park location")
        verbose_name_plural = _("park locations")

    def __str__(self):
        """Return a string representation of the ParkLocation model"""
        return self.location


class Weight(models.Model):
    name = models.CharField(
        _("name"),
        max_length=20,
    )
    min_weight = models.PositiveIntegerField(
        _("minimum weight"),
    )
    price = models.DecimalField(
        _("price"),
        max_digits=10,
        decimal_places=2,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created"]
        verbose_name = _("weight")
        verbose_name_plural = _("weights")

    def __str__(self):
        """Return a string representation of the Weight model"""
        return self.name


class BagType(models.Model):

    class SizeOption(models.TextChoices):
        SMALL = "S", _("Small")
        MEDIUM = "M", _("Medium")
        LARGE = "L", _("Large")

    name = models.CharField(
        _("name"),
        max_length=50,
    )
    size = models.CharField(
        _("size"),
        max_length=1,
        choices=SizeOption.choices,
    )
    description = models.TextField(
        _("description"),
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = _("bag type")
        verbose_name_plural = _("bag types")

    def __str__(self):
        """Return a string representation of the BagType model"""
        return f"{self.name} - {self.size}"


class Trip(models.Model):
    name = models.CharField(
        _("trip"),
        max_length=50,
        unique=True,
        help_text="format: ENU-to-LAG-01-01-2000",
    )
    bus = models.ForeignKey(
        Bus,
        on_delete=models.CASCADE,
        verbose_name=_("bus"),
    )
    departure = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name="departure",
        verbose_name=_("departure"),
    )
    destination = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name="arrival",
        verbose_name=_("destination"),
    )
    date_of_journey = models.DateTimeField(
        _("date of journey"),
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return a string representation of the Trip model"""
        return self.name

    def total_luggage_amount(self):
        return sum(
            luggagebill.total_amount() for luggagebill in self.luggagebill_set.all()
        )


class LuggageBill(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        verbose_name=_("customer"),
    )
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        verbose_name=_("trip"),
    )
    added_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("added by"),
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = _("luggage bill")
        verbose_name_plural = _("luggage bills")

    def __str__(self):
        """Return a string representation of the LuggageBill model"""
        return f"Luggage Bill for {self.customer}"

    def total_amount(self):
        return sum(item.amount() for item in self.items.all())

    def total_weight_per_customer(self):
        return sum(item.weight.min_weight for item in self.items.all())


class Luggage(models.Model):
    luggage = models.ForeignKey(
        LuggageBill,
        related_name="items",
        on_delete=models.CASCADE,
        verbose_name=_("luggage"),
    )
    weight = models.ForeignKey(
        Weight,
        on_delete=models.CASCADE,
        verbose_name=_("weight"),
    )
    bag_type = models.ForeignKey(
        BagType,
        on_delete=models.CASCADE,
        verbose_name=_("bag type"),
    )
    quantity = models.PositiveIntegerField(
        _("quantity"),
        default=1,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = _("luggage")
        verbose_name_plural = _("luggages")

    def __str__(self):
        """Return a string representation of the Luggage model"""
        return str(self.id)

    def amount(self):
        return self.weight.price * self.quantity
