from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI()

weather_codes = {
    0: 'Clear sky',
    1: 'Mainly clear',
    2: 'Partly cloudy',
    3: 'Overcast',
    45: 'Fog',
    48: 'Depositing rime fog',
    51: 'Drizzle: Light',
    53: 'Drizzle: Moderate',
    55: 'Drizzle: Dense intensity',
    61: 'Rain: Slight',
    63: 'Rain: Moderate',
    65: 'Rain: Heavy',
    80: 'Rain showers: Slight',
    81: 'Rain showers: Moderate',
    82: 'Rain showers: Violent'
}

@app.get("/weather/")
async def get_weather(latitude: float, longitude: float):
    try:
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise HTTPException(status_code=400, detail="Invalid latitude or longitude values.")

        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()

        weather = response.json().get("current_weather",{})
        if "temperature" not in weather or "windspeed" not in weather:
            raise HTTPException(status_code=502, detail="Unexpected weather data format.")

        structured_data = {
            "latitude": latitude,
            "longitude": longitude,
            "temperature": f"{weather['temperature']} °C",
            "weatherDescription": weather_codes.get(weather['weathercode'], 'Unknown weather condition'),
            "windSpeed": f"{weather['windspeed']} km/h"
        }

        return structured_data

    except HTTPException as http_err:
        raise http_err
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve weather data: {str(error)}")


#http://localhost:8000/weather/?latitude=48.8566&longitude=2.3522