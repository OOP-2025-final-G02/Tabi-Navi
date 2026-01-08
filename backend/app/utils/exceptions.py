"""
カスタム例外定義
"""


class PlanNotFoundError(Exception):
    """プランが見つからない場合の例外"""
    pass


class DatabaseError(Exception):
    """データベース操作エラーの例外"""
    pass


class ValidationError(Exception):
    """バリデーションエラーの例外"""
    pass


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