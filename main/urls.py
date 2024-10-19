from django.urls import path

from .views import HomeView
from .views import InitImageView

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    # path('/init', InitImageView.as_view(), name='init_image')
]