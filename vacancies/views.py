from django.shortcuts import get_object_or_404, render

from core.translations import format_slots

from .models import Vacancy


def vacancy_list(request):
    lang = request.LANGUAGE_CODE
    qs = Vacancy.objects.filter(is_published=True)
    vacancies = [
        {
            "slug": v.slug,
            "title": v.title(lang),
            "location": v.location(lang),
            "slots": v.slots,
            "slots_label": format_slots(v.slots, lang),
        }
        for v in qs
    ]
    return render(request, "vacancies/list.html", {"vacancies": vacancies})


def vacancy_detail(request, slug):
    lang = request.LANGUAGE_CODE
    v = get_object_or_404(Vacancy, slug=slug, is_published=True)
    vacancy = {
        "title": v.title(lang),
        "location": v.location(lang),
        "description": v.description(lang),
        "slots": v.slots,
        "slots_label": format_slots(v.slots, lang),
    }
    return render(request, "vacancies/detail.html", {"vacancy": vacancy})
