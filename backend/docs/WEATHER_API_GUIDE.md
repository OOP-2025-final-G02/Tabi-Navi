# Open-Meteo 天気API統合ガイド

## 概要
Open-Meteo API は無料で利用できる天気情報提供サービスです。APIキー不要で、以下の情報が取得できます。

- **利点:**
  - 完全無料（APIキー不要）
  - 登録不要で使用可能
  - 日本語対応のジオコーディング
  - 最大16日先の予報
  - 複数の言語対応

## 基本的な使用方法

### 1. 地名から天気情報を取得

```python
from app.services.weather_service import get_weather_service

async def get_weather_by_location():
    weather_service = get_weather_service()
    
    # 地名から座標を取得
    coords = await weather_service.get_location_coordinates("東京")
    
    if coords:
        # 天気情報を取得（今後7日間）
        weather = await weather_service.get_weather(
            latitude=coords["latitude"],
            longitude=coords["longitude"],
            days=7
        )
        return weather
```

### 2. 座標から直接天気情報を取得

```python
from app.services.weather_service import get_weather_service

async def get_weather_by_coordinates():
    weather_service = get_weather_service()
    
    # 直接座標指定
    weather = await weather_service.get_weather(
        latitude=35.6762,  # 東京
        longitude=139.6503,
        days=7
    )
    return weather
```

## APIレスポンス形式

### `get_location_coordinates()` の戻り値

```json
{
    "latitude": 35.6762,
    "longitude": 139.6503,
    "name": "東京",
    "country": "日本"
}
```

### `get_weather()` の戻り値

```json
{
    "location": {
        "latitude": 35.6762,
        "longitude": 139.6503,
        "timezone": "Asia/Tokyo"
    },
    "forecast": [
        {
            "date": "2026-01-10",
            "weather_code": 0,
            "weather_description": "晴天",
            "temp_max": 12.5,
            "temp_min": 5.2,
            "precipitation": 0.0
        },
        {
            "date": "2026-01-11",
            "weather_code": 3,
            "weather_description": "曇り",
            "temp_max": 11.2,
            "temp_min": 4.8,
            "precipitation": 2.3
        }
    ]
}
```

## WMO天気コード対応表

主要なコード：
- `0`: 晴天
- `1`: ほぼ晴天
- `2`: 部分的に曇り
- `3`: 曇り
- `51-55`: 雨（弱い/中程度/激しい）
- `71-75`: 雪（弱い/中程度/激しい）
- `80-82`: 通り雨
- `95-99`: 雷雨

## 旅行プラン生成での活用例

```python
async def generate_travel_plan_with_weather(location, days):
    weather_service = get_weather_service()
    
    # 位置情報を取得
    coords = await weather_service.get_location_coordinates(location)
    
    if coords:
        # 天気情報を取得
        weather_data = await weather_service.get_weather(
            latitude=coords["latitude"],
            longitude=coords["longitude"],
            days=days
        )
        
        # 天気情報をプラン生成に含める
        weather_context = f"""
        目的地: {location}
        予報期間: {days}日間
        天気予報:
        {json.dumps(weather_data['forecast'], ensure_ascii=False, indent=2)}
        """
        
        # 旅行プランを生成（天気情報を考慮）
        plan = await generate_plan(location, days, weather_context)
        return plan
```

## 環境設定（requirements.txt）

既に `aiohttp` は requirements.txt に含まれています：
- `requests==2.31.0` - REST API呼び出し
- `aiohttp` - 非同期HTTP通信（uvicorn での使用に最適）

## API制限

- **レート制限:** 無制限（フェアユース原則）
- **同時リクエスト:** 推奨 10 リクエスト/秒
- **キャッシュ推奨:** 予報は1時間ごとに更新

## トラブルシューティング

### タイムアウトが発生する場合
```python
weather_service.timeout = aiohttp.ClientTimeout(total=15)
```

### 日本語の地名が見つからない場合
- 英語名で試してみる: `"Tokyo"` 
- より詳細な地域を指定: `"Tokyo, Japan"`

### 座標エラーが発生する場合
- 座標値が有効な範囲内か確認
  - 緯度: -90 ～ 90
  - 経度: -180 ～ 180

## 参考リンク

- [Open-Meteo 公式](https://open-meteo.com/)
- [API ドキュメント](https://open-meteo.com/en/docs)
- [ジオコーディング API](https://open-meteo.com/en/docs/geocoding-api)
