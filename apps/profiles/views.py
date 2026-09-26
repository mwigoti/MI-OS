"""
MwohaOS Profiles Views — Milestone 1: Professional Profile & Evidence System
Complete CRUD views for Profile, Skills, Experience, Education, Projects,
Achievements, Certifications, Publications, Languages, Preferences, and Evidence.
Strict ownership enforcement throughout.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import (
    AchievementForm,
    CertificationForm,
    EducationForm,
    EvidenceForm,
    ExperienceForm,
    LanguageForm,
    ProfileForm,
    ProfilePreferenceForm,
    ProjectForm,
    PublicationForm,
    SkillForm,
)
from .models import (
    Achievement,
    Certification,
    Education,
    Evidence,
    Experience,
    Language,
    Profile,
    ProfilePreference,
    ProfileVersion,
    Project,
    Publication,
    Skill,
)
from .services.completeness import calculate_profile_completeness


def get_user_profile(user) -> Profile:
    """Helper to get or create the user's primary profile."""
    profile, created = Profile.objects.get_or_create(user=user)
    return profile


def record_profile_version(profile: Profile, change_summary: str):
    """Utility to increment and log a profile version snapshot."""
    last_ver = profile.versions.first()
    next_num = (last_ver.version + 1) if last_ver else 1
    ProfileVersion.objects.create(
        profile=profile,
        version=next_num,
        change_summary=change_summary[:250],
        snapshot_data={
            "headline": profile.headline,
            "location": profile.location,
            "skills_count": profile.skills.count(),
            "experience_count": profile.experiences.count(),
            "projects_count": profile.projects.count(),
        },
    )


# -----------------------------------------------------------------------------
# 1. OVERVIEW & BASE PROFILE
# -----------------------------------------------------------------------------

@login_required
def profile_overview(request):
    """
    Main Profile Dashboard: overview of professional identity, completeness metric,
    and summaries across all profile domains.
    """
    profile = get_user_profile(request.user)
    completeness = calculate_profile_completeness(profile)

    context = {
        "profile": profile,
        "completeness": completeness,
        "skills": profile.skills.all()[:10],
        "experiences": profile.experiences.all()[:5],
        "education_list": profile.education.all()[:3],
        "projects": profile.projects.all()[:5],
        "achievements": profile.achievements.all()[:3],
        "certifications": profile.certifications.all()[:3],
        "publications": profile.publications.all()[:3],
        "languages": profile.languages.all()[:5],
        "documents": profile.documents.all()[:5],
        "evidence_items": profile.evidence_items.all()[:5],
    }
    return render(request, "profiles/overview.html", context)


@login_required
def profile_edit(request):
    """Edit core identity, summary, and links."""
    profile = get_user_profile(request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            record_profile_version(profile, "Updated core identity and contact details")
            messages.success(request, "Professional profile updated.")
            return redirect("profiles:overview")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "profiles/profile_form.html", {"form": form, "profile": profile})


# -----------------------------------------------------------------------------
# 2. SKILLS
# -----------------------------------------------------------------------------

@login_required
def skill_list(request):
    profile = get_user_profile(request.user)
    skills = profile.skills.all()
    form = SkillForm()
    return render(request, "profiles/skills_list.html", {"profile": profile, "skills": skills, "form": form})


@login_required
def skill_create(request):
    profile = get_user_profile(request.user)
    if request.method == "POST":
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.profile = profile
            try:
                skill.save()
                messages.success(request, f"Skill '{skill.name}' added.")
            except Exception:
                messages.error(request, f"Skill '{skill.name}' already exists in your profile.")
            return redirect("profiles:skill_list")
    else:
        form = SkillForm()
    return render(request, "profiles/skill_form.html", {"form": form, "title": "Add Skill"})


@login_required
def skill_edit(request, pk: int):
    profile = get_user_profile(request.user)
    skill = get_object_or_404(Skill, pk=pk, profile=profile)
    if request.method == "POST":
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, f"Skill '{skill.name}' updated.")
            return redirect("profiles:skill_list")
    else:
        form = SkillForm(instance=skill)
    return render(request, "profiles/skill_form.html", {"form": form, "skill": skill, "title": "Edit Skill"})


@login_required
@require_POST
def skill_delete(request, pk: int):
    profile = get_user_profile(request.user)
    skill = get_object_or_404(Skill, pk=pk, profile=profile)
    name = skill.name
    skill.delete()
    messages.success(request, f"Skill '{name}' deleted.")
    return redirect("profiles:skill_list")


# -----------------------------------------------------------------------------
# 3. EXPERIENCE
# -----------------------------------------------------------------------------

@login_required
def experience_list(request):
    profile = get_user_profile(request.user)
    experiences = profile.experiences.all()
    return render(request, "profiles/experience_list.html", {"profile": profile, "experiences": experiences})


@login_required
def experience_create(request):
    profile = get_user_profile(request.user)
    if request.method == "POST":
        form = ExperienceForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.profile = profile
            exp.save()
            messages.success(request, f"Experience at {exp.organization} added.")
            return redirect("profiles:experience_list")
    else:
        form = ExperienceForm()
    return render(request, "profiles/experience_form.html", {"form": form, "title": "Add Experience"})


@login_required
def experience_edit(request, pk: int):
    profile = get_user_profile(request.user)
    exp = get_object_or_404(Experience, pk=pk, profile=profile)
    if request.method == "POST":
        form = ExperienceForm(request.POST, instance=exp)
        if form.is_valid():
            form.save()
            messages.success(request, f"Experience at {exp.organization} updated.")
            return redirect("profiles:experience_list")
    else:
        form = ExperienceForm(instance=exp)
    return render(request, "profiles/experience_form.html", {"form": form, "experience": exp, "title": "Edit Experience"})


@login_required
@require_POST
def experience_delete(request, pk: int):
    profile = get_user_profile(request.user)
    exp = get_object_or_404(Experience, pk=pk, profile=profile)
    org = exp.organization
    exp.delete()
    messages.success(request, f"Experience at {org} removed.")
    return redirect("profiles:experience_list")


# -----------------------------------------------------------------------------
# 4. EDUCATION
# -----------------------------------------------------------------------------

@login_required
def education_list(request):
    profile = get_user_profile(request.user)
    education_records = profile.education.all()
    return render(request, "profiles/education_list.html", {"profile": profile, "education_list": education_records})


@login_required
def education_create(request):
    profile = get_user_profile(request.user)
    if request.method == "POST":
        form = EducationForm(request.POST)
        if form.is_valid():
            edu = form.save(commit=False)
            edu.profile = profile
            edu.save()
            messages.success(request, f"Education at {edu.institution} added.")
            return redirect("profiles:education_list")
    else:
        form = EducationForm()
    return render(request, "profiles/education_form.html", {"form": form, "title": "Add Education"})


@login_required
def education_edit(request, pk: int):
    profile = get_user_profile(request.user)
    edu = get_object_or_404(Education, pk=pk, profile=profile)
    if request.method == "POST":
        form = EducationForm(request.POST, instance=edu)
        if form.is_valid():
            form.save()
            messages.success(request, f"Education at {edu.institution} updated.")
            return redirect("profiles:education_list")
    else:
        form = EducationForm(instance=edu)
    return render(request, "profiles/education_form.html", {"form": form, "education": edu, "title": "Edit Education"})


@login_required
@require_POST
def education_delete(request, pk: int):
    profile = get_user_profile(request.user)
    edu = get_object_or_404(Education, pk=pk, profile=profile)
    inst = edu.institution
    edu.delete()
    messages.success(request, f"Education at {inst} removed.")
    return redirect("profiles:education_list")


# -----------------------------------------------------------------------------
# 5. PROJECTS
# -----------------------------------------------------------------------------

@login_required
def project_list(request):
    profile = get_user_profile(request.user)
    category = request.GET.get("category", "")
    projects = profile.projects.all()
    if category:
        projects = projects.filter(category=category)
    return render(request, "profiles/project_list.html", {
        "profile": profile,
        "projects": projects,
        "categories": Project.Category.choices,
        "selected_category": category,
    })


@login_required
def project_create(request):
    profile = get_user_profile(request.user)
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            proj = form.save(commit=False)
            proj.profile = profile
            proj.save()
            messages.success(request, f"Project '{proj.name}' added.")
            return redirect("profiles:project_list")
    else:
        form = ProjectForm()
    return render(request, "profiles/project_form.html", {"form": form, "title": "Add Project"})


@login_required
def project_edit(request, pk: int):
    profile = get_user_profile(request.user)
    proj = get_object_or_404(Project, pk=pk, profile=profile)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=proj)
        if form.is_valid():
            form.save()
            messages.success(request, f"Project '{proj.name}' updated.")
            return redirect("profiles:project_list")
    else:
        form = ProjectForm(instance=proj)
    return render(request, "profiles/project_form.html", {"form": form, "project": proj, "title": "Edit Project"})


@login_required
@require_POST
def project_delete(request, pk: int):
    profile = get_user_profile(request.user)
    proj = get_object_or_404(Project, pk=pk, profile=profile)
    name = proj.name
    proj.delete()
    messages.success(request, f"Project '{name}' removed.")
    return redirect("profiles:project_list")


# -----------------------------------------------------------------------------
# 6. ACHIEVEMENTS
# -----------------------------------------------------------------------------

@login_required
def achievement_list(request):
    profile = get_user_profile(request.user)
    achievements = profile.achievements.all()
    return render(request, "profiles/achievement_list.html", {"profile": profile, "achievements": achievements})


@login_required
def achievement_create(request):
    profile = get_user_profile(request.user)
    if request.method == "POST":
        form = AchievementForm(request.POST)
        if form.is_valid():
            ach = form.save(commit=False)
            ach.profile = profile
            ach.save()
            messages.success(request, f"Achievement '{ach.title}' added.")
            return redirect("profiles:achievement_list")
    else:
        form = AchievementForm()
    return render(request, "profiles/achievement_form.html", {"form": form, "title": "Add Achievement"})


@login_required
def achievement_edit(request, pk: int):
    profile = get_user_profile(request.user)
    ach = get_object_or_404(Achievement, pk=pk, profile=profile)
    if request.method == "POST":
        form = AchievementForm(request.POST, instance=ach)
        if form.is_valid():
            form.save()
            messages.success(request, f"Achievement '{ach.title}' updated.")
            return redirect("profiles:achievement_list")
    else:
        form = AchievementForm(instance=ach)
    return render(request, "profiles/achievement_form.html", {"form": form, "achievement": ach, "title": "Edit Achievement"})


@login_required
@require_POST
def achievement_delete(request, pk: int):
    profile = get_user_profile(request.user)
    ach = get_object_or_404(Achievement, pk=pk, profile=profile)
    title = ach.title
    ach.delete()
    messages.success(request, f"Achievement '{title}' removed.")
    return redirect("profiles:achievement_list")


# -----------------------------------------------------------------------------
# 7. CERTIFICATIONS
# -----------------------------------------------------------------------------

@login_required
def certification_list(request):
    profile = get_user_profile(request.user)
    certifications = profile.certifications.all()
    return render(request, "profiles/certification_list.html", {"profile": profile, "certifications": certifications})


@login_required
def certification_create(request):
    profile = get_user_profile(request.user)
    if request.method == "POST":
        form = CertificationForm(request.POST)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.profile = profile
            cert.save()
            messages.success(request, f"Certification '{cert.name}' added.")
            return redirect("profiles:certification_list")
    else:
        form = CertificationForm()
    return render(request, "profiles/certification_form.html", {"form": form, "title": "Add Certification"})


@login_required
def certification_edit(request, pk: int):
    profile = get_user_profile(request.user)
    cert = get_object_or_404(Certification, pk=pk, profile=profile)
    if request.method == "POST":
        form = CertificationForm(request.POST, instance=cert)
        if form.is_valid():
            form.save()
            messages.success(request, f"Certification '{cert.name}' updated.")
            return redirect("profiles:certification_list")
    else:
        form = CertificationForm(instance=cert)
    return render(request, "profiles/certification_form.html", {"form": form, "certification": cert, "title": "Edit Certification"})


@login_required
@require_POST
def certification_delete(request, pk: int):
    profile = get_user_profile(request.user)
    cert = get_object_or_404(Certification, pk=pk, profile=profile)
    name = cert.name
    cert.delete()
    messages.success(request, f"Certification '{name}' removed.")
    return redirect("profiles:certification_list")


# -----------------------------------------------------------------------------
# 8. PUBLICATIONS
# -----------------------------------------------------------------------------

@login_required
def publication_list(request):
    profile = get_user_profile(request.user)
    publications = profile.publications.all()
    return render(request, "profiles/publication_list.html", {"profile": profile, "publications": publications})


@login_required
def publication_create(request):
    profile = get_user_profile(request.user)
    if request.method == "POST":
        form = PublicationForm(request.POST)
        if form.is_valid():
            pub = form.save(commit=False)
            pub.profile = profile
            pub.save()
            messages.success(request, f"Publication '{pub.title}' added.")
            return redirect("profiles:publication_list")
    else:
        form = PublicationForm()
    return render(request, "profiles/publication_form.html", {"form": form, "title": "Add Publication"})


@login_required
def publication_edit(request, pk: int):
    profile = get_user_profile(request.user)
    pub = get_object_or_404(Publication, pk=pk, profile=profile)
    if request.method == "POST":
        form = PublicationForm(request.POST, instance=pub)
        if form.is_valid():
            form.save()
            messages.success(request, f"Publication '{pub.title}' updated.")
            return redirect("profiles:publication_list")
    else:
        form = PublicationForm(instance=pub)
    return render(request, "profiles/publication_form.html", {"form": form, "publication": pub, "title": "Edit Publication"})


@login_required
@require_POST
def publication_delete(request, pk: int):
    profile = get_user_profile(request.user)
    pub = get_object_or_404(Publication, pk=pk, profile=profile)
    title = pub.title
    pub.delete()
    messages.success(request, f"Publication '{title}' removed.")
    return redirect("profiles:publication_list")


# -----------------------------------------------------------------------------
# 9. LANGUAGES
# -----------------------------------------------------------------------------

@login_required
def language_list(request):
    profile = get_user_profile(request.user)
    languages = profile.languages.all()
    return render(request, "profiles/language_list.html", {"profile": profile, "languages": languages})


@login_required
def language_create(request):
    profile = get_user_profile(request.user)
    if request.method == "POST":
        form = LanguageForm(request.POST)
        if form.is_valid():
            lang = form.save(commit=False)
            lang.profile = profile
            try:
                lang.save()
                messages.success(request, f"Language '{lang.language}' added.")
            except Exception:
                messages.error(request, f"Language '{lang.language}' already added.")
            return redirect("profiles:language_list")
    else:
        form = LanguageForm()
    return render(request, "profiles/language_form.html", {"form": form, "title": "Add Language"})


@login_required
def language_edit(request, pk: int):
    profile = get_user_profile(request.user)
    lang = get_object_or_404(Language, pk=pk, profile=profile)
    if request.method == "POST":
        form = LanguageForm(request.POST, instance=lang)
        if form.is_valid():
            form.save()
            messages.success(request, f"Language '{lang.language}' updated.")
            return redirect("profiles:language_list")
    else:
        form = LanguageForm(instance=lang)
    return render(request, "profiles/language_form.html", {"form": form, "language": lang, "title": "Edit Language"})


@login_required
@require_POST
def language_delete(request, pk: int):
    profile = get_user_profile(request.user)
    lang = get_object_or_404(Language, pk=pk, profile=profile)
    name = lang.language
    lang.delete()
    messages.success(request, f"Language '{name}' removed.")
    return redirect("profiles:language_list")


# -----------------------------------------------------------------------------
# 10. PROFESSIONAL PREFERENCES
# -----------------------------------------------------------------------------

@login_required
def preference_view(request):
    profile = get_user_profile(request.user)
    pref, _ = ProfilePreference.objects.get_or_create(profile=profile)
    if request.method == "POST":
        form = ProfilePreferenceForm(request.POST, instance=pref)
        if form.is_valid():
            form.save()
            messages.success(request, "Target opportunity preferences updated.")
            return redirect("profiles:preferences")
    else:
        # Prepopulate MultipleChoice fields
        form = ProfilePreferenceForm(
            instance=pref,
            initial={
                "target_opportunity_types": pref.target_opportunity_types,
                "target_sectors": pref.target_sectors,
                "work_modes": pref.work_modes,
            },
        )
    return render(request, "profiles/preferences.html", {"form": form, "profile": profile})


# -----------------------------------------------------------------------------
# 11. EVIDENCE BANK
# -----------------------------------------------------------------------------

@login_required
def evidence_list(request):
    """
    Evidence Bank: search and inspect proof supporting claims.
    """
    profile = get_user_profile(request.user)
    ev_type = request.GET.get("type", "")
    verified_only = request.GET.get("verified", "")
    query = request.GET.get("q", "").strip()

    items = profile.evidence_items.all()
    if ev_type:
        items = items.filter(evidence_type=ev_type)
    if verified_only == "1":
        items = items.filter(verified=True)
    if query:
        items = items.filter(title__icontains=query)

    context = {
        "profile": profile,
        "evidence_items": items,
        "evidence_types": Evidence.EvidenceType.choices,
        "selected_type": ev_type,
        "verified_only": verified_only,
        "query": query,
    }
    return render(request, "profiles/evidence_list.html", context)


@login_required
def evidence_create(request):
    profile = get_user_profile(request.user)
    if request.method == "POST":
        form = EvidenceForm(request.POST, profile=profile)
        if form.is_valid():
            ev = form.save(commit=False)
            ev.profile = profile
            ev.save()
            messages.success(request, f"Evidence item '{ev.title}' added to bank.")
            return redirect("profiles:evidence_list")
    else:
        form = EvidenceForm(profile=profile)
    return render(request, "profiles/evidence_form.html", {"form": form, "title": "Record Supporting Evidence"})


@login_required
def evidence_edit(request, pk: int):
    profile = get_user_profile(request.user)
    ev = get_object_or_404(Evidence, pk=pk, profile=profile)
    if request.method == "POST":
        form = EvidenceForm(request.POST, instance=ev, profile=profile)
        if form.is_valid():
            form.save()
            messages.success(request, f"Evidence item '{ev.title}' updated.")
            return redirect("profiles:evidence_list")
    else:
        form = EvidenceForm(instance=ev, profile=profile)
    return render(request, "profiles/evidence_form.html", {"form": form, "evidence": ev, "title": "Edit Evidence Item"})


@login_required
@require_POST
def evidence_delete(request, pk: int):
    profile = get_user_profile(request.user)
    ev = get_object_or_404(Evidence, pk=pk, profile=profile)
    title = ev.title
    ev.delete()
    messages.success(request, f"Evidence item '{title}' removed.")
    return redirect("profiles:evidence_list")


@login_required
@require_POST
def evidence_toggle_verification(request, pk: int):
    profile = get_user_profile(request.user)
    ev = get_object_or_404(Evidence, pk=pk, profile=profile)
    ev.verified = not ev.verified
    ev.save()
    status = "verified" if ev.verified else "marked unverified"
    messages.success(request, f"Evidence '{ev.title}' {status}.")
    return redirect("profiles:evidence_list")
