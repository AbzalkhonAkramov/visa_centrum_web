from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import ContactForm
from .translations import TRANSLATIONS

LANG_PREFIXES = {"uz": "", "de": "/de", "en": "/en", "ru": "/ru"}


def home(request):
    return render(request, "core/home.html", {})


def about(request):
    from team.models import TeamMember

    members = TeamMember.objects.filter(is_published=True)
    return render(request, "core/about.html", {"members": members})


def services(request):
    return render(request, "core/services.html", {})


def contact(request):
    lang = request.LANGUAGE_CODE if request.LANGUAGE_CODE in TRANSLATIONS else "uz"
    T = TRANSLATIONS[lang]

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(request.path + "?sent=1")
    else:
        form = ContactForm()

    form.fields["full_name"].widget.attrs.setdefault("placeholder", T["contact_ph_name"])
    form.fields["email"].widget.attrs.setdefault("placeholder", T["contact_ph_email"])
    form.fields["phone"].widget.attrs.setdefault("placeholder", T["contact_ph_phone"])
    form.fields["message"].widget.attrs.setdefault("placeholder", T["contact_ph_message"])

    return render(request, "core/contact.html", {
        "form": form,
        "sent": request.GET.get("sent") == "1",
    })


def robots_txt(request):
    sitemap_url = request.build_absolute_uri("/sitemap.xml")
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "",
        f"Sitemap: {sitemap_url}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request):
    from vacancies.models import Vacancy

    paths = ["/", "/about/", "/services/", "/contact/", "/vacancies/"]
    paths += [f"/vacancies/{slug}/" for slug in Vacancy.objects.filter(is_published=True).values_list("slug", flat=True)]

    urls = []
    for path in paths:
        for lang, prefix in LANG_PREFIXES.items():
            urls.append(request.build_absolute_uri(f"{prefix}{path}"))

    body = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        body.append(f"  <url><loc>{url}</loc></url>")
    body.append("</urlset>")
    return HttpResponse("\n".join(body), content_type="application/xml")
