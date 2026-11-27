from collections import Counter
from datetime import date, timedelta
from app.models.emotion_record_model import EmotionRecord

# 마음 돌아보기 계산 함수 모음(DB, FastAPI 모름. 기록 목록을 넣으면 숫자, 문장이 나온다.)

#태그별 한마디
WEEK_MESSAGES = {
    "평온": "잔잔한 마음이 머문 한 주였어요",
    "기쁨": "기뻤던 순간을 기억해 두면 힘이 돼요",
    "감사": "고마운 마음을 알아차린 한 주였어요",
    "설렘": "기대되는 일이 마음을 두드렸나 봐요",
    "뿌듯함": "스스로를 칭찬해 주고 싶은 날이 있었네요",
    "피곤": "몸과 마음이 쉬어 가고 싶다는 신호일 수 있어요",
    "불안": "불안한 마음도 알아차린 것만으로 충분해요",
    "우울": "무거운 마음을 남겨 준 것만으로도 소중해요",
    "외로움": "마음을 나눌 누군가가 떠오른다면 연락해 봐도 좋아요",
    "무기력": "오늘은 작은 돌봄 하나만 해도 충분해요",
}
DEFAULT_SUB_MESSAGE = "맑은 날도 흐린 날도 모두 소중한 기록이에요"
EMPTY_HEADLINE = "아직 남긴 마음이 없어요"
EMPTY_SUB_MESSAGE = "오늘 마음 날씨부터 가볍게 남겨 볼까요?"


# 1. 점수 -> 날씨 묶음 (캘린더 mood_level과 같은 기준: 4~5 맑음, 3 구름, 1~2 흐림)
def weather_level(score: int) -> str:
    if score >= 4:
        return "good"
    if score == 3:
        return "neutral"
    return "bad"

# 2. 기간 [start, end)의 날짜마다 1칸. 기록 없는 날은 점수·태그·메모가 None (앱이 점선/빈칸으로 그림)
def fill_empty_days(records: list[EmotionRecord], start: date, end: date) -> list[dict]:
    by_day = {r.record_date: r for r in records}
    days = []
    day = start
    while day < end:
        r = by_day.get(day)
        days.append({
            "day": day,
            "mood_score": r.mood_score if r else None,
            "mood_tag": r.mood_tag if r else None,
            "memo": r.memo if r else None,
        })
        day += timedelta(days=1)
    return days


# 3. 태그별 일수, 많은 순 (태그 안 고른 날은 세지 않음)
def count_tags(records: list[EmotionRecord]) -> list[dict]:
    counter = Counter(r.mood_tag for r in records if r.mood_tag)
    return [{"tag": tag, "count": count} for tag, count in counter.most_common()]


# 4. 맑은 날 / 구름 낀 날 / 흐린 날 일수
def count_weather(records: list[EmotionRecord]) -> dict:
    counts = {"good": 0, "neutral": 0, "bad": 0}
    for r in records:
        counts[weather_level(r.mood_score)] += 1
    return counts


# 5. 가장 맑았던 날 (점수가 같으면 더 최근 날). 기록이 없으면 None
def best_record(records: list[EmotionRecord]) -> EmotionRecord | None:
    if not records:
        return None
    return max(records, key=lambda r: (r.mood_score, r.record_date))


# 6. 이번 주 문장 (제목, 한마디)
def week_message(top_tag: str | None, recorded_days: int) -> tuple[str, str]:
    if recorded_days == 0:
        return EMPTY_HEADLINE, EMPTY_SUB_MESSAGE
    if top_tag is None:
        return f"이번 주엔 {recorded_days}일 마음을 남겼어요", DEFAULT_SUB_MESSAGE
    return f"이번 주엔 '{top_tag}' 마음을 자주 남겼어요", WEEK_MESSAGES.get(top_tag, DEFAULT_SUB_MESSAGE)


# 7. 이번 달 문장 (제목, 한마디)
def month_message(month: int, recorded_days: int) -> tuple[str, str]:
    if recorded_days == 0:
        return EMPTY_HEADLINE, EMPTY_SUB_MESSAGE
    return f"{month}월엔 {recorded_days}일 마음을 남겼어요", DEFAULT_SUB_MESSAGE