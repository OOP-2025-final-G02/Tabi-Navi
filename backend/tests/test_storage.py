"""
test_storage.py - ストレージサービステスト
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.db_models import Base, TravelPlanDB
from app.services.plan_storage_service import PlanStorageService
from app.models.travel_plan import TravelPlan, DaySchedule, TimelineItem
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
async def test_save_plan_success(test_db):
    """正常系: プラン保存"""
    plan = TravelPlan(
        plan_id="test-plan-1",
        input_data={"origin": "東京", "destination": "京都"},
        schedules=[],
        total_cost=50000,
        total_duration=1440,
        created_at=datetime.now()
    )
    
    service = PlanStorageService()
    result = await service.save_plan(plan, test_db)
    
    assert result == "test-plan-1"
    
    # DB確認
    saved_plan = test_db.query(TravelPlanDB).filter_by(plan_id="test-plan-1").first()
    assert saved_plan is not None
    assert saved_plan.total_cost == 50000


@pytest.mark.asyncio
async def test_get_plan_success(test_db):
    """正常系: プラン取得"""
    plan = TravelPlan(
        plan_id="test-plan-2",
        input_data={"origin": "東京", "destination": "京都"},
        schedules=[],
        total_cost=50000,
        total_duration=1440,
        created_at=datetime.now()
    )
    
    service = PlanStorageService()
    await service.save_plan(plan, test_db)
    
    retrieved = await service.get_plan("test-plan-2", test_db)
    assert retrieved.plan_id == "test-plan-2"
    assert retrieved.input_data["origin"] == "東京"


@pytest.mark.asyncio
async def test_get_plan_not_found(test_db):
    """異常系: プラン未検出"""
    service = PlanStorageService()
    
    with pytest.raises(Exception):
        await service.get_plan("nonexistent", test_db)


@pytest.mark.asyncio
async def test_get_all_plans(test_db):
    """正常系: プラン一覧取得"""
    # テストデータ追加
    for i in range(3):
        plan = TravelPlanDB(
            plan_id=f"plan-{i}",
            input_data={},
            schedules=[],
            total_cost=10000 * (i + 1),
            total_duration=1440
        )
        test_db.add(plan)
    test_db.commit()
    
    service = PlanStorageService()
    plans = await service.get_all_plans(test_db, limit=10, offset=0)
    
    assert len(plans) == 3


@pytest.mark.asyncio
async def test_delete_plan_success(test_db):
    """正常系: プラン削除"""
    # テストデータ追加
    plan = TravelPlanDB(
        plan_id="test-delete",
        input_data={},
        schedules=[],
        total_cost=50000,
        total_duration=1440
    )
    test_db.add(plan)
    test_db.commit()
    
    service = PlanStorageService()
    result = await service.delete_plan("test-delete", test_db)
    
    assert result is True
    
    # 確認
    deleted = test_db.query(TravelPlanDB).filter_by(plan_id="test-delete").first()
    assert deleted is None


@pytest.mark.asyncio
async def test_count_plans(test_db):
    """正常系: プラン数カウント"""
    # テストデータ追加
    for i in range(5):
        plan = TravelPlanDB(
            plan_id=f"count-test-{i}",
            input_data={},
            schedules=[],
            total_cost=10000,
            total_duration=1440
        )
        test_db.add(plan)
    test_db.commit()
    
    service = PlanStorageService()
    count = await service.count_plans(test_db)
    
    assert count == 5
