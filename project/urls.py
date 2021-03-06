from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, logout_then_login

import core.urls


urlpatterns = [
    path('', include(core.urls, namespace='core')),
    path('admin/', admin.site.urls),

    path('login/', LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', logout_then_login, {'login_url': '/login/?next=/'}, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static('node_modules', document_root=settings.BASE_DIR + '/node_modules')
    urlpatterns += static('media', document_root=settings.MEDIA_ROOT)
