"""
Open-Meteo API を使用した天気情報取得サービス
APIキー不要の無料天気API
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Open-Meteo API のベースURL
OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


class WeatherService:
    """Open-Meteo APIを使用した天気情報取得"""
    
    def __init__(self):
        """初期化"""
        self.base_url = OPEN_METEO_BASE_URL
        self.geocoding_url = OPEN_METEO_GEOCODING_URL
        self.timeout = aiohttp.ClientTimeout(total=10)
    
    async def get_weather(
        self,
        latitude: float,
        longitude: float,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        指定座標の天気情報を取得
        
        Args:
            latitude: 緯度
            longitude: 経度
            days: 取得する日数（最大16日間）
        
        Returns:
            天気情報辞書
        
        Raises:
            Exception: API呼び出しエラー
        """
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
                "temperature_unit": "celsius",
                "wind_speed_unit": "kmh",
                "precipitation_unit": "mm",
                "timezone": "auto"
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_weather_response(data, days)
                    else:
                        logger.error(f"天気API エラー: {response.status}")
                        raise Exception(f"Weather API Error: {response.status}")
        
        except asyncio.TimeoutError:
            logger.error("天気API タイムアウト")
            raise Exception("Weather API timeout")
        except Exception as e:
            logger.error(f"天気情報取得エラー: {str(e)}")
            raise
    
    async def get_location_coordinates(self, location_name: str) -> Optional[Dict[str, float]]:
        """
        地名から緯度経度を取得
        
        Args:
            location_name: 地名（日本語対応）
        
        Returns:
            {'latitude': float, 'longitude': float} または None
        
        Raises:
            Exception: API呼び出しエラー
        """
        try:
            params = {
                "name": location_name,
                "count": 1,
                "language": "ja",
                "format": "json"
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(self.geocoding_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("results") and len(data["results"]) > 0:
                            result = data["results"][0]
                            return {
                                "latitude": result["latitude"],
                                "longitude": result["longitude"],
                                "name": result.get("name", ""),
                                "country": result.get("country", "")
                            }
                        return None
                    else:
                        logger.error(f"ジオコーディングAPI エラー: {response.status}")
                        raise Exception(f"Geocoding API Error: {response.status}")
        
        except asyncio.TimeoutError:
            logger.error("ジオコーディングAPI タイムアウト")
            raise Exception("Geocoding API timeout")
        except Exception as e:
            logger.error(f"位置情報取得エラー: {str(e)}")
            raise
    
    def _parse_weather_response(self, data: Dict[str, Any], days: int) -> Dict[str, Any]:
        """
        Open-Meteo APIレスポンスをパース
        
        Args:
            data: APIレスポンス
            days: 取得する日数
        
        Returns:
            パース済み天気情報
        """
        daily = data.get("daily", {})
        times = daily.get("time", [])[:days]
        weather_codes = daily.get("weather_code", [])[:days]
        temps_max = daily.get("temperature_2m_max", [])[:days]
        temps_min = daily.get("temperature_2m_min", [])[:days]
        precipitations = daily.get("precipitation_sum", [])[:days]
        
        forecasts = []
        for i, date_str in enumerate(times):
            forecasts.append({
                "date": date_str,
                "weather_code": weather_codes[i] if i < len(weather_codes) else None,
                "weather_description": self._get_weather_description(weather_codes[i]) if i < len(weather_codes) else "不明",
                "temp_max": temps_max[i] if i < len(temps_max) else None,
                "temp_min": temps_min[i] if i < len(temps_min) else None,
                "precipitation": precipitations[i] if i < len(precipitations) else 0
            })
        
        return {
            "location": {
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "timezone": data.get("timezone")
            },
            "forecast": forecasts
        }
    
    @staticmethod
    def _get_weather_description(weather_code: int) -> str:
        """
        WMO天気コードを日本語説明に変換
        
        Args:
            weather_code: WMO天気コード
        
        Returns:
            日本語の天気説明
        """
        weather_descriptions = {
            0: "晴天",
            1: "ほぼ晴天",
            2: "部分的に曇り",
            3: "曇り",
            45: "霧",
            48: "霧（続く）",
            51: "小雨",
            53: "中程度の雨",
            55: "激しい雨",
            61: "弱い雨",
            63: "中程度の雨",
            65: "激しい雨",
            71: "弱い雪",
            73: "中程度の雪",
            75: "激しい雪",
            77: "みぞれ",
            80: "弱い通り雨",
            81: "中程度の通り雨",
            82: "激しい通り雨",
            85: "弱い雪",
            86: "激しい雪",
            95: "雷雨",
            96: "雹を伴う雷雨",
            99: "雹を伴う雷雨"
        }
        return weather_descriptions.get(weather_code, f"コード{weather_code}")


# グローバルインスタンス
_weather_service: Optional[WeatherService] = None


def get_weather_service() -> WeatherService:
    """
    天気サービスインスタンスを取得（シングルトン）
    
    Returns:
        WeatherService インスタンス
    """
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
    return _weather_service
