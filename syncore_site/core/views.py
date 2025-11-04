from django.shortcuts import render,redirect
from .models import HomeBanner, StaticMetric, Service, ProvenResult, TrustedBy, ContactInfo
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.utils.html import strip_tags
from .forms import VisitorInfoForm
from .models import ContactInfo
from math import ceil

def home(request):
    banner = HomeBanner.objects.filter(is_active=True).first()
    video_name = (banner.video.name if getattr(banner, "video", None) else "")
    video_lower = video_name.lower() if video_name else ""
    banner_is_gif = video_lower.endswith(".gif")
    banner_is_mp4  = video_lower.endswith(".mp4")

    logos_all = list(TrustedBy.objects.all().order_by("id"))
    n = len(logos_all)
    half = ceil(n / 2) if n else 0
    logos_top = logos_all[:half]
    logos_bottom = logos_all[half:]

    ctx = {
        "banner": banner,
        "banner_is_gif": banner_is_gif,
        "banner_is_mp4": banner_is_mp4,

        "metrics": StaticMetric.objects.all(),
        "services": Service.objects.all(),
        "results": ProvenResult.objects.all(),

        "logos": logos_all,
        "logos_top": logos_top,
        "logos_bottom": logos_bottom,

        "contact": ContactInfo.objects.first(),
    }
    return render(request, "core/home.html", ctx)

def _client_ip(request):
    # tolerate proxies
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")



def contact_form_view(request):
    contact = ContactInfo.objects.first()

    if request.method == "POST":
        form = VisitorInfoForm(request.POST)
        if form.is_valid():
            visitor = form.save(commit=False)
            visitor.ip_address = _client_ip(request)
            visitor.save()

            # ----- addresses -----
            owner_email = (
                contact.email if contact and contact.email
                else getattr(settings, "DEFAULT_FROM_EMAIL", None)
            )
            default_from = getattr(settings, "DEFAULT_FROM_EMAIL", owner_email)

            # ----- common formatting helpers -----
            visit_date_str = visitor.visit_date.strftime("%d %b %Y") if visitor.visit_date else "-"

            # ===== 1) OWNER NOTIFICATION (full info, reply-to = visitor) =====
            if owner_email:
                owner_subject = f"New inquiry from {visitor.full_name}"
                owner_body_lines = [
                    "You have a new contact inquiry:",
                    "",
                    f"Name           : {visitor.full_name}",
                    f"Email          : {visitor.email}",
                    f"Phone          : {visitor.phone or '-'}",
                    f"Visit Date     : {visit_date_str}",
                    f"Company        : {visitor.company_name or '-'}",
                    f"Service        : {visitor.interest_service or '-'}",
                    "Message        :",
                    f"{(visitor.message or '-').strip()}",
                    "",
                    f"IP Address     : {visitor.ip_address or '-'}",
                ]
                owner_body = "\n".join(owner_body_lines)

                msg = EmailMessage(
                    subject=owner_subject,
                    body=owner_body,
                    from_email=default_from,
                    to=[owner_email],
                    reply_to=[visitor.email] if visitor.email else None,
                )
                try:
                    msg.send(fail_silently=True)
                except Exception:
                    pass

            # ===== 2) VISITOR ACK (includes interest, date, and their message) =====
            if default_from and visitor.email:
                visitor_subject = "Thanks for contacting SynCore"
                visitor_body_lines = [
                    f"Hi {visitor.full_name},",
                    "",
                    "Thanks for reaching out! We’ve received your request with the details below.",
                    "",
                    "— Your Request —",
                    f"Service Interested : {visitor.interest_service or '-'}",
                    f"Preferred Date     : {visit_date_str}",
                    f"Phone              : {visitor.phone or '-'}",
                    f"Company            : {visitor.company_name or '-'}",
                    "Message            :",
                    f"{(visitor.message or '-').strip()}",
                    "",
                    "We’ll get back to you shortly.",
                    "",
                    "— SynCore Team",
                ]
                visitor_body = "\n".join(visitor_body_lines)

                try:
                    send_mail(
                        subject=visitor_subject,
                        message=visitor_body,
                        from_email=default_from,
                        recipient_list=[visitor.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass

            messages.success(request, "Thanks! Your request was submitted.")
            return redirect("home")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = VisitorInfoForm()

    return render(request, "core/contact_form.html", {"form": form, "contact": contact})


