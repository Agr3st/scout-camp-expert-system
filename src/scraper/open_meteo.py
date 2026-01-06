import openmeteo_requests
import pandas as pd
import requests_cache
from openmeteo_sdk.WeatherApiResponse import WeatherApiResponse
from retry_requests import retry


def _create_openmeteo_client(
    cache_dir: str = ".cache",
    expire_after: int = 3600,
    retries: int = 5,
    backoff_factor: float = 0.2,
) -> openmeteo_requests.Client:
    """
    Create Open-Meteo API client with cache and retry logic.
    """
    cache_session = requests_cache.CachedSession(cache_dir, expire_after=expire_after)
    retry_session = retry(cache_session, retries=retries, backoff_factor=backoff_factor)
    return openmeteo_requests.Client(session=retry_session)


def _fetch_weather_response(
    client: openmeteo_requests.Client,
    lat: float,
    lon: float,
    forecast_days: int = 1,
    timezone: str = "Europe/Berlin",
) -> WeatherApiResponse:
    """
    Fetch weather data from Open-Meteo API.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": [
            "temperature_2m",
            "weather_code",
            "wind_speed_10m",
            "rain",
            "wind_gusts_10m",
        ],
        "timezone": timezone,
        "forecast_days": forecast_days,
    }

    responses = client.weather_api(url, params=params)
    return responses[0]  # single location


def _parse_hourly_to_dataframe(response) -> pd.DataFrame:
    """
    Parse hourly Open-Meteo response into pandas DataFrame.
    """
    hourly = response.Hourly()

    start_dt = pd.to_datetime(hourly.Time(), unit="s", utc=True).tz_convert(
        "Europe/Berlin"
    )
    end_dt = pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True).tz_convert(
        "Europe/Berlin"
    )

    data = {
        "date": pd.date_range(
            start=start_dt,
            end=end_dt,
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        ),
        "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
        "weather_code": hourly.Variables(1).ValuesAsNumpy(),
        "wind_speed_10m": hourly.Variables(2).ValuesAsNumpy(),
        "rain": hourly.Variables(3).ValuesAsNumpy(),
        "wind_gusts_10m": hourly.Variables(4).ValuesAsNumpy(),
    }
    return pd.DataFrame(data)


def get_hourly_weather_forecast(lat: float, lon: float) -> pd.DataFrame:
    """
    Takes latitude & longitude and returns hourly weather DataFrame for the next 24 hours.
    """
    client = _create_openmeteo_client()
    response = _fetch_weather_response(client, lat, lon)
    df = _parse_hourly_to_dataframe(response)
    return df
