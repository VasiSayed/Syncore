# core/forms.py
from django import forms
from .models import VisitorInfo

class VisitorInfoForm(forms.ModelForm):
    class Meta:
        model = VisitorInfo
        fields = ["full_name", "email", "phone", "visit_date",
                  "company_name", "interest_service", "message"]
        widgets = {
            "full_name": forms.TextInput(attrs={
                "placeholder": "Jane Smith", "class": "form-control"}),
            "email": forms.EmailInput(attrs={
                "placeholder": "jane@framer.com", "class": "form-control"}),
            "phone": forms.TextInput(attrs={
                "placeholder": "+123 476 9789", "class": "form-control"}),
            "visit_date": forms.DateInput(attrs={
                "type": "date", "class": "form-control"}),
            "company_name": forms.TextInput(attrs={
                "placeholder": "Company Name", "class": "form-control"}),
            "interest_service": forms.TextInput(attrs={
                "placeholder": "Select / type...", "class": "form-control"}),
            "message": forms.Textarea(attrs={
                "rows": 5, "placeholder": "How can we help?", "class": "form-control"}),
        }
