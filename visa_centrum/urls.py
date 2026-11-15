from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.views.static import serve as static_serve

from core.views import robots_txt, sitemap_xml

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin.site.urls),
    path("robots.txt", robots_txt),
    path("sitemap.xml", sitemap_xml),
    path("favicon.ico", RedirectView.as_view(url="/static/core/img/favicon.ico", permanent=True)),
    path("media/<path:path>", static_serve, {"document_root": settings.MEDIA_ROOT}),
]

urlpatterns += i18n_patterns(
    path("vacancies/", include("vacancies.urls")),
    path("", include("core.urls")),
    prefix_default_language=False,
)
