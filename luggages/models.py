from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Customer(models.Model):
    fullname = models.CharField(max_length=150, unique=True)
    email = models.EmailField()
    address = models.CharField(max_length=100, blank=True, null=True)
    next_of_kin = models.CharField(max_length=150)
    next_of_kin_phonenumber = models.CharField(max_length=11)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["fullname"]

    def __str__(self):
        return self.fullname


class Bus(models.Model):
    plate_number = models.CharField(max_length=20, unique=True)
    driver_name = models.CharField(max_length=150)
    max_luggage_weight = models.PositiveIntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created"]
        verbose_name_plural = "Buses"

    def __str__(self):
        return self.plate_number


class Destination(models.Model):
    name = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created"]

    def __str__(self):
        return self.name


class Weight(models.Model):
    name = models.CharField(max_length=20)
    min_weight = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created"]

    def __str__(self):
        return self.name


class BagType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Trip(models.Model):
    name = models.CharField(
        max_length=50, unique=True, help_text="format: ENU-to-LAG-01-01-2000"
    )
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    departure = models.ForeignKey(
        Destination, on_delete=models.CASCADE, related_name="departure"
    )
    destination = models.ForeignKey(
        Destination, on_delete=models.CASCADE, related_name="arrival"
    )
    date_of_journey = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def total_luggage_amount(self):
        return sum(
            luggagebill.total_amount() for luggagebill in self.luggagebill_set.all()
        )


class LuggageBill(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    added_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"Luggage Bill for {self.customer}"

    def total_amount(self):
        return sum(item.amount() for item in self.items.all())

    def total_weight_per_customer(self):
        return sum(item.weight.min_weight for item in self.items.all())


class Luggage(models.Model):
    luggage = models.ForeignKey(
        LuggageBill, related_name="items", on_delete=models.CASCADE
    )
    weight = models.ForeignKey(Weight, on_delete=models.CASCADE)
    bag_type = models.ForeignKey(BagType, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    def amount(self):
        return self.weight.price * self.quantity
