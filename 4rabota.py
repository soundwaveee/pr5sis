import aiohttp
import asyncio
import json
from datetime import datetime

BRAND_URL = "https://vpic.nhtsa.dot.gov/api/vehicles/GetMakesForVehicleType/car?format=json"
CHARACTERISTICS_URL = "https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMake/honda?format=json"

semaphore = asyncio.Semaphore(3)

async def fetch_data(url, session):
    async with semaphore:
        try:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Ошибка {response.status} при запросе {url}")
        except asyncio.TimeoutError:
            print(f"Таймаут при запросе {url}")
        except Exception as e:
            print(f"Ошибка: {e} при запросе {url}")
        return None

async def get_car_data():
    async with aiohttp.ClientSession() as session:
        brand_task = fetch_data(BRAND_URL, session)
        char_task = fetch_data(CHARACTERISTICS_URL, session)
        brand_data, char_data = await asyncio.gather(brand_task, char_task)
        return {
            "brand": brand_data,
            "characteristics": char_data,
            "timestamp": datetime.now().isoformat()
        }

def save_data(data, filename="cars_data.json"):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

async def main():
    while True:
        data = await get_car_data()
        if data:
            save_data(data)

            brands_count = data['brand'].get('Count', 0) if data['brand'] else 0
            models_count = data['characteristics'].get('Count', 0) if data['characteristics'] else 0

            print(f"[{datetime.now().strftime('%H:%M:%S')}] Данные сохранены! "
                  f"Получено марок: {brands_count}, моделей: {models_count}")

        await asyncio.sleep(600)

if __name__ == "__main__":
    asyncio.run(main())