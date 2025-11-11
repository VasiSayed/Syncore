# core/admin.py
from django.contrib import admin, messages
from django.utils.html import format_html, mark_safe
from django.db import transaction
from django.forms import Textarea
from django.db import models as dj_models
from .models import SocialMedia


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


from django.utils.html import format_html
from .models import Transform

@admin.register(Transform)
class TransformAdmin(admin.ModelAdmin):
    list_display = ("heading", "is_active", "button_text", "link", "updated_at")
    list_filter  = ("is_active", "updated_at")
    search_fields = ("heading", "body_text")
    readonly_fields = ("image_preview",)
    fields = ("heading", "body_text", "image", "image_preview", "link", "button_text", "is_active")
    actions = ["make_active"]

    def image_preview(self, obj):
        if getattr(obj, "image", None):
            try:
                return format_html('<img src="{}" style="max-height:120px;border-radius:10px;">', obj.image.url)
            except Exception:
                pass
        return "—"
    image_preview.short_description = "Preview"

    @admin.action(description="Make selected Transform ACTIVE (others become inactive)")
    def make_active(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Select exactly one row to activate.", level=messages.WARNING)
            return
        obj = queryset.first()
        with transaction.atomic():
            Transform.objects.filter(is_active=True).exclude(pk=obj.pk).update(is_active=False)
            obj.is_active = True
            obj.save(update_fields=["is_active"])
        self.message_user(request, f"‘{obj.heading}’ is now the active Transform.", level=messages.SUCCESS)




@admin.register(SocialMedia)
class SocialMediaAdmin(admin.ModelAdmin):
    list_display = ("id", "preview", "link_tag", "order", "updated_at")
    list_editable = ("order",)
    search_fields = ("link",)
    ordering = ("order", "id")
    save_on_top = True

    readonly_fields = ("preview_large", "created_at", "updated_at")
    fields = ("image", "link", "order", "preview_large", "created_at", "updated_at")

    def link_tag(self, obj):
        return format_html('<a href="{0}" target="_blank" rel="noopener">{0}</a>', obj.link)
    link_tag.short_description = "Link"

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:40px;height:40px;object-fit:contain;border-radius:6px" />',
                obj.image.url,
            )
        return "—"
    preview.short_description = "Icon"

    def preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:200px;height:80px;object-fit:contain;border-radius:8px;border:1px solid #eee;padding:4px;background:#fff" />',
                obj.image.url,
            )
        return "—"
    preview_large.short_description = "Preview"


