"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from ninja import NinjaAPI
from authentication.api import router as auth_router
from apps.example.api import router as example_router
from django.http import JsonResponse
import time

# Create API instance
api = NinjaAPI(
    title="API Boilerplate",
    version="1.0.0",
    description="Django Ninja API boilerplate with Celery and Channels",
    docs_url="/docs",
)

# Add routers
api.add_router("/auth", auth_router)
api.add_router("/example", example_router)


# Health check endpoint (no auth required)
@api.get("/health", tags=["System"])
def health_check(request):
    """Health check endpoint for Docker"""
    return {"status": "healthy", "timestamp": time.time()}


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    # Redirect health check with trailing slash to without trailing slash
    path("api/health/", RedirectView.as_view(url="/api/health", permanent=True)),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
