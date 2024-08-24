import asyncio
import os

from moviepy.video.io.VideoFileClip import VideoFileClip


def __split_video_into_chunks_and_analyze(video_path: str, chunk_duration: int = 3):
    try:
        video = VideoFileClip(video_path)
        video_duration = int(video.duration)

        base_name = os.path.splitext(os.path.basename(video_path))[0]
        chunks_dir = f"{os.getcwd()}/static/{base_name}_chunks"
        os.makedirs(chunks_dir, exist_ok=True)

        for start_time in range(0, video_duration, chunk_duration):
            end_time = min(start_time + chunk_duration, video_duration)
            __process_chunk(video, start_time, end_time, chunks_dir, base_name)

    except Exception as e:
        print(e)


def __process_chunk(video, start_time, end_time, chunks_dir, base_name):
    chunk_filename = f"{chunks_dir}/{base_name}_chunk_{start_time}-{end_time}.mov"
    chunk = video.subclip(start_time, end_time)
    chunk.write_videofile(chunk_filename, codec="libx264", audio_codec="aac")


video = "Овечкин,_Романов_и_Ткачак_ТОП_10_силовых_приёмов_НХЛ_сезона_2022.mp4"

__split_video_into_chunks_and_analyze(video)