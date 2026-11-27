from app.schema.common_schema import BaseDTO
from datetime import date

# 마음 돌아보기 (주간/월간 감정 분석 집계) 요청/응답 DTO
# 규칙: BaseDTO 상속, XxxCreateDTO / XxxUpdateDTO / XxxResponseDTO 이름 사용

# TODO: DTO 추가

#하루 1칸 (그래프, 달력, 기록 목록에 공통으로 사용) 기록 없는 날은 점수, 태그, 메모가 null
class ReflectionDayResponseDTO(BaseDTO):
    day: date
    mood_score: int|None=None
    mood_tag: str|None=None
    memo: str|None=None

#자주 느낀 마음 - 태그 1개와 일수
class TagCountResponseDTO(BaseDTO):
    tag:str
    count:int

#마음 날씨 막대 - 맑은 날(4~5)/구름 낀 날(3)/ 흐린 날(1~2)일수
class WeatherCountResponseDTO(BaseDTO):
    good: int
    neutral: int
    bad: int

# 이번 주 돌아보기(월~일)
class WeeklyReflectionResponseDTO(BaseDTO):
    start: date                                  # 월요일
    end: date                                    # 일요일
    recorded_days: int                           # 기록한 날 수
    top_tag: str | None = None                   # 가장 많이 고른 태그 (없으면 null)
    headline: str                                # 이번 주 마음 카드 제목
    sub_message: str                             # 이번 주 마음 카드 한마디
    days: list[ReflectionDayResponseDTO]         # 월~일 7칸 (마음 흐름 그래프)
    best_day: ReflectionDayResponseDTO | None = None   # 가장 맑았던 날 (한 줄 하이라이트)
    tag_counts: list[TagCountResponseDTO]        # 자주 느낀 마음 (많은 순)
    records: list[ReflectionDayResponseDTO]      # 이번 주 기록 목록 (기록 있는 날만, 최신순)

# 이번 달 몰아보기
class MonthlyReflectionResponseDTO(BaseDTO):
    month: str                                   # "2026-11"
    recorded_days: int                           # 기록한 날 수
    headline: str                                # N월 마음 카드 제목
    sub_message: str                             # N월 마음 카드 한마디
    days: list[ReflectionDayResponseDTO]         # 그 달 날짜 수만큼 (달력)
    weather_counts: WeatherCountResponseDTO      # N월 마음 날씨 막대
