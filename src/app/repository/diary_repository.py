from datetime import datetime
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.postgresql import get_postgresql_db
from fastapi import Depends

# 모델, ORM
from app.models.diary_model import Diary


class DiaryRepository:

    # 생성자 주입
    def __init__(self, db: AsyncSession):
        self.db = db


    # 1. 그날 일기 조회 (시각 [start_at, end_at), 삭제 제외)
    async def find_diary_by_range(self, user_id: int, start_at: datetime, end_at: datetime) -> Diary | None:
        query = (
            select(Diary)
            .where(
                Diary.user_id == user_id,
                Diary.deleted_at.is_(None),
                Diary.diary_date >= start_at,
                Diary.diary_date < end_at
            )
            .order_by(Diary.diary_id.desc())
            .limit(1)
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()


    # 2. 일기 작성 -> 저장된 일기
    # - 제약 조건에 걸리면(동시에 같은 날 저장 등) None
    async def create_diary(self, user_id: int, diary_date: datetime, content: str) -> Diary | None:
        diary = Diary(user_id=user_id, diary_date=diary_date, content=content)
        self.db.add(diary)

        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            return None

        return diary



# 주입 팩토리 메서드
def get_diary_repository(db: AsyncSession = Depends(get_postgresql_db)):
    return DiaryRepository(db)
