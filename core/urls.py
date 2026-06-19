from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('social.urls')), # यसले सिधै सामाजिक एपको urls.py लाई लिङ्क गर्छ
]

# इमेज र मिडिया फाइलहरू लोड गर्नका लागि
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)