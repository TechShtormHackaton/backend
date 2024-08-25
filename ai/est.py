from transformers import AutoProcessor, AutoModelForVision2Seq
from PIL import Image


def image_to_tensor(image):
    model = AutoModelForVision2Seq.from_pretrained("../tf_save_pretrained_model")

    processor = AutoProcessor.from_pretrained('../tf_save_pretrained_processor')

    image = Image.open("first_frame.jpg")

    prompt = "Description of KHL hockey game:"

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
