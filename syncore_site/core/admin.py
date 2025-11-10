# core/admin.py
from django.contrib import admin, messages
from django.utils.html import format_html, mark_safe
from django.db import transaction
from django.forms import Textarea
from django.db import models as dj_models

from .models import (
    HomeBanner,
    VisitorInfo,
    StaticMetric,
    Service,
    ProvenResult,
    TrustedBy,
    ContactInfo,
    FaceCompany,
    AboutUsStatic,
    ApproachSection,
    ApproachStep,
)

admin.site.register(HomeBanner)

@admin.register(VisitorInfo)
class VisitorInfoAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "visit_date", "interest_service", "created_at")
    search_fields = ("full_name", "email", "company_name", "interest_service")
    list_filter = ("visit_date", "created_at")


@admin.register(StaticMetric)
class StaticMetricAdmin(admin.ModelAdmin):
    list_display = ("title", "count", "unit", "order")
    list_editable = ("order",)
    list_display_links = ("title",)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "icon_preview")
    list_display_links = ("title",)
    list_editable = ("order",)
    readonly_fields = ("icon_preview",)
    fields = ("title", "link", "order", "icon", "icon_class", "icon_svg", "icon_preview")

    def icon_preview(self, obj):
        if getattr(obj, "icon", None):
            try:
                return format_html('<img src="{}" style="height:40px;border-radius:6px" />', obj.icon.url)
            except Exception:
                pass
        if obj.icon_svg:
            return mark_safe(obj.icon_svg)
        if obj.icon_class:
            return format_html('<i class="{}" style="font-size:28px"></i>', obj.icon_class)
        return "—"
    icon_preview.short_description = "Preview"


@admin.register(ProvenResult)
class ProvenResultAdmin(admin.ModelAdmin):
    list_display = ("id", "order")
    list_editable = ("order",)


@admin.register(TrustedBy)
class TrustedByAdmin(admin.ModelAdmin):
    list_display = ("id", "order")
    list_editable = ("order",)


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ("name", "email")


@admin.register(FaceCompany)
class FaceCompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "position", "is_founder", "founder_year", "consulting_engagements")
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


# ---- Approach (Inline + its own page) ----

class ApproachStepInline(admin.StackedInline):
    model = ApproachStep
    extra = 0
    ordering = ("order",)
    readonly_fields = ("icon_preview",)

    fieldsets = (
        ("Order & Title", {
            "fields": ("order", "title"),
        }),
        ("Icon", {
            "fields": ("icon", "icon_class", "icon_svg", "icon_preview"),
            "description": "Provide exactly one of icon / icon_class / icon_svg."
        }),
        ("Content", {
            "fields": ("body", "body_secondary"),
        }),
    )

    # Make textareas comfortable
    formfield_overrides = {
        dj_models.TextField: {"widget": Textarea(attrs={"rows": 3, "style": "width:100%;"})},
    }

    def icon_preview(self, obj):
        if not obj or not getattr(obj, "pk", None):
            return "—"
        if obj.icon:
            try:
                return format_html('<img src="{}" style="height:28px;border-radius:6px" />', obj.icon.url)
            except Exception:
                pass
        if obj.icon_svg:
            return mark_safe(obj.icon_svg)
        if obj.icon_class:
            return format_html('<i class="{}" style="font-size:22px"></i>', obj.icon_class)
        return "—"
    icon_preview.short_description = "Preview"


@admin.register(ApproachSection)
class ApproachSectionAdmin(admin.ModelAdmin):
    list_display = ("id", "is_active", "updated_at")
    list_filter = ("is_active",)
    actions = ["make_active"]
    fields = ("heading", "image", "is_active")
    inlines = [ApproachStepInline]

    @admin.action(description="Make selected section ACTIVE (others become inactive)")
    def make_active(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Select exactly one section.", level=messages.WARNING)
            return
        obj = queryset.first()
        with transaction.atomic():
            ApproachSection.objects.filter(is_active=True).update(is_active=False)
            obj.is_active = True
            obj.save(update_fields=["is_active"])
        self.message_user(request, "Active approach section updated.", level=messages.SUCCESS)


@admin.register(ApproachStep)
class ApproachStepAdmin(admin.ModelAdmin):
    """Separate changelist for steps (optional but handy)."""
    list_display = ("title", "section", "order", "updated_at")
    list_filter = ("section",)
    search_fields = ("title", "body", "body_secondary")
    ordering = ("section", "order")
    readonly_fields = ("icon_preview",)

    fieldsets = (
        ("Belongs To", {"fields": ("section",)}),
        ("Order & Title", {"fields": ("order", "title")}),
        ("Icon", {"fields": ("icon", "icon_class", "icon_svg", "icon_preview")}),
        ("Content", {"fields": ("body", "body_secondary")}),
    )

    formfield_overrides = {
        dj_models.TextField: {"widget": Textarea(attrs={"rows": 5, "style": "width:100%;"})},
    }

    def icon_preview(self, obj):
        if obj.icon:
            try:
                return format_html('<img src="{}" style="height:28px;border-radius:6px" />', obj.icon.url)
            except Exception:
                pass
        if obj.icon_svg:
            return mark_safe(obj.icon_svg)
        if obj.icon_class:
            return format_html('<i class="{}" style="font-size:22px"></i>', obj.icon_class)
        return "—"
    icon_preview.short_description = "Preview"
