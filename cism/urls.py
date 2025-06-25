from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('cism_app.urls')),  # Include the app's URLs
]

# Serve media files using Django's built-in serve view
# This works regardless of DEBUG setting
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]

# Serve static files (for development/testing)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
