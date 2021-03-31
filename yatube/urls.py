from django.contrib import admin
from django.urls import include, path
from django.conf.urls import handler404, handler500
from posts import views


urlpatterns = [
    path('404/', views.page_not_found, name='404'),
    path('500/', views.server_error, name='500'),
    path('about/', include('about.urls', namespace='about')),
    path("auth/", include("users.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path("", include("posts.urls")),
]
handler404 = "posts.views.page_not_found"  # noqa
handler500 = "posts.views.server_error"  # noqa
