from ai.transform import *


def load_model():
    return tf.keras.models.load_model('video_model.keras',
                                      custom_objects={'Conv2Plus1D': Conv2Plus1D,
                                                      'ResidualMain': ResidualMain,
                                                      'Project': Project,
                                                      'add_residual_block': add_residual_block,
                                                      'ResizeVideo': ResizeVideo})
