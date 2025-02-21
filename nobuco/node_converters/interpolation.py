import numbers
from typing import Optional, Union, List, Tuple, Sequence, Any

from tensorflow.python.ops.image_ops_impl import ResizeMethod
from torch import Tensor

import tensorflow as tf
import torch
import torch.nn.functional as F
from nobuco.converters.node_converter import converter


@converter(F.interpolate)
def converter_interpolate(input: Tensor, size: Optional[int] = None, scale_factor: Optional[List[float]] = None, mode: str = 'nearest',
                align_corners: Optional[bool] = None, recompute_scale_factor: Optional[bool] = None, antialias: bool = False):
    if mode == 'bilinear':
        method = ResizeMethod.BILINEAR
    elif mode == 'nearest':
        method = ResizeMethod.NEAREST_NEIGHBOR
    else:
        raise Exception('Unsupported mode: ', mode)

    def func(input, size=None, scale_factor=None, mode='nearest', align_corners=None, recompute_scale_factor=None, antialias=False):
        if isinstance(scale_factor, numbers.Number):
            scale_factor = (scale_factor, scale_factor)

        if isinstance(size, numbers.Number):
            size = (size, size)

        if size is None:
            _, h, w, _ = input.shape
            size = (int(h * scale_factor[0]), int(w * scale_factor[1]))

        return tf.image.resize(input, size=size, method=method, antialias=antialias)
    return func
