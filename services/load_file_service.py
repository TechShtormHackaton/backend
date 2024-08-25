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

    def _save_uploaded_file(self, video: UploadFile) -> str:
        """Сохраняет загруженный видеофайл на диск."""
        video_path = f"{os.getcwd()}/static/{video.filename}"
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        return video_path

    async def _split_video_into_chunks_and_analyze(self, video_path: str, video_path_model: VideoPath,
                                                   chunk_duration: int = 3):
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

        # Сохранение информации о кусках видео в базе данных
        new_frame_video = FrameVideo(
            video_id=video_path_model.id,
            frame_path=chunk_filename
        )
        await self.load_file_repository.add_frame_path(new_frame_video)

    async def stream_and_analyze_video(self):
        """Стримит последнее видео и анализирует его перед отправкой."""
        try:
            model = tf.keras.models.load_model('video_model_2.1.keras',
                                               custom_objects={'Conv2Plus1D': Conv2Plus1D,
                                                               'ResidualMain': ResidualMain,
                                                               'Project': Project,
                                                               'add_residual_block': add_residual_block,
                                                               'ResizeVideo': ResizeVideo})
            latest_video = await self.load_file_repository.get_latest_video()

            if latest_video is None or not latest_video.video_frame:
                raise HTTPException(status_code=404, detail="No video found.")

            async def stream_generator():
                for frame_video in latest_video.video_frame:
                    chunk_path = frame_video.frame_path

                    # Анализ сегмента с помощью модели
                    result = run_model(video_file=chunk_path, model=model)

                    # Отправка результата анализа
                    yield f"--frame\r\nContent-Type: text/plain\r\n\r\nSegment: {os.path.basename(chunk_path)}, Result: {result}\r\n\r\n"

                    # Отправка видеофайла сегмента
                    with open(chunk_path, "rb") as chunk_file:
                        yield b"--frame\r\nContent-Type: video/mp4\r\n\r\n" + chunk_file.read() + b"\r\n"

            return StreamingResponse(stream_generator(), media_type="multipart/x-mixed-replace; boundary=frame")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error streaming video: {str(e)}")


def load_file_service(load_file_repository: LoadFileRepository = Depends(load_message_repository)) -> LoadFileService:
    return LoadFileService(load_file_repository)
