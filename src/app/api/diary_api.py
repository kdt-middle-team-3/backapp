from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.service.diary_service import get_diary_service, DiaryService
from app.schema.user_schema import UserClaimDTO
from app.schema.diary_schema import (
    DiaryCreateDTO,
    DiaryCreateResponseDTO,
    DiaryDuplicateDTO,
)
from app.schema.common_schema import ApiResponseDTO
from app.dependencie.auth_dependency import get_current_user


# 환자 일기 (기록-01)
# - main.py에서 prefix="/diaries"로 등록한다.
# - 로그인한 사용자 본인의 일기만 다룬다.
router = APIRouter()


# 1. 일기 쓰기
@router.post(
    "",
    summary="일기 쓰기 (하루 1개)",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponseDTO[DiaryCreateResponseDTO],
    responses={409: {"model": DiaryDuplicateDTO, "description": "같은 날 일기가 이미 있음"}}
)
async def create_diary(
    request: DiaryCreateDTO,
    current_user: UserClaimDTO = Depends(get_current_user),
    diary_service: DiaryService = Depends(get_diary_service)
):
    result = await diary_service.create_diary(current_user.id, request)

    if isinstance(result, DiaryDuplicateDTO):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=result.model_dump(mode="json", by_alias=True)
        )

    return ApiResponseDTO(
        success=True,
        message="일기 저장 완료",
        data=result
    )
