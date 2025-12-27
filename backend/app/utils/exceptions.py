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
