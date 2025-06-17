from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import FavoriteCity
from .serializers import FavoriteCitySerializer
import requests

API_KEY = '5f72053d09076a38ff9d5bd895a00529'  # Replace with your real API key

@api_view(['GET'])
def current_weather(request, city):
    cache_key = f"current_weather_{city.lower()}"
    cached_data = cache.get(cache_key)

    if cached_data:
        print("cached")
        return Response(cached_data)

    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'
    r = requests.get(url)

    if r.status_code == 200:
        data = r.json()
        cache.set(cache_key, data, timeout=300)  # Cache 5 min
        return Response(data)

    return Response({'error': 'City not found'}, status=r.status_code)

@api_view(['GET'])
def forecast_weather(request, city):
    cache_key = f"forecast_weather_{city.lower()}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return Response(cached_data)

    url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric'
    r = requests.get(url)

    if r.status_code == 200:
        data = r.json()
        cache.set(cache_key, data, timeout=300)  # Cache 5 min
        return Response(data)

    return Response({'error': 'City not found'}, status=r.status_code)

@api_view(['GET', 'POST'])
def favorites(request):
    print(request)
    if request.method == 'POST':
        serializer = FavoriteCitySerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        favorites = FavoriteCity.objects.all()
        serializer = FavoriteCitySerializer(favorites, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def current_weather_multiple(request, cities):
    # cities_param = request.query_params.get('cities')
    cities_param = cities
    if not cities_param:
        return Response({'error': 'Please provide cities as ?cities=City1,City2'}, status=400)
    
    cities = [city.strip() for city in cities_param.split(',')]
    results = []

    for city in cities:
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            results.append({
                'city': city,
                'temperature': data['main']['temp'],
                'description': data['weather'][0]['description'],
                'raw': data  # optional: remove if you want only summary
            })
        else:
            results.append({
                'city': city,
                'error': f"Could not fetch weather: {r.status_code} {r.reason}"
            })

    return Response(results)