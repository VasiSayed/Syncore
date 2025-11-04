from django.contrib import admin
from . import models
from .models import HomeBanner , Service

admin.site.register(HomeBanner)

from django.contrib import admin
from .models import VisitorInfo
@admin.register(VisitorInfo)
class VisitorInfoAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "visit_date", "interest_service", "created_at")
    search_fields = ("full_name", "email", "company_name", "interest_service")
    list_filter = ("visit_date", "created_at")



@admin.register(models.StaticMetric)
class StaticMetricAdmin(admin.ModelAdmin):
    list_display = ("title", "count", "unit", "order")
    list_editable = ("order",)

# core/admin.py
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "link")
    list_editable = ("order",)
    fields = ("title", "link", "order", "icon_class", "icon_svg")
    help_texts = {
        "icon_class": "Example: fa-solid fa-gear (Font Awesome) or bi-gear (Bootstrap Icons)",
        "icon_svg": "Paste raw <svg>…</svg> markup",
    }


@admin.register(models.ProvenResult)
class ProvenResultAdmin(admin.ModelAdmin):
    list_display = ("id", "order")
    list_editable = ("order",)

@admin.register(models.TrustedBy)
class TrustedByAdmin(admin.ModelAdmin):
    list_display = ("id", "order")
    list_editable = ("order",)

@admin.register(models.ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ("name", "email")
