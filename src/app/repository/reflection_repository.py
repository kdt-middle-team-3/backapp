from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.infrastructure.postgresql import get_postgresql_db
from datetime import date
from sqlalchemy import select

#모델, ORM
from app.models.emotion_record_model import EmotionRecord


# 마음 돌아보기 (주간/월간 감정 분석 집계) DB 접근
class ReflectionRepository:

    # 생성자 주입
    def __init__(self, db: AsyncSession):
        self.db = db

    # TODO: 조회/저장 쿼리 추가
    #1. 기간 [start,end] 안의 내 기록(안 지운 것만, 날짜순) - 주간, 월간 모두 이거 하나로
    async def find_records_in_range(
            self, user_id: int, start: date, end: date
    ) -> list[EmotionRecord]:
        query = (
            select(EmotionRecord)
            .where(
                EmotionRecord.user_id == user_id,
                EmotionRecord.record_date >= start,
                EmotionRecord.record_date < end,
                EmotionRecord.deleted_at.is_(None)
            )
            .order_by(EmotionRecord.record_date)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())


def get_reflection_repository(db: AsyncSession = Depends(get_postgresql_db)) -> ReflectionRepository:
    return ReflectionRepository(db)
