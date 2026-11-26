from fastapi import Depends, HTTPException, status
from app.repository.diary_repository import DiaryRepository, get_diary_repository
from app.schema.diary_schema import (
    DiaryCreateDTO,
    DiaryCreateResponseDTO,
    DiaryDuplicateDTO,
    diary_date_to_datetime,
)
from app.util.date_util import kst_day_range


# 예외처리, 서비스가 드러나도록 이름을 선정해서 제작
# 트랜잭션 관리
class DiaryService:

    def __init__(self, repo: DiaryRepository):
        self.repo = repo


    # 1. 일기 쓰기 (기록-01)
    # - 같은 날 일기가 있으면 새로 쓰지 않고 DiaryDuplicateDTO를 돌려준다. (라우터에서 409)
    async def create_diary(
        self, user_id: int, request: DiaryCreateDTO
    ) -> DiaryCreateResponseDTO | DiaryDuplicateDTO:
        start_at, end_at = kst_day_range(request.diary_date)

        existing = await self.repo.find_diary_by_range(user_id, start_at, end_at)

        if not existing:
            diary = await self.repo.create_diary(
                user_id, diary_date_to_datetime(request.diary_date), request.content
            )
            if diary:
                return DiaryCreateResponseDTO.model_validate(diary)

            # 저장 실패: 확인과 저장 사이에 다른 요청이 같은 날 일기를 먼저 저장한 경우
            existing = await self.repo.find_diary_by_range(user_id, start_at, end_at)
            if not existing:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="일기를 저장하지 못했습니다."
                )

        return DiaryDuplicateDTO(
            existing_diary_id=existing.diary_id,
            diary_date=request.diary_date
        )



# 레포지토리 주입 팩토리 함수
def get_diary_service(repo: DiaryRepository = Depends(get_diary_repository)):
    return DiaryService(repo)
