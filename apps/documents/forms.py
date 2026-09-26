"""
MwohaOS Documents Forms — Milestone 1: Secure File Uploads
"""
from django import forms
from .models import Document


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = [
            "title",
            "document_type",
            "file",
            "version",
            "is_primary",
            "description",
        ]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500",
                "placeholder": "e.g. Master Curriculum Vitae (2026)",
            }),
            "document_type": forms.Select(attrs={
                "class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500",
            }),
            "file": forms.FileInput(attrs={
                "class": "w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100",
            }),
            "version": forms.TextInput(attrs={
                "class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500",
                "placeholder": "1.0 or 2026-v1",
            }),
            "is_primary": forms.CheckboxInput(attrs={
                "class": "rounded border-slate-300 text-blue-600 focus:ring-blue-500",
            }),
            "description": forms.Textarea(attrs={
                "rows": 2,
                "class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500",
                "placeholder": "Context or special revisions in this document...",
            }),
        }
