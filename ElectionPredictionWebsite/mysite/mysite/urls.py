from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('app3/', include('app3.urls')),
    path('admin/', admin.site.urls)
]
