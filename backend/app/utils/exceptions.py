"""
カスタム例外定義
"""


class ApplicationException(Exception):
    """アプリケーション例外の基底クラス"""
    pass


class GeminiAPIError(ApplicationException):
    """Gemini API エラー"""
    pass


class ValidationError(ApplicationException):
    """データ検証エラー"""
    pass


class PlanGenerationError(ApplicationException):
    """旅行プラン生成エラー"""
    pass
