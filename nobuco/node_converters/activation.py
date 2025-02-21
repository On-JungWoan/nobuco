from typing import Optional, Union, List, Tuple, Sequence, Any

from torch import Tensor
from torch.types import _int, _bool, Number, _dtype, _size

import tensorflow as tf
from tensorflow import keras
import torch
import torch.nn.functional as F
from torch import nn

from tensorflow.python.framework.ops import disable_eager_execution

from nobuco.commons import ChannelOrder, ChannelOrderingStrategy
from nobuco.converters.channel_ordering import set_channel_order, get_channel_order
from nobuco.converters.node_converter import converter
from nobuco.converters.tensor import dim_pytorch2keras

def prelu(x, weight):
    x = tf.math.maximum(0, x) + weight * tf.math.minimum(0, x)
    return x

def hard_sigmoid_pytorch_compatible(x):
  x = tf.clip_by_value(x/6 + 1/2, clip_value_min=0, clip_value_max=1)
  return x


def hard_swish_pytorch_compatible(x):
  x = x * hard_sigmoid_pytorch_compatible(x)
  return x


def hard_tanh_pytorch_compatible(x, min_val, max_val):
  x = tf.clip_by_value(x, clip_value_min=min_val, clip_value_max=max_val)
  return x


@converter(torch.sigmoid, torch.Tensor.sigmoid, channel_ordering_strategy=ChannelOrderingStrategy.MINIMUM_TRANSPOSITIONS)
def converter_sigmoid(input: Tensor, *, out: Optional[Tensor]=None):
    def func(input, *, out=None):
        return keras.layers.Activation(keras.activations.sigmoid)(input)
    return func


@converter(torch.tanh, torch.Tensor.tanh, channel_ordering_strategy=ChannelOrderingStrategy.MINIMUM_TRANSPOSITIONS)
def converter_tanh(input: Tensor, *, out: Optional[Tensor]=None):
    def func(input: Tensor, *, out=None):
        return keras.layers.Activation(keras.activations.tanh)(input)
    return func


@converter(nn.ReLU, channel_ordering_strategy=ChannelOrderingStrategy.MINIMUM_TRANSPOSITIONS)
def converter_ReLU(self, input: Tensor):
    return keras.layers.ReLU()


@converter(F.relu, channel_ordering_strategy=ChannelOrderingStrategy.MINIMUM_TRANSPOSITIONS)
def converter_relu(input: Tensor, inplace: bool = False):
    def func(input, inplace=False):
        return tf.nn.relu(input)
    return func


@converter(torch.relu_, torch.Tensor.relu_, channel_ordering_strategy=ChannelOrderingStrategy.MINIMUM_TRANSPOSITIONS)
def converter_relu_(input: Tensor):
    def func(input):
        return tf.nn.relu(input)
    return func


# # please help me
# @converter(nn.PReLU, channel_ordering_strategy=ChannelOrderingStrategy.MINIMUM_TRANSPOSITIONS)
# def converter_PReLU(self, input: Tensor):
#     return keras.layers.PReLU()


@converter(F.prelu, channel_ordering_strategy=ChannelOrderingStrategy.MINIMUM_TRANSPOSITIONS)
def converter_prelu(input: Tensor, alpha: float = 0.0, inplace: bool = False):
    def func(input, alpha=0.0, inplace=False):
        # return keras.layers.PReLU(tf.initializers.constant(alpha))(input) # please help me
        return keras.layers.PReLU(tf.initializers.constant(0))(input)
    return func


@converter(torch.prelu, torch.Tensor.prelu, channel_ordering_strategy=ChannelOrderingStrategy.MINIMUM_TRANSPOSITIONS)
def converter_prelu(input: Tensor, alpha: float = 0.0, inplace: bool = False):
    def func(input, alpha=0.0, inplace=False):
        # return keras.layers.PReLU(tf.initializers.constant(alpha))(input) # please help me
        return keras.layers.PReLU(tf.initializers.constant(0))(input)
    return func


@converter(nn.LeakyReLU, channel_ordering_strategy=ChannelOrderingStrategy.MINIMUM_TRANSPOSITIONS)
def converter_LeakyRelu(self, input: Tensor):
    return keras.layers.LeakyReLU(alpha=self.negative_slope)


@converter(F.leaky_relu, channel_ordering_strategy=ChannelOrderingStrategy.MINIMUM_TRANSPOSITIONS)
def converter_leaky_relu(input: Tensor, negative_slope: float = 0.01, inplace: bool = False):
    def func(input, negative_slope=0.01, inplace=False):
        return keras.layers.LeakyReLU(alpha=negative_slope)(input)
    return func


@converter(F.hardsigmoid, channel_ordering_strategy=ChannelOrderingStrategy.MINIMUM_TRANSPOSITIONS)
def converter_hardsigmoid(input: Tensor, inplace: bool = False):
    def func(input, inplace=False):
        return hard_sigmoid_pytorch_compatible(input)
    return func


@converter(F.hardtanh, channel_ordering_strategy=ChannelOrderingStrategy.MINIMUM_TRANSPOSITIONS)
def converter_hardtanh(input: Tensor, min_val: float = -1.0, max_val: float = 1.0, inplace: bool = False):
    def func(input, min_val=-1.0, max_val=1.0, inplace=False):
        return hard_tanh_pytorch_compatible(input, min_val, max_val)
    return func


@converter(F.hardswish, channel_ordering_strategy=ChannelOrderingStrategy.MINIMUM_TRANSPOSITIONS)
def converter_hardswish(input: Tensor, inplace: bool = False):
    def func(input, inplace=False):
        return hard_swish_pytorch_compatible(input)
    return func


@converter(torch.softmax, torch.Tensor.softmax, channel_ordering_strategy=ChannelOrderingStrategy.MINIMUM_TRANSPOSITIONS)
def converter_softmax(input: Tensor, dim: Union[str, None], *, dtype: Optional[_dtype]=None):
    num_dims = input.dim()

    def func(input: Tensor, dim, *, dtype=None):
        if get_channel_order(input) == ChannelOrder.TENSORFLOW:
            dim = dim_pytorch2keras(dim, num_dims)
        return tf.nn.softmax(input, axis=dim)
    return func


@converter(torch.clip, channel_ordering_strategy=ChannelOrderingStrategy.MINIMUM_TRANSPOSITIONS)
def converter_clip(input: Tensor, min: Optional[Tensor]=None, max: Optional[Tensor]=None, *, out: Optional[Tensor]=None):
    def func(input, min=None, max=None, *, out=None):
        return tf.clip_by_value(input, min, max)
    return func
