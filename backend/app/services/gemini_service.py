"""
Gemini API通信サービス
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any
from google.generativeai import GenerativeModel
from app.config import settings
from app.utils.exceptions import GeminiAPIError


class GeminiService:
    """Gemini API通信管理"""
    
    def __init__(self):
        """初期化"""
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY環境変数が設定されていません")
        
        # Gemini APIの初期化
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        self.model = GenerativeModel('gemini-pro')
        self.timeout = settings.AI_REQUEST_TIMEOUT
    
    async def call_gemini(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        """
        Gemini APIにリクエスト送信
        
        Args:
            prompt (str): プロンプト
            temperature (float): 創造性レベル (0.0-1.0)
            max_tokens (int): 最大トークン数
            
        Returns:
            Dict[str, Any]: JSON形式のレスポンス
            
        Raises:
            GeminiAPIError: API呼び出し失敗時
        """
        try:
            # タイムアウト付きでAPI呼び出し
            response = await asyncio.wait_for(
                self._call_api(prompt, temperature, max_tokens),
                timeout=self.timeout
            )
            return response
        except asyncio.TimeoutError:
            raise GeminiAPIError(f"Gemini API タイムアウト ({self.timeout}秒)")
        except Exception as e:
            raise GeminiAPIError(f"Gemini API エラー: {str(e)}")
    
    async def _call_api(
        self, 
        prompt: str, 
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """APIを実際に呼び出す（内部メソッド）"""
        # 非同期でAPI呼び出しを実行
        response = await asyncio.to_thread(
            self._sync_generate_content,
            prompt,
            temperature,
            max_tokens
        )
        
        # レスポンスをJSON化
        response_text = response.text
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            raise GeminiAPIError(f"JSON パースエラー: {str(e)}\nレスポンス: {response_text[:500]}")
    
    def _sync_generate_content(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int
    ):
        """同期版のコンテンツ生成（スレッドで実行）"""
        response = self.model.generate_content(
            prompt,
            generation_config={
                'temperature': temperature,
                'max_output_tokens': max_tokens,
            }
        )
        return response
    
    async def generate_travel_plan(
        self, 
        travel_input, 
        plan_id: str
    ) -> Dict[str, Any]:
        """
        旅行プラン生成（高レベルAPI）
        
        Args:
            travel_input: TravelInput モデル
            plan_id (str): プラン用UUID
            
        Returns:
            Dict[str, Any]: 生成されたプラン
        """
        # プロンプト生成
        prompt = self._create_travel_prompt(travel_input)
        
        # Gemini API呼び出し
        response = await self.call_gemini(
            prompt=prompt,
            temperature=0.7,
            max_tokens=2048
        )
        
        # ログ記録
        await self._save_api_log(plan_id, prompt, response)
        
        return response
    
    def _create_travel_prompt(self, travel_input) -> str:
        """旅行プラン用プロンプト生成"""
        from app.services.prompts.travel_plan_prompt import create_travel_prompt
        return create_travel_prompt(travel_input)
    
    async def _save_api_log(
        self, 
        plan_id: str, 
        request: str, 
        response: Dict
    ) -> None:
        """リクエスト・レスポンスをJSONファイルに記録"""
        from app.utils.json_handler import save_gemini_log
        await save_gemini_log(plan_id, request, response)


# グローバルインスタンス（遅延初期化）
_gemini_service = None


def get_gemini_service() -> GeminiService:
    """Gemini Service インスタンスを取得"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
