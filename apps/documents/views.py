"""
MwohaOS Documents Views — Milestone 1: Secure Document Management
Authenticates ownership, protects against unauthorized downloads, and provides isolated uploads.
"""
import mimetypes
import os
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from apps.profiles.models import Profile
from .forms import DocumentUploadForm
from .models import Document


def get_user_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


@login_required
def document_list_view(request):
    """
    List user's uploaded professional documents with filtering by type.
    Enforces ownership: only documents owned by request.user.profile are queried.
    """
    profile = get_user_profile(request.user)
    doc_type = request.GET.get("type", "")
    query = request.GET.get("q", "").strip()

    docs = Document.objects.filter(profile=profile)
    if doc_type:
        docs = docs.filter(document_type=doc_type)
    if query:
        docs = docs.filter(title__icontains=query)

    form = DocumentUploadForm()
    context = {
        "profile": profile,
        "documents": docs,
        "form": form,
        "selected_type": doc_type,
        "query": query,
        "doc_types": Document.DocumentType.choices,
    }
    return render(request, "documents/list.html", context)


@login_required
def document_upload_view(request):
    """
    Handles secure document uploads with server-side validation.
    """
    profile = get_user_profile(request.user)
    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.profile = profile
            doc.save()
            messages.success(request, f"Document '{doc.title}' uploaded successfully.")
            return redirect("documents:list")
        else:
            messages.error(request, "Please fix the errors below to upload your document.")
    else:
        form = DocumentUploadForm()

    return render(request, "documents/upload.html", {"form": form, "profile": profile})


@login_required
def document_download_view(request, pk: int):
    """
    Secure file delivery endpoint with strict ownership check.
    Prevents User B from downloading User A's uploaded documents.
    """
    profile = get_user_profile(request.user)
    # Strict ownership check: Must belong to request.user's profile
    document = get_object_or_404(Document, pk=pk, profile=profile)

    if not document.file:
        raise Http404("Document file not found.")

    try:
        file_path = document.file.path
        if not os.path.exists(file_path):
            raise Http404("Physical file missing from storage.")

        # Determine MIME type safely
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = "application/octet-stream"

        filename = os.path.basename(document.file.name)
        response = FileResponse(open(file_path, "rb"), content_type=content_type)
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        return response
    except Exception as e:
        raise Http404("Error reading file.")


@login_required
@require_POST
def document_delete_view(request, pk: int):
    """
    Delete document with ownership validation.
    """
    profile = get_user_profile(request.user)
    document = get_object_or_404(Document, pk=pk, profile=profile)
    title = document.title
    # Delete physical file
    if document.file:
        document.file.delete(save=False)
    document.delete()
    messages.success(request, f"Document '{title}' was deleted.")
    return redirect("documents:list")
