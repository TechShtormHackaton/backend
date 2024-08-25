import asyncio
import shutil
import os
from fastapi import Depends, UploadFile, HTTPException
from starlette import status
from moviepy.video.io.VideoFileClip import VideoFileClip
from starlette.responses import StreamingResponse

from models.video_path import VideoPath
from models.video_frame import FrameVideo
from repositories.load_file_repository import LoadFileRepository, load_message_repository
from run_model import run_model
from ai.transform import *
from ai.est import image_to_tensor, extract_middle_frame_from_video


class LoadFileService:
    def __init__(self, load_file_repository: LoadFileRepository):
        self.load_file_repository = load_file_repository

    async def process_video_file(self, video: UploadFile):
        try:
            # Сохранение загруженного видео на диск
            video_path = self._save_uploaded_file(video)

            # Сохранение пути к видео в базе данных
            new_video = VideoPath(path=video_path)
            video_path_model = await self.load_file_repository.add_video_path(new_video)

            # Асинхронный запуск задачи по делению видео на части и анализу
            await asyncio.create_task(self._split_video_into_chunks_and_analyze(video_path, video_path_model))

            # Возвращаем успешный ответ немедленно
            return {"status": "success", "message": "Видео успешно загружено и сохранено."}

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при загрузке видео: {str(e)}"
            )

    async def get_stats_from_video_path(self):
        latest_video = await self.load_file_repository.get_latest_video()

    def _save_uploaded_file(self, video: UploadFile) -> str:
        """Сохраняет загруженный видеофайл на диск."""
        video_path = f"{os.getcwd()}/static/{video.filename}"
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        return video_path

    async def _split_video_into_chunks_and_analyze(self, video_path: str, video_path_model: VideoPath,
                                                   chunk_duration: int = 2):
        """Разделяет видео на куски и сохраняет их в базу данных."""
        try:
            video = VideoFileClip(video_path)
            video_duration = int(video.duration)

            base_name = os.path.splitext(os.path.basename(video_path))[0]
            chunks_dir = f"{os.getcwd()}/static/{base_name}_chunks"
            os.makedirs(chunks_dir, exist_ok=True)

            for start_time in range(0, video_duration, chunk_duration):
                end_time = min(start_time + chunk_duration, video_duration)
                await self._process_chunk(video, start_time, end_time, chunks_dir, base_name, video_path_model)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при делении видео на части: {str(e)}"
            )

    async def _process_chunk(self, video, start_time, end_time, chunks_dir, base_name, video_path_model):
        """Создает и сохраняет кусок видео."""
        chunk_filename = f"{chunks_dir}/{base_name}_chunk_{start_time}-{end_time}.mp4"
        chunk = video.subclip(start_time, end_time)
        chunk.write_videofile(chunk_filename, codec="libx264", audio_codec="aac")

        model = tf.keras.models.load_model('video_model_2.1.keras',
                                           custom_objects={'Conv2Plus1D': Conv2Plus1D,
                                                           'ResidualMain': ResidualMain,
                                                           'Project': Project,
                                                           'add_residual_block': add_residual_block,
                                                           'ResizeVideo': ResizeVideo})

        result = run_model(video_file=chunk_filename, model=model)

        middle_frame = extract_middle_frame_from_video(chunk_filename)

        text = image_to_tensor(middle_frame)
        new_frame_video = FrameVideo(
            video_id=video_path_model.id,
            frame_path=chunk_filename,
            throws_state=result if int(result) == 1 else 0,
            power_state=result if int(result) == 2 else 0,
            empty_state=result if int(result) == 0 else 0,
            description=text if text else None
        )
        await self.load_file_repository.add_frame_path(new_frame_video)

    async def get_analysis_results(self):
        latest_video = await self.load_file_repository.get_latest_video()

        if not latest_video:
            raise HTTPException(status_code=404, detail="No video found.")

        unsent_frames = [
            frame for frame in sorted(latest_video.video_frame, key=lambda x: x.id) if not frame.is_send
        ]

        if not unsent_frames:
            return {"message": "All frames have been sent"}

        for frame in unsent_frames:

            data = {
                "throws_state": frame.throws_state,
                "power_state": frame.power_state,
                "empty_state": frame.empty_state,
                "description": frame.description
            }

            frame.is_send = True
            await self.load_file_repository.update_frame_path(frame)

            return {"results": data}


def load_file_service(load_file_repository: LoadFileRepository = Depends(load_message_repository)) -> LoadFileService:
    return LoadFileService(load_file_repository)
