from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db.models import Max


class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True


class HomeBanner(models.Model):
    video = models.FileField(upload_to="banners/", help_text="MP4 recommended")
    is_active = models.BooleanField(default=False)
    service_image = models.ImageField(
        upload_to="serice_image/",
        blank=True, null=True,
        verbose_name="Service Image",  
        help_text="Upload a square PNG/SVG (raster) for the service icon."
    )

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
    icon = models.ImageField(
        upload_to="service_icons/",
        blank=True, null=True,
        verbose_name="Icon",  
        help_text="Upload a square PNG/SVG (raster) for the service icon."
    )

    icon_class = models.CharField(
        max_length=120, blank=True, null=True,
        help_text="e.g. 'fa-solid fa-gear' or 'bi-gear'"
    )
    icon_svg = models.TextField(
        blank=True, null=True,
        help_text="Paste inline SVG markup starting with <svg …>"
    )
    title = models.CharField(max_length=100)
    link = models.URLField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def clean(self):
        chosen = sum(bool(x) for x in [self.icon, self.icon_class, self.icon_svg])
        if chosen == 0:
            raise ValidationError("Provide one of: Icon image, icon_class or icon_svg.")
        if chosen > 1:
            raise ValidationError("Use only one: Icon image OR icon_class OR icon_svg.")

    def __str__(self):
        return self.title



class Transform(models.Model):
    heading = models.CharField(max_length=200)
    body_text = models.TextField()
    image = models.ImageField(upload_to="transform/", blank=True, null=True)
    link = models.URLField(blank=True)
    button_text = models.CharField(max_length=60, blank=True, default="Learn more")

    is_active = models.BooleanField(default=False)  # <-- only one True allowed

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["is_active"],
                condition=Q(is_active=True),
                name="uniq_active_transform"
            )
        ]

    def save(self, *args, **kwargs):
        if self.is_active:
            type(self).objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.heading


class ProvenResult(TimeStamped):
    image = models.ImageField(upload_to="proven_results/")
    title=models.CharField(max_length=400,null=True,blank=True)
    description = models.TextField()
    link = models.URLField(blank=True, null=True)
    link_text = models.CharField(max_length=60, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self): return f"Proven Result #{self.pk}"


class ApproachSection(models.Model):
    """
    One record represents the 'About / Our Approach' section:
    - a big left image
    - the heading text above it
    - an active flag (use only 1 active)
    """
    heading = models.TextField(
        help_text="Main heading above the section. Use plain text; <br> will be inserted on line breaks."
    )
    image = models.ImageField(
        upload_to="approach/",
        blank=True, null=True,
        help_text="Large left image."
    )
    is_active = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ApproachSection #{self.pk} ({'ACTIVE' if self.is_active else 'inactive'})"

    class Meta:
        verbose_name = "Approach Section"
        verbose_name_plural = "Approach Sections"


class ApproachStep(models.Model):
    """
    Right-side cards, ordered: Understand / Strategize / Implement / Measure
    """
    section = models.ForeignKey(
        ApproachSection,
        related_name="steps",
        on_delete=models.CASCADE
    )
    order = models.PositiveIntegerField(default=0)

    icon = models.ImageField(
        upload_to="approach/icons/",
        blank=True, null=True,
        help_text="Upload small square image for the step icon."
    )
    icon_class = models.CharField(
        max_length=120, blank=True, null=True,
        help_text="e.g. 'fa-solid fa-bolt' or 'bi-lightning-charge'"
    )
    icon_svg = models.TextField(
        blank=True, null=True,
        help_text="Paste inline SVG markup starting with <svg …>"
    )

    title = models.CharField(max_length=80)
    body = models.TextField(help_text="First paragraph.")
    body_secondary = models.TextField(blank=True, help_text="Optional second paragraph.")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.order:02d} · {self.title}"

    def clean(self):
        chosen = sum(bool(x) for x in [self.icon, self.icon_class, self.icon_svg])
        if chosen == 0:
            raise ValidationError("Provide one of: icon image, icon_class or icon_svg.")
        if chosen > 1:
            raise ValidationError("Use only one: icon image OR icon_class OR icon_svg.")


class TrustedBy(TimeStamped):
    logo = models.ImageField(upload_to="trusted_by/")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Trusted By"
        verbose_name_plural = "Trusted By"

    def __str__(self): return f"Logo #{self.pk}"


class ContactInfo(TimeStamped):
    name = models.CharField(max_length=120,null=True,blank=True)
    video = models.FileField(upload_to="Contact/", help_text="MP4 recommended",blank=True,null=True)
    phone_number=models.BigIntegerField(null=True,blank=True)
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


IMG_VALIDATOR = FileExtensionValidator(["jpg", "jpeg", "png", "webp"])



class FaceCompany(models.Model):
    image = models.ImageField(upload_to="faces/", validators=[IMG_VALIDATOR])
    name = models.CharField(max_length=120)
    position = models.CharField(max_length=120, blank=True)

    is_founder = models.BooleanField(default=False)
    founder_year = models.PositiveIntegerField(null=True, blank=True, help_text="e.g. 25 (years of experience)")
    consulting_engagements = models.PositiveIntegerField(
        null=True, blank=True, help_text="e.g. 75 (engagements)"
    )

    class Meta:
        ordering = ["-is_founder", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["is_founder"],
                condition=models.Q(is_founder=True),
                name="unique_true_founder_only",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({'Founder' if self.is_founder else self.position})"
    

class AboutUsStatic(models.Model):
    """
    Store copy + numbers; use images from DB; headings remain static in template.
    Only ONE row may be active at a time.
    """
    hero_page    = models.ImageField(upload_to="about/", validators=[IMG_VALIDATOR])
    mission_image= models.ImageField(upload_to="about/", validators=[IMG_VALIDATOR], blank=True, null=True)
    cta_image    = models.ImageField(upload_to="about/", validators=[IMG_VALIDATOR], blank=True, null=True)
    above_state_image = models.ImageField(upload_to="above_state_image/", validators=[IMG_VALIDATOR], blank=True, null=True)

    who_we_are_body = models.TextField()
    mission_body    = models.TextField()
    vision_line     = models.TextField()
    cta_body        = models.TextField()

    stat_clients_percent = models.IntegerField(default=92)   
    stat_revenue_millions = models.IntegerField(default=50)  
    stat_businesses       = models.IntegerField(default=100) 
    stat_years            = models.IntegerField(default=15)  

    updated_at = models.DateTimeField(auto_now=True)
    is_active  = models.BooleanField(default=False)

    class Meta:
        verbose_name = "About Us (Static Integers & Text)"
        verbose_name_plural = "About Us (Static Integers & Text)"
        constraints = [
            models.UniqueConstraint(
                fields=["is_active"],
                condition=models.Q(is_active=True),
                name="about_only_one_active",
            ),
        ]

    def __str__(self):
        return f"AboutUsStatic #{self.pk} (updated {self.updated_at:%Y-%m-%d})"




class SocialMedia(models.Model):
    image = models.ImageField(upload_to="socials/")
    link = models.URLField()
    order = models.PositiveIntegerField(default=0, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["order"], name="unique_socialmedia_order")
        ]

    def save(self, *args, **kwargs):
        if not self.order:
            max_order = SocialMedia.objects.aggregate(m=Max("order"))["m"] or 0
            self.order = max_order + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.link} (#{self.order})"

