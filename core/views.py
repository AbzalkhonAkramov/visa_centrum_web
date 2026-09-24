from django.shortcuts import redirect, render

from .forms import ContactForm
from .translations import TRANSLATIONS


def home(request):
    lang = request.LANGUAGE_CODE if request.LANGUAGE_CODE in TRANSLATIONS else "uz"
    T = TRANSLATIONS[lang]

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(request.path + "?sent=1#contact")
    else:
        form = ContactForm()

    form.fields["full_name"].widget.attrs.setdefault("placeholder", T["contact_ph_name"])
    form.fields["email"].widget.attrs.setdefault("placeholder", T["contact_ph_email"])
    form.fields["phone"].widget.attrs.setdefault("placeholder", T["contact_ph_phone"])
    form.fields["message"].widget.attrs.setdefault("placeholder", T["contact_ph_message"])

    return render(request, "core/home.html", {
        "form": form,
        "sent": request.GET.get("sent") == "1",
    })
