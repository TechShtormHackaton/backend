import random

import cv2
import numpy as np

import tensorflow as tf
import keras
from keras import layers
import einops


class CreateFrames:

    @staticmethod
    def format_frames(frame, output_size):
        """
          Pad and resize an image from a video.

          Args:
            frame: Image that needs to resized and padded.
            output_size: Pixel size of the output frame image.

          Return:
            Formatted frame with padding of specified output size.
        """

        frame = tf.image.convert_image_dtype(frame, tf.float32)
        frame = tf.image.resize_with_pad(frame, *output_size)
        return frame

    @staticmethod
    def frames_from_video_file(video_path, n_frames, output_size=(224, 224), frame_step=15):
        """
          Creates frames from each video file present for each category.

          Args:
            video_path: File path to the video.
            n_frames: Number of frames to be created per video file.
            output_size: Pixel size of the output frame image.

          Return:
            An NumPy array of frames in the shape of (n_frames, height, width, channels).
        """
        # Read each video frame by frame
        result = []
        src = cv2.VideoCapture(str(video_path))

        video_length = src.get(cv2.CAP_PROP_FRAME_COUNT)

        need_length = 1 + (n_frames - 1) * frame_step

        if need_length > video_length:
            start = 0
        else:
            max_start = video_length - need_length
            start = random.randint(0, max_start + 1)

        src.set(cv2.CAP_PROP_POS_FRAMES, start)
        # ret is a boolean indicating whether read was successful, frame is the image itself
        ret, frame = src.read()
        result.append(CreateFrames.format_frames(frame, output_size))

        for _ in range(n_frames - 1):
            for _ in range(frame_step):
                ret, frame = src.read()
            if ret:
                frame = (CreateFrames.format_frames(frame, output_size))
                result.append(frame)
            else:
                result.append(np.zeros_like(result[0]))
        src.release()
        result = np.array(result)[..., [2, 1, 0]]

        yield result, 0


class FrameGenerator:
    """ Returns a set of frames with their associated label.

        Args:
          video: Video file paths.
          n_frames: Number of frames.
          training: Boolean to determine if training dataset is being created.
      """

    def __init__(self, video, n_frames):
        self.video = video
        self.n_frames = n_frames

    def __call__(self):
        video_frames = CreateFrames.frames_from_video_file(self.video, self.n_frames)

        return video_frames


@keras.saving.register_keras_serializable()
class Conv2Plus1D(keras.layers.Layer):
    def __init__(self, filters, kernel_size, padding, **kwargs):
        """
      A sequence of convolutional layers that first apply the convolution operation over the
      spatial dimensions, and then the temporal dimension.
    """
        super().__init__(**kwargs)
        self.seq = keras.Sequential([
            # Spatial decomposition
            layers.Conv3D(filters=filters,
                          kernel_size=(1, kernel_size[1], kernel_size[2]),
                          padding=padding),
            # Temporal decomposition
            layers.Conv3D(filters=filters,
                          kernel_size=(kernel_size[0], 1, 1),
                          padding=padding)
        ])

    def call(self, x):
        return self.seq(x)


@keras.saving.register_keras_serializable()
class ResidualMain(keras.layers.Layer):
    """
    Residual block of the model with convolution, layer normalization, and the
    activation function, ReLU.
  """

    def __init__(self, filters, kernel_size, **kwargs):
        super().__init__(**kwargs)
        self.seq = keras.Sequential([
            Conv2Plus1D(filters=filters,
                        kernel_size=kernel_size,
                        padding='same'),
            layers.LayerNormalization(),
            layers.ReLU(),
            Conv2Plus1D(filters=filters,
                        kernel_size=kernel_size,
                        padding='same'),
            layers.LayerNormalization()
        ])

    def call(self, x):
        return self.seq(x)


@keras.saving.register_keras_serializable()
class Project(keras.layers.Layer):
    """
    Project certain dimensions of the tensor as the data is passed through different
    sized filters and downsampled.
  """

    def __init__(self, units, **kwargs):
        super().__init__(**kwargs)
        self.seq = keras.Sequential([
            layers.Dense(units),
            layers.LayerNormalization()
        ])

    def call(self, x):
        return self.seq(x)


@keras.saving.register_keras_serializable()
def add_residual_block(input, filters, kernel_size):
    """
    Add residual blocks to the model. If the last dimensions of the input data
    and filter size does not match, project it such that last dimension matches.
  """
    out = ResidualMain(filters,
                       kernel_size)(input)

    res = input
    # Using the Keras functional APIs, project the last dimension of the tensor to
    # match the new filter size
    if out.shape[-1] != input.shape[-1]:
        res = Project(out.shape[-1])(res)

    return layers.add([res, out])


@keras.saving.register_keras_serializable()
class ResizeVideo(keras.layers.Layer):
    def __init__(self, height, width, **kwargs):
        super().__init__(**kwargs)
        self.height = height
        self.width = width
        self.resizing_layer = layers.Resizing(self.height, self.width)

    def call(self, video):
        """
      Use the einops library to resize the tensor.

      Args:
        video: Tensor representation of the video, in the form of a set of frames.

      Return:
        A downsampled size of the video according to the new height and width it should be resized to.
    """
        # b stands for batch size, t stands for time, h stands for height,
        # w stands for width, and c stands for the number of channels.
        old_shape = einops.parse_shape(video, 'b t h w c')
        images = einops.rearrange(video, 'b t h w c -> (b t) h w c')
        images = self.resizing_layer(images)
        videos = einops.rearrange(
            images, '(b t) h w c -> b t h w c',
            t=old_shape['t'])
        return videos
