from fastapi import APIRouter, File, UploadFile, Depends
from services.load_file_service import load_file_service, LoadFileService

router = APIRouter(
    prefix="/api/v1",
    tags=["Загрузка видео"],
)


@router.post("/video-file", summary="Загрузка видео")
async def get_video_file(video: UploadFile = File(...),
                         service: LoadFileService = Depends(load_file_service)):
    status = await service.process_video_file(video)
    return status


@router.get("/stream", summary="Стриминг и анализ последнего видео")
async def stream_video(service: LoadFileService = Depends(load_file_service)):
    return await service.stream_and_analyze_video()