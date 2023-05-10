from django.urls import path
from . import views

app_name = "api"
urlpatterns = [
    path("doaj-api/", views.doaj_get, name="doaj_api"),
    path("google-scholar/", views.google_scholar, name="google-scholar"),
    path("core", views.core_get, name="core"),
    path('eric/', views.eric_papers, name='eric_papers'),
    path("zenodo/",views.zenodo, name="zenodo"),
    path('post-paper/',views.post_papers,name='post-papers'),
    path('semantic-scholar/', views.semantic_scholar, name='semantic-scholar')
]