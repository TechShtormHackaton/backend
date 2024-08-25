import io

import numpy as np
from moviepy.video.io.VideoFileClip import VideoFileClip
from transformers import AutoProcessor, AutoModelForVision2Seq
from PIL import Image


def extract_middle_frame_from_video(video_path):
    """Извлекает кадр из середины видео и возвращает его как изображение PIL."""
    with VideoFileClip(video_path) as video:
        middle_time = video.duration / 2  # Время середины видео
        frame = video.get_frame(middle_time)  # Извлекаем кадр из середины
        image = Image.fromarray(np.uint8(frame))  # Преобразуем массив numpy в изображение PIL
    return image


def image_to_tensor(image: Image.Image):
    # Сохраняем изображение в буфер в формате JPEG
    image_buffer = io.BytesIO()
    image.save(image_buffer, format='JPEG')
    image_buffer.seek(0)  # Возвращаем курсор в начало буфера

    model = AutoModelForVision2Seq.from_pretrained("tf_save_pretrained_model")
    processor = AutoProcessor.from_pretrained("tf_save_pretrained_processor")

    prompt = "Description of ice hockey game:"

    # Читаем изображение из буфера
    image_bytes = image_buffer.read()
    image_buffer.seek(0)

    # Преобразуем байты обратно в изображение для дальнейшей обработки
    image = Image.open(io.BytesIO(image_bytes))

    inputs = processor(text=prompt, images=image, return_tensors="pt")

    generated_ids = model.generate(
        pixel_values=inputs["pixel_values"],
        input_ids=inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        image_embeds=None,
        image_embeds_position_mask=inputs["image_embeds_position_mask"],
        use_cache=True,
        max_new_tokens=128,
    )
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    processed_text = processor.post_process_generation(generated_text, cleanup_and_extract=False)
    processed_text, entities = processor.post_process_generation(generated_text)

    return processed_text
