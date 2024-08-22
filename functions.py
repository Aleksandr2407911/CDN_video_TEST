# Функция для получения координат города
import math

import aiohttp

from config import API_KEY_COORD


async def get_city_coordinates(city_name: str):
    api_key = API_KEY_COORD  # Replace with your API key
    url = f"https://api.api-ninjas.com/v1/geocoding?city={city_name}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={'X-Api-Key': api_key}) as response:
            if response.status != 200:
                return None, None
            data = await response.json()
            if data:
                return data[0]['latitude'], data[0]['longitude']
            return None, None

# Функция для вычисления расстояния между двумя точками
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Радиус Земли в километрах
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    return R * c