from .translations import LANGUAGE_LABELS, TRANSLATIONS


def i18n(request):
    lang = getattr(request, "LANGUAGE_CODE", "uz")
    if lang not in TRANSLATIONS:
        lang = "uz"

    # `request.path` on a non-default-language page already carries that
    # language's own URL prefix (e.g. "/de/vacancies/"). If we fed that
    # straight back into the language-switch form's "next" field, Django's
    # set_language view only ADDS a prefix when one is missing — it never
    # swaps an existing one — so switching languages a second time (while
    # already on a prefixed page) silently redirected back to the SAME
    # old-language URL. Stripping the current prefix here gives
    # set_language a language-neutral path to redirect to, so it can
    # attach the newly-chosen language's prefix correctly every time.
    path = request.path
    if lang != "uz" and path.startswith(f"/{lang}/"):
        next_path = path[len(lang) + 1:] or "/"
    elif lang != "uz" and path == f"/{lang}":
        next_path = "/"
    else:
        next_path = path

    # Equivalent path of the current page in every supported language, for
    # hreflang alternate links (e.g. {"uz": "/vacancies/", "de": "/de/vacancies/", ...}).
    hreflang_paths = {
        code: (next_path if code == "uz" else f"/{code}{next_path}")
        for code in TRANSLATIONS
    }

    return {
        "T": TRANSLATIONS[lang],
        "CUR_LANG": lang,
        "LANGUAGES_LIST": LANGUAGE_LABELS,
        "LANG_NEUTRAL_PATH": next_path,
        "HREFLANG_PATHS": hreflang_paths,
    }
