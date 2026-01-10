"""
Gemini API通信サービス
"""

import asyncio
import json
import sys
from pathlib import Path
import google.generativeai as genai
from datetime import datetime
from typing import Dict, Any
from google.generativeai import GenerativeModel

# Add backend directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import settings
from ..utils.exceptions import GeminiAPIError


class GeminiService:
    """Gemini API通信管理"""
    
    def __init__(self):
        """初期化"""
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY環境変数が設定されていません")
        
        # Gemini APIの初期化
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
        except Exception as e:
            raise GeminiAPIError(f"Gemini API 初期化エラー: {str(e)}")
        
        try:
            self.model = GenerativeModel('gemini-pro')
        except Exception as e:
            raise GeminiAPIError(f"モデルロードエラー: {str(e)}")
        
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
        except GeminiAPIError:
            # 既に GeminiAPIError の場合はそのまま再スロー
            raise
        except Exception as e:
            raise GeminiAPIError(f"予期しないエラー: {type(e).__name__}: {str(e)}")
    
    async def _call_api(
        self, 
        prompt: str, 
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """APIを実際に呼び出す（内部メソッド）"""
        try:
            # 非同期でAPI呼び出しを実行
            response = await asyncio.to_thread(
                self._sync_generate_content,
                prompt,
                temperature,
                max_tokens
            )
            
            # レスポンスがNoneの場合
            if response is None:
                raise GeminiAPIError("API レスポンスが空です")
            
            # レスポンスをJSON化
            response_text = response.text
            if not response_text:
                raise GeminiAPIError("API がテキストレスポンスを返しませんでした")
            
            try:
                return json.loads(response_text)
            except json.JSONDecodeError as e:
                raise GeminiAPIError(f"JSON パースエラー: {str(e)}\nレスポンス: {response_text[:500]}")
        
        except GeminiAPIError:
            raise
        except Exception as e:
            raise GeminiAPIError(f"API呼び出しエラー: {type(e).__name__}: {str(e)}")
    
    def _sync_generate_content(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int
    ):
        """同期版のコンテンツ生成（スレッドで実行）"""
        try:
            # プロンプトの検証
            if not prompt or len(prompt.strip()) == 0:
                raise ValueError("プロンプトが空です")
            
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': temperature,
                    'max_output_tokens': max_tokens,
                }
            )
            
            # レスポンスの検証
            if not response:
                raise GeminiAPIError("API がレスポンスを返しませんでした")
            
            return response
        
        except ValueError as e:
            raise GeminiAPIError(f"パラメータエラー: {str(e)}")
        except GeminiAPIError:
            raise
        except Exception as e:
            raise GeminiAPIError(f"コンテンツ生成エラー: {type(e).__name__}: {str(e)}")
    
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
            
        Raises:
            GeminiAPIError: プラン生成エラー
        """
        try:
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
        
        except GeminiAPIError:
            raise
        except Exception as e:
            raise GeminiAPIError(f"旅行プラン生成エラー: {type(e).__name__}: {str(e)}")
    
    def _create_travel_prompt(self, travel_input) -> str:
        """旅行プラン用プロンプト生成"""
        try:
            from .prompts.travel_plan_prompt import create_travel_prompt
            return create_travel_prompt(travel_input)
        except Exception as e:
            raise GeminiAPIError(f"プロンプト生成エラー: {type(e).__name__}: {str(e)}")
    
    async def _save_api_log(
        self, 
        plan_id: str, 
        request: str, 
        response: Dict
    ) -> None:
        """リクエスト・レスポンスをJSONファイルに記録"""
        try:
            from ..utils.json_handler import save_gemini_log
            await save_gemini_log(plan_id, request, response)
        except Exception as e:
            # ログ保存失敗は警告として記録するが、プラン生成は成功とする
            print(f"警告: ログ保存失敗 - {type(e).__name__}: {str(e)}")


# グローバルインスタンス（遅延初期化）
_gemini_service = None


def get_gemini_service() -> GeminiService:
    """Gemini Service インスタンスを取得"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
