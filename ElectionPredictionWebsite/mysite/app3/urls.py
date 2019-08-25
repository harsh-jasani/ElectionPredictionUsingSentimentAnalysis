from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('calculate', views.getresults, name="calculate"),
    path('portfolio', views.giveportfolio, name="portfolio"),
    path('about', views.about, name="about"),
    path('contact', views.contact, name="contact"),
    path('download', views.download, name="download")
    #path('download', views.download, name="download")
]