# syncore_site/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from core.views import home,contact_form_view,about_page

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("contact/", contact_form_view, name="contact"),
    path("about/", about_page, name="about"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


