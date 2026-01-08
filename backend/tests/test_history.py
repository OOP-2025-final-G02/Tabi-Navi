"""
test_history.py - 履歴管理サービステスト
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.db_models import Base, TimelineItemHistory
from app.services.history_service import HistoryService
from datetime import datetime

# テスト用DB（メモリ）
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
Base.metadata.create_all(bind=engine)
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture
def test_db():
    """テスト用DBセッション"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.mark.asyncio
async def test_record_edit_success(test_db):
    """正常系: 編集操作を記録"""
    service = HistoryService()
    
    history_id = await service.record_edit(
        plan_id="test-plan-1",
        day=1,
        item_index=0,
        operation_type="update",
        field_changed="time",
        original_data={"time": "09:00"},
        updated_data={"time": "10:00"},
        db=test_db
    )
    
    assert history_id is not None
    
    # DB確認
    history = test_db.query(TimelineItemHistory).filter_by(id=history_id).first()
    assert history is not None
    assert history.operation_type == "update"


@pytest.mark.asyncio
async def test_get_history_success(test_db):
    """正常系: 編集履歴取得"""
    service = HistoryService()
    
    # 複数の履歴記録
    for i in range(3):
        await service.record_edit(
            plan_id="test-plan-2",
            day=1,
            item_index=i,
            operation_type="update",
            field_changed=f"field_{i}",
            db=test_db
        )
    
    histories = await service.get_history("test-plan-2", test_db)
    assert len(histories) == 3


@pytest.mark.asyncio
async def test_get_history_by_day(test_db):
    """正常系: 特定日の履歴取得"""
    service = HistoryService()
    
    # 異なる日の履歴記録
    await service.record_edit(
        plan_id="test-plan-3",
        day=1,
        item_index=0,
        operation_type="update",
        db=test_db
    )
    
    await service.record_edit(
        plan_id="test-plan-3",
        day=2,
        item_index=0,
        operation_type="insert",
        db=test_db
    )
    
    day1_histories = await service.get_history_by_day("test-plan-3", 1, test_db)
    day2_histories = await service.get_history_by_day("test-plan-3", 2, test_db)
    
    assert len(day1_histories) == 1
    assert len(day2_histories) == 1


@pytest.mark.asyncio
async def test_get_history_count(test_db):
    """正常系: 編集回数カウント"""
    service = HistoryService()
    
    # 履歴記録
    for i in range(5):
        await service.record_edit(
            plan_id="test-plan-4",
            day=1,
            item_index=i,
            operation_type="update",
            db=test_db
        )
    
    count = await service.get_history_count("test-plan-4", test_db)
    assert count == 5


@pytest.mark.asyncio
async def test_clear_history_success(test_db):
    """正常系: 履歴クリア"""
    service = HistoryService()
    
    # 履歴記録
    for i in range(3):
        await service.record_edit(
            plan_id="test-plan-5",
            day=1,
            item_index=i,
            operation_type="update",
            db=test_db
        )
    
    # クリア
    deleted_count = await service.clear_history("test-plan-5", test_db)
    assert deleted_count == 3
    
    # 確認
    count = await service.get_history_count("test-plan-5", test_db)
    assert count == 0
