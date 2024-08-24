import asyncio
import shutil

from models.video_path import VideoPath
from moviepy.video.io.VideoFileClip import VideoFileClip
from ai.transform import *
from repositories.load_file_repository import LoadFileRepository, load_message_repository
from fastapi import Depends, UploadFile, HTTPException
from starlette import status
import os

from run_model import run_model


class LoadFileService:
    def __init__(self, load_file_repository: LoadFileRepository):
        self.load_file_repository = load_file_repository

    async def process_video_file(self, video: UploadFile):
        # Загружаем модель
        model = tf.keras.models.load_model('video_model.keras',
                                           custom_objects={'Conv2Plus1D': Conv2Plus1D,
                                                           'ResidualMain': ResidualMain,
                                                           'Project': Project,
                                                           'add_residual_block': add_residual_block,
                                                           'ResizeVideo': ResizeVideo})

        video_path = f"{os.getcwd()}/static/{video.filename}"
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)

        existing_video = await self.load_file_repository.get_video_by_name(video.filename)

        if not existing_video:
            existing_video = VideoPath(video_name=video.filename)
            await self.load_file_repository.add_video_path(existing_video)

        # Запускаем модель и получаем статистику
        statistic = run_model(video_file=video_path, model=model)

        if statistic == 1:
            existing_video.throws += 1
        elif statistic == 2:
            existing_video.power_state += 1
        else:
            existing_video.empty_state += 1

        await self.load_file_repository.update_models()

        return await self.__get_total_stats(video.filename)

    async def __get_total_stats(self, video_name: str):
        videos = await self.load_file_repository.get_videos_by_name(video_name)

        total_stats = {
            "total_faceoff": sum(video.throws for video in videos),
            "total_priemy": sum(video.power_state for video in videos),
            "total_empty": sum(video.empty_state for video in videos),
        }

        return total_stats

    async def __split_video_into_chunks_and_analyze(self, video_path: str, video_path_model: VideoPath,
                                                    chunk_duration: int = 3):
        try:
            video = VideoFileClip(video_path)
            video_duration = int(video.duration)

            base_name = os.path.splitext(os.path.basename(video_path))[0]
            chunks_dir = f"{os.getcwd()}/static/{base_name}_chunks"
            os.makedirs(chunks_dir, exist_ok=True)

            for start_time in range(0, video_duration, chunk_duration):
                end_time = min(start_time + chunk_duration, video_duration)
                await self.__process_chunk(video, start_time, end_time, chunks_dir, base_name, video_path_model)


        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при делении видео на части: {str(e)}"
            )

    async def __process_chunk(self, video, start_time, end_time, chunks_dir, base_name, video_path_model):
        chunk_filename = f"{chunks_dir}/{base_name}_chunk_{start_time}-{end_time}.mov"
        chunk = video.subclip(start_time, end_time)
        chunk.write_videofile(chunk_filename, codec="libx264", audio_codec="aac")


def load_file_service(load_file_repository: LoadFileRepository = Depends(load_message_repository)) -> LoadFileService:
    return LoadFileService(load_file_repository)
