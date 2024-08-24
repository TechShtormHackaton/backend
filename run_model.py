from ai.transform import *


def run_model(video_file, model):
    n_frames = 10
    batch_size = 1

    output_signature = (tf.TensorSpec(shape=(None, None, None, 3), dtype=tf.float32),
                        tf.TensorSpec(shape=(), dtype=tf.int16))

    test_video = tf.data.Dataset.from_generator(FrameGenerator(video_file, n_frames),
                                                output_signature=output_signature)

    test_video = test_video.batch(batch_size)

    predicted = model.predict(test_video)
    predicted = tf.argmax(predicted, axis=1)

    predicted = predicted.numpy()[0]

    return predicted

