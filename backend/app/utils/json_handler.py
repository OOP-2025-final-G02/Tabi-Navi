"""
JSON ログ管理
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


LOGS_DIR = Path(__file__).parent.parent.parent / "data" / "gemini_logs"


async def save_gemini_log(
    plan_id: str,
    request_prompt: str,
    response_data: Dict[str, Any]
) -> None:
    """
    Gemini API のリクエスト・レスポンスをJSONファイルに保存
    
    Args:
        plan_id (str): プラン ID
        request_prompt (str): リクエストプロンプト
        response_data (Dict): レスポンスデータ
    """
    # ログディレクトリを確認
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # ファイル名: {plan_id}_{timestamp}.json
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = LOGS_DIR / f"{plan_id}_{timestamp}.json"
    
    # ログデータ構築
    log_data = {
        "plan_id": plan_id,
        "timestamp": datetime.now().isoformat(),
        "request": {
            "prompt": request_prompt
        },
        "response": response_data
    }
    
    # 非同期でファイルに書き込み
    await asyncio.to_thread(
        _write_json_file,
        filename,
        log_data
    )


def _write_json_file(filepath: Path, data: Dict[str, Any]) -> None:
    """
    JSON ファイルに書き込み（同期版）
    
    Args:
        filepath (Path): 書き込み先ファイルパス
        data (Dict): 書き込みデータ
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_gemini_log(plan_id: str, timestamp: str) -> Dict[str, Any]:
    """
    保存済み Gemini ログを読み込み
    
    Args:
        plan_id (str): プラン ID
        timestamp (str): タイムスタンプ
        
    Returns:
        Dict: ログデータ
        
    Raises:
        FileNotFoundError: ログファイルが見つからない場合
    """
    filename = LOGS_DIR / f"{plan_id}_{timestamp}.json"
    
    if not filename.exists():
        raise FileNotFoundError(f"ログファイルが見つかりません: {filename}")
    
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def list_gemini_logs(plan_id: str) -> list:
    """
    特定のプラン ID に対するすべてのログを列挙
    
    Args:
        plan_id (str): プラン ID
        
    Returns:
        list: ログファイルのパスリスト
    """
    if not LOGS_DIR.exists():
        return []
    return sorted(LOGS_DIR.glob(f"{plan_id}_*.json"))
