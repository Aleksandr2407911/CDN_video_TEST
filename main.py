from typing import Annotated

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import select
from database import async_session, City
from functions import get_city_coordinates, haversine



# Создание FastAPI приложения
app = FastAPI()

# Модель для запроса добавления города
class CityCreate(BaseModel):
    name: str

# Добавление города
@app.post("/cities/", response_model=CityCreate)
async def add_city(city: Annotated[CityCreate, Depends()]):
    latitude, longitude = await get_city_coordinates(city.name)
    if latitude is None or longitude is None:
        raise HTTPException(status_code=400, detail="Failed to retrieve city coordinates")

    async with async_session() as session:
        new_city = City(name=city.name, latitude=latitude, longitude=longitude)
        session.add(new_city)
        await session.commit()
        await session.refresh(new_city)

    return new_city


# Удаление города
@app.delete("/cities/{city_id}")
async def delete_city(city_id: int):
    async with async_session() as session:
        city = await session.get(City, city_id)
        if city is None:
            raise HTTPException(status_code=404, detail="City not found")

        await session.delete(city)
        await session.commit()

    return {"message": "City deleted successfully"}

# Получение информации о всех городах
@app.get("/cities/")
async def get_cities():
    async with async_session() as session:
        cities = await session.scalars(select(City))
        return cities.all()


# Получение 2 ближайших городов
@app.get("/nearest_cities/")
async def get_nearest_cities(latitude: float, longitude: float):
    async with async_session() as session:
        cities = await session.scalars(select(City))
        cities_list = cities.all()

    if not cities_list:
        raise HTTPException(status_code=404, detail="No cities found in the database")

    # Вычисление расстояний до заданной точки
    distances = []
    for city in cities_list:
        distance = haversine(latitude, longitude, city.latitude, city.longitude)
        distances.append((city, distance))

    # Сортировка по расстоянию и выбор 2 ближайших
    nearest_cities = sorted(distances, key=lambda x: x[1])[:2]
    return [{"name": city[0].name, "latitude": city[0].latitude, "longitude": city[0].longitude, "distance": city[1]} for city in nearest_cities]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

