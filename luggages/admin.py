import csv
import datetime

from django.contrib import admin
from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
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


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    content_disposition = f"attachment; filename={opts.verbose_name}.csv"
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = content_disposition
    writer = csv.writer(response)
    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    # Write a first row with header information
    writer.writerow([field.verbose_name for field in fields])
    # Write data rows
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime("%d/%m/%Y")
            data_row.append(value)
        writer.writerow(data_row)
    return response


export_to_csv.short_description = "Export selected bills to CSV"


def luggage_receipt(obj):
    url = reverse("admin_luggagebill_detail", args=[obj.id])
    return mark_safe(f'<a href="{url}">View</a>')


def customer_detail(obj):
    url = reverse("admin_customer_detail", args=[obj.id])
    return mark_safe(f'<a href="{url}">View</a>')


def trip_luggages(obj):
    url = reverse("admin_trip_luggages", args=[obj.id])
    return mark_safe(f'<a href="{url}">View</a>')


@admin.register(BagType)
class BagTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "size"]
    search_fields = ["name"]


class TripInlineBus(admin.TabularInline):
    model = Trip
    extra = 1
    readonly_fields = [
        "name",
        "departure",
        "destination",
        "date_of_journey",
    ]

    def has_delete_permission(self, request, obj=None):
        """Determine whether the user has permission to delete Trip instances.

        Args:
            request: The current request.
            obj (optional): The object being edited.

        Returns:
            bool: True if the user has permission to delete, False otherwise.
        """
        return False

    def has_add_permission(self, request, obj=None):
        """Determine whether the user has permission to add new Trip instances.

        Args:
            request: The current request.
            obj (optional): The object being edited.

        Returns:
            bool: True if the user has permission to add, False otherwise.
        """
        return False


@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ["plate_number", "driver_name"]
    search_fields = ["plate_number", "driver_name"]
    inlines = [TripInlineBus]


class TripInlineLocation(admin.TabularInline):
    model = Trip
    extra = 1
    readonly_fields = [
        "name",
        "departure",
        "destination",
        "date_of_journey",
    ]
    fk_name = "departure"

    def has_delete_permission(self, request, obj=None):
        """Determine whether the user has permission to delete Trip instances.

        Args:
            request: The current request.
            obj (optional): The object being edited.

        Returns:
            bool: True if the user has permission to delete, False otherwise.
        """
        return False

    def has_add_permission(self, request, obj=None):
        """Determine whether the user has permission to add new Trip instances.

        Args:
            request: The current request.
            obj (optional): The object being edited.

        Returns:
            bool: True if the user has permission to add, False otherwise.
        """
        return False


@admin.register(ParkLocation)
class ParkLocationAdmin(admin.ModelAdmin):
    list_display = ["location", "state", "full_address"]
    list_filter = ["state"]
    search_fields = ["full_address", "location"]
    inlines = [TripInlineLocation]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        "fullname",
        "email",
        "address",
        "next_of_kin",
        "next_of_kin_phonenumber",
        customer_detail,
    ]
    search_fields = ["fullname", "next_of_kin"]


class ParkLocationInline(admin.StackedInline):
    model = ParkLocation
    extra = 1


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ["name", "short_code", "park_locations_count"]
    inlines = [ParkLocationInline]

    def park_locations_count(self, obj):
        return obj.parklocation_set.count()

    park_locations_count.short_description = "Number of Park Locations"
    park_locations_count.admin_order_field = "parklocation_set__count"


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "bus",
        "departure",
        "destination",
        "date_of_journey",
        trip_luggages,
    ]
    list_filter = ["date_of_journey"]
    search_fields = [
        "departure__location",
        "destination__location",
        "bus__plate_number",
        "name",
    ]
    date_hierarchy = "date_of_journey"


@admin.register(Weight)
class WeightAdmin(admin.ModelAdmin):
    list_display = ["name", "min_weight", "price"]


class LuggageInline(admin.TabularInline):
    model = Luggage
    extra = 1


@admin.register(LuggageBill)
class LuggageBillAdmin(admin.ModelAdmin):
    list_display = ["customer", "trip", "created", luggage_receipt]
    list_filter = ["created"]
    search_fields = ["customer__fullname", "trip__name", "trip__bus__plate_number"]
    date_hierarchy = "created"
    inlines = [LuggageInline]
    actions = [export_to_csv]

    def queryset(self, request):
        # override queryset returned by list page to only
        # return bills created by logged in staff
        qs = super().queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(added_by=request.user)

    def get_form(self, request, obj=None, **kwargs):
        # Exclude the 'added_by' field from the form
        exclude = ["added_by"]
        kwargs["exclude"] = exclude
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        # Set the added_by field to the currently logged-in admin user
        # check to ensure this is a record that hasn't been saved
        if getattr(obj, "added_by", None) is None:
            obj.added_by = request.user
        super().save_model(request, obj, form, change)


admin.site.unregister(Group)
