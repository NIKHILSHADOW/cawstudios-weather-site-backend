from django.urls import path
from . import views

urlpatterns = [
    path('current-multiple/<str:cities>', views.current_weather_multiple, name='current_weather_multiple'),
    path('current/<str:city>/', views.current_weather, name='current_weather'),
    path('forecast/<str:city>/', views.forecast_weather, name='forecast_weather'),
    path('favorites/', views.favorites, name='favorites') 
]
