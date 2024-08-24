import asyncio
from models.video_path import VideoPath
from models.frame_video import FrameVideo
from moviepy.video.io.VideoFileClip import VideoFileClip
from ai.transform import *
from repositories.load_file_repository import LoadFileRepository, load_message_repository
from fastapi import Depends, UploadFile, HTTPException
from starlette import status
import shutil
import os

from run_model import run_model


class LoadFileService:
    def __init__(self, load_file_repository: LoadFileRepository):
        self.load_file_repository = load_file_repository

    async def process_video_file(self, video: UploadFile):
        try:
            video_path = f"{os.getcwd()}/static/{video.filename}"

            with open(video_path, "wb") as buffer:
                shutil.copyfileobj(video.file, buffer)

                new_video = VideoPath(
                    path=video_path,
                )

                video_path_model = await self.load_file_repository.add_video_path(new_video)

            await self.__split_video_into_chunks_and_analyze(video_path, video_path_model)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при загрузке видео: {str(e)}"
            )

    async def __split_video_into_chunks_and_analyze(self, video_path: str, video_path_model: VideoPath,
                                                    chunk_duration: int = 5):
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

        new_frame_video = FrameVideo(
            video_id=video_path_model.id,
            frame_path=chunk_filename
        )

        await self.load_file_repository.add_frame_path(new_frame_video)


def load_file_service(load_file_repository: LoadFileRepository = Depends(load_message_repository)) -> LoadFileService:
    return LoadFileService(load_file_repository)
