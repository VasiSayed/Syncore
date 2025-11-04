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


from django.contrib import admin, messages
from django.db import transaction
from .models import FaceCompany, AboutUsStatic

@admin.register(FaceCompany)
class FaceCompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "position", "is_founder")
    list_filter = ("is_founder",)
    search_fields = ("name", "position")

@admin.register(AboutUsStatic)
class AboutUsStaticAdmin(admin.ModelAdmin):
    list_display = ("id", "is_active", "updated_at",
                    "stat_clients_percent", "stat_revenue_millions",
                    "stat_businesses", "stat_years")
    list_filter = ("is_active",)
    actions = ["make_active"]

    @admin.action(description="Make selected record ACTIVE (others become inactive)")
    def make_active(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Select exactly one record.", level=messages.WARNING)
            return
        obj = queryset.first()
        with transaction.atomic():
            AboutUsStatic.objects.filter(is_active=True).update(is_active=False)
            obj.is_active = True
            obj.save(update_fields=["is_active"])
        self.message_user(request, "Active record updated.", level=messages.SUCCESS)

