from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True


class HomeBanner(models.Model):
    video = models.FileField(upload_to="banners/", help_text="MP4 recommended")
    is_active = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["is_active"],           
                condition=Q(is_active=True),    
                name="unique_active_home_banner",
            )
        ]
        verbose_name = "Home Banner"
        verbose_name_plural = "Home Banners"

    def __str__(self):
        return f"Banner #{self.pk} ({'ACTIVE' if self.is_active else 'inactive'})"


class StaticMetric(TimeStamped):
    UNIT_CHOICES = [
        ("CR", "Cr"), ("LAKH", "Lakh"),
        ("THOUSAND", "Thousand"), ("HUNDRED", "Hundred"), ("NONE", ""),
    ]
    title = models.CharField(max_length=120)
    count = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default="NONE")
    image = models.ImageField(upload_to="static_metrics/", blank=True, null=True)  # optional right-side photo
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Static"
        verbose_name_plural = "Statics"

    def __str__(self): return self.title


class Service(TimeStamped):
    icon_class = models.CharField(
        max_length=120, blank=True,null=True,
        help_text="e.g. 'fa-solid fa-gear' or 'bi-gear'"
    )
    icon_svg = models.TextField(
        blank=True,null=True,
        help_text="Paste inline SVG markup starting with <svg …>"
    )
    title = models.CharField(max_length=100)
    link = models.URLField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def clean(self):
        if not self.icon_class and not self.icon_svg:
            raise ValidationError("Provide either icon_class or icon_svg.")
        if self.icon_class and self.icon_svg:
            raise ValidationError("Use only one: icon_class OR icon_svg.")

    def __str__(self):
        return self.title


class ProvenResult(TimeStamped):
    image = models.ImageField(upload_to="proven_results/")
    title=models.CharField(max_length=200,null=True,blank=True)
    description = models.TextField()
    link = models.URLField(blank=True, null=True)
    link_text = models.CharField(max_length=60, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self): return f"Proven Result #{self.pk}"


class TrustedBy(TimeStamped):
    logo = models.ImageField(upload_to="trusted_by/")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Trusted By"
        verbose_name_plural = "Trusted By"

    def __str__(self): return f"Logo #{self.pk}"


class ContactInfo(TimeStamped):
    name = models.CharField(max_length=120)
    video = models.FileField(upload_to="Contact/", help_text="MP4 recommended",blank=True,null=True)
    phone_number=models.BigIntegerField(MinValueValidator(0),null=True,blank=True)
    address=models.CharField(max_length=200,null=True,blank=True)
    email = models.EmailField()

    def __str__(self): return f"{self.name} <{self.email}>"


class VisitorInfo(models.Model):
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    visit_date = models.DateField(null=True, blank=True)
    company_name = models.CharField(max_length=150, blank=True)
    interest_service = models.CharField(max_length=150, blank=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = "visitor_info"  

    def __str__(self):
        return f"{self.full_name} <{self.email}>"

