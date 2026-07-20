from django import forms
from django.contrib.auth import get_user_model
from .models import Project, Decision, Attachment

User = get_user_model()


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["title", "description"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control rounded-3",
                "placeholder": "e.g., Q3 Cloud Infrastructure Migration",
                "required": True
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control rounded-3",
                "rows": 3,
                "placeholder": "Describe the scope and objectives of this project workspace..."
            }),
        }


class DecisionForm(forms.ModelForm):
    class Meta:
        model = Decision
        fields = ["title", "description", "category", "risk_level", "priority", "status", "impact_score"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control rounded-3",
                "placeholder": "e.g., Evaluate AWS vs Azure multi-cloud architecture",
                "required": True
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control rounded-3",
                "rows": 5,
                "placeholder": "Provide detailed decision context, evaluation criteria, and trade-offs...",
                "required": True
            }),
            "category": forms.Select(attrs={
                "class": "form-select rounded-3"
            }),
            "risk_level": forms.Select(attrs={
                "class": "form-select rounded-3"
            }),
            "priority": forms.Select(attrs={
                "class": "form-select rounded-3"
            }),
            "status": forms.Select(attrs={
                "class": "form-select rounded-3"
            }),
            "impact_score": forms.NumberInput(attrs={
                "class": "form-control rounded-3",
                "min": 1,
                "max": 100,
                "placeholder": "Score 1-100"
            }),
        }


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ["file"]
        widgets = {
            "file": forms.FileInput(attrs={
                "class": "form-control rounded-3",
                "accept": ".pdf,image/*,.png,.jpg,.jpeg,.doc,.docx"
            })
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control rounded-3"}),
            "first_name": forms.TextInput(attrs={"class": "form-control rounded-3"}),
            "last_name": forms.TextInput(attrs={"class": "form-control rounded-3"}),
        }
