# pettycash/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# from core.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', home, name='home'),
    path('accounts/', include(('accounts.urls','accounts'), namespace='accounts')),
    path('', include(('core.urls','core'), namespace='core')),
    path('transactions/', include(('transactions.urls','transactions'), namespace='transactions')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
