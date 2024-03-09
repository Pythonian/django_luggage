import csv
import datetime
from django.http import HttpResponse
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse


from .models import (
    BagType,
    Bus,
    LuggageBill,
    Luggage,
    Customer,
    State,
    ParkLocation,
    Weight,
    Trip,
)


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    content_disposition = f"attachment; filename={opts.verbose_name}.csv"
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = content_disposition
    writer = csv.writer(response)
    fields = [
        field
        for field in opts.get_fields()
        if not field.many_to_many and not field.one_to_many
    ]
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
    pass


@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ["plate_number", "driver_name"]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        "fullname",
        "email",
        "address",
        "next_of_kin",
        "next_of_kin_phonenumber",
        "created",
        customer_detail,
    ]
    search_fields = ["fullname", "email", "next_of_kin"]


class ParkLocationInline(admin.StackedInline):
    model = ParkLocation
    extra = 1


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ["name", "short_code"]
    inlines = [ParkLocationInline]


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
    list_filter = ["date_of_journey", "bus", "departure", "destination"]
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
    list_filter = ["trip__bus__plate_number", "trip__name", "created"]
    search_fields = ["customer", "trip"]
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

    def save_model(self, request, obj, form, change):
        """
        Override this method to save the current user when record is created.
        """
        # check to ensure this is a record that hasn't been saved
        if getattr(obj, "added_by", None) is None:
            obj.added_by = request.user
        obj.last_modified_by = request.user
        obj.save()
