from fastapi import Depends
from app.repository.reflection_repository import ReflectionRepository, get_reflection_repository
from datetime import date, timedelta
from fastapi import HTTPException, status
from app.models.emotion_record_model import EmotionRecord
from app.util.date_util import today_kst, week_range, month_range
from app.util.reflection_util import (
    fill_empty_days,
    count_tags,
    count_weather,
    best_record,
    week_message,
    month_message,
)
from app.schema.reflection_schema import (
    ReflectionDayResponseDTO,
    WeeklyReflectionResponseDTO,
    MonthlyReflectionResponseDTO,
)


# 마음 돌아보기 (주간/월간 감정 분석 집계) 비즈니스 로직, 예외 처리, 트랜잭션 관리
class ReflectionService:

    def __init__(self, repo: ReflectionRepository):
        self.repo = repo

    # TODO: 서비스 메서드 추가

    #기록 1개: 하루 칸 DTO (칼럼 이름 record_date와 DTO 이름 day가 달라서 직접 옮긴다.)
    @staticmethod
    def _to_day(record: EmotionRecord) -> ReflectionDayResponseDTO:
        return ReflectionDayResponseDTO(
            day=record.record_date,
            mood_score=record.mood_score,
            mood_tag=record.mood_tag,
            memo=record.memo
        )

    #------기능-------
    async def get_week(self,user_id: int, day:date|None=None)-> WeeklyReflectionResponseDTO:
        start, end = week_range(day or today_kst())
        records = await self.repo.find_records_in_range(user_id, start, end)

        tag_counts = count_tags(records)
        top_tag = tag_counts[0]["tag"] if tag_counts else None
        headline, sub_message = week_message(top_tag, len(records))
        best = best_record(records)

        return WeeklyReflectionResponseDTO(
            start=start,
            end=end - timedelta(days=1),                      # 다음 주 월요일 -> 이번 주 일요일
            recorded_days=len(records),
            top_tag=top_tag,
            headline=headline,
            sub_message=sub_message,
            days=fill_empty_days(records, start, end),
            best_day=self._to_day(best) if best else None,
            tag_counts=tag_counts,
            records=[self._to_day(r) for r in reversed(records)]   # 최신순
        )

    #2. 이번 달 돌아보기 - month("2026-11"), 없으면 이번 달
    async def get_month(self, user_id: int, month: str | None = None) -> MonthlyReflectionResponseDTO:
        try:
            start, end = month_range(month or today_kst().strftime("%Y-%m"))
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="month는 2026-11 같은 형식으로 보내 주세요."
            )
        records = await self.repo.find_records_in_range(user_id, start, end)
        headline, sub_message = month_message(start.month, len(records))

        return MonthlyReflectionResponseDTO(
            month=start.strftime("%Y-%m"),
            recorded_days=len(records),
            headline=headline,
            sub_message=sub_message,
            days=fill_empty_days(records, start, end),
            weather_counts=count_weather(records)
        )

    
    


def get_reflection_service(repo: ReflectionRepository = Depends(get_reflection_repository)) -> ReflectionService:
    return ReflectionService(repo)
