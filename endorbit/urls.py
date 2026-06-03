"""
URL configuration for endorbit project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include, re_path
from aihandler.views import GetAllProduct
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def serve_spa(request, path=None):
    index_path = os.path.join(settings.BASE_DIR, "frontend-dist", "index.html")
    with open(index_path) as f:
        return HttpResponse(f.read(), content_type="text/html")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("aihandler.urls"), name="api-v1"),
    path("", view=GetAllProduct.as_view(), name="index"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(
            template_name="swagger-ui.html", url_name="schema"
        ),
        name="swagger-ui",
    ),
    # Catch-all: serve React SPA for client-side routing
    re_path(r"^(?!api/|admin/|schema/|docs/).*$", serve_spa),
]
