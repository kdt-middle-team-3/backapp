from datetime import date, datetime

from pydantic import Field, field_serializer, field_validator

from app.schema.common_schema import BaseDTO
from app.util.date_util import KST, kst_day_range, today_kst


# 결정-14(본문 길이, 지난·미래 날짜 허용)는 아직 미정이다. 팀 결정이 나오면 아래 값만 바꾼다.
DIARY_CONTENT_MAX = 5000      # 본문 최대 글자 수 (ERD 는 TEXT 라 제한이 없으므로 API 에서 막는다)
ALLOW_FUTURE_DATE = False     # 미래 날짜 일기 허용 여부
DIARY_PAST_DAYS_MAX: int | None = None    # 지난 날짜 허용 일수 (None: 제한 없음, ERD 주석대로면 7)


# date -> diaries.diary_date(DATETIME) 저장값: KST 자정으로 통일 (서비스에서 사용)
def diary_date_to_datetime(value: date) -> datetime:
    return kst_day_range(value)[0]


# DB 의 datetime -> KST 기준 datetime (시간대 정보가 없으면 KST 로 저장된 값으로 본다)
def _as_kst(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=KST)
    return value.astimezone(KST)


# ──────────────────────────────── 요청 ────────────────────────────────

# 일기 쓰기 요청 (기록-01: 입력 = 날짜, 본문)
# - 작성자(user_id)는 바디로 받지 않고 로그인 사용자에서 꺼낸다.
# - diaryDate 를 보내지 않으면 오늘(KST) 일기로 저장한다.
class DiaryCreateDTO(BaseDTO):
    diary_date: date = Field(default_factory=today_kst, description="일기 날짜 (YYYY-MM-DD)")
    content: str = Field(max_length=DIARY_CONTENT_MAX, description="일기 본문")

    @field_validator("content")
    @classmethod
    def strip_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("일기 내용을 입력하세요.")
        return value

    @field_validator("diary_date")
    @classmethod
    def check_date_range(cls, value: date) -> date:
        days_ago = (today_kst() - value).days
        if not ALLOW_FUTURE_DATE and days_ago < 0:
            raise ValueError("미래 날짜의 일기는 쓸 수 없습니다.")
        if DIARY_PAST_DAYS_MAX is not None and days_ago > DIARY_PAST_DAYS_MAX:
            raise ValueError(f"지난 일기는 최근 {DIARY_PAST_DAYS_MAX}일까지만 쓸 수 있습니다.")
        return value


# ──────────────────────────────── 응답 ────────────────────────────────

# 일기 쓰기 성공 응답 (기록-01: 출력 = 저장된 일기)
# - 보안-01: 환자에게 분석 결과를 보여 주지 않으므로 감정 점수·대표 감정은 넣지 않는다.
class DiaryCreateResponseDTO(BaseDTO):
    diary_id: int
    diary_date: date
    content: str
    created_at: datetime

    @field_validator("diary_date", mode="before")
    @classmethod
    def to_date(cls, value: datetime | date) -> date:
        if isinstance(value, datetime):
            return _as_kst(value).date()
        return value

    @field_serializer("created_at")
    def to_kst(self, value: datetime) -> datetime:
        return _as_kst(value)


# 같은 날 일기가 이미 있을 때 (기록-01 예외: 새로 쓰지 않고 고치기로 안내)
# - 409 응답 본문. 프론트는 existingDiaryId 로 고치기 화면으로 보낸다.
class DiaryDuplicateDTO(BaseDTO):
    message: str = "이미 이 날짜에 쓴 일기가 있어요. 고치기로 이동할까요?"
    existing_diary_id: int
    diary_date: date
