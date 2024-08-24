from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from moviepy.video.io.VideoFileClip import VideoFileClip
import asyncio
import io
from PIL import Image
from ai.transform import *
from managers.web_socket_manager import connection_manager
from services.ws_service import WebSocketService, get_ws_service
from run_model import run_model
from models import VideoPath

router = APIRouter(
    prefix="/api/v1",
    tags=["WebSockets"],
)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, service: WebSocketService = Depends(get_ws_service)):
    await connection_manager.connect(websocket)

    path = await service.get_path()

    try:
        video_path = path
        await send_video_and_statistics(video_path, websocket)

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)


async def send_video_and_statistics(video_path: VideoPath, websocket: WebSocket):
    try:
        model = tf.keras.models.load_model('video_model.keras',
                                           custom_objects={'Conv2Plus1D': Conv2Plus1D,
                                                           'ResidualMain': ResidualMain,
                                                           'Project': Project,
                                                           'add_residual_block': add_residual_block,
                                                           'ResizeVideo': ResizeVideo})

        for frame_video in video_path.video_frame:

            result_ai = run_model(frame_video.frame_path, model)

            if isinstance(result_ai, np.int64):
                result_ai = int(result_ai)

            video = VideoFileClip(frame_video.frame_path)
            duration = video.duration

            for t in range(0, int(duration), 1):
                frame = video.get_frame(t)

                # Преобразуем кадр в изображение JPEG и оборачиваем в байты
                image = Image.fromarray(frame)
                buffer = io.BytesIO()
                image.save(buffer, format="JPEG")
                frame_data = buffer.getvalue()

                await websocket.send_bytes(frame_data)

            await websocket.send_json({"result": result_ai})

            await asyncio.sleep(1)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        video.close()
