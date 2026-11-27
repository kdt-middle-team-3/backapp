from fastapi import APIRouter, Depends
from app.service.reflection_service import get_reflection_service, ReflectionService
from app.schema.user_schema import UserClaimDTO
from app.dependencie.auth_dependency import get_current_user
from datetime import date
from fastapi import Query
from app.schema.common_schema import ApiResponseDTO
from app.schema.reflection_schema import WeeklyReflectionResponseDTO, MonthlyReflectionResponseDTO


router = APIRouter()

# TODO: 마음 돌아보기 (주간/월간 감정 분석 집계) 엔드포인트 추가


# 1. 이번 주 돌아보기 - date가 있는 주(월~일), 없으면 이번 주
@router.get(
    "/week",
    summary="이번 주 마음 돌아보기",
    response_model=ApiResponseDTO[WeeklyReflectionResponseDTO]
)
async def get_week_reflection(
    day: date | None = Query(default=None, alias="date", description="이 날짜가 있는 주. 없으면 이번 주 (예: 2026-11-27)"),
    current_user: UserClaimDTO = Depends(get_current_user),
    service: ReflectionService = Depends(get_reflection_service)
):
    data = await service.get_week(current_user.id, day)
    return ApiResponseDTO(success=True, message="이번 주 마음 돌아보기 조회 완료", data=data)


# 2. 이번 달 돌아보기 - month가 없으면 이번 달
@router.get(
    "/month",
    summary="이번 달 마음 돌아보기",
    response_model=ApiResponseDTO[MonthlyReflectionResponseDTO]
)
async def get_month_reflection(
    month: str | None = Query(default=None, description="YYYY-MM 형식. 없으면 이번 달 (예: 2026-11)"),
    current_user: UserClaimDTO = Depends(get_current_user),
    service: ReflectionService = Depends(get_reflection_service)
):
    data = await service.get_month(current_user.id, month)
    return ApiResponseDTO(success=True, message="이번 달 마음 돌아보기 조회 완료", data=data)