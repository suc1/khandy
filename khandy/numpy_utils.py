from typing import List

import numpy as np
from numpy.core.multiarray import normalize_axis_index


def sigmoid(x):
    return 1. / (1 + np.exp(-x))
    
    
def softmax(x, axis=-1, copy=True):
    """
    Args:
        copy: Copy x or not.
        
    Referneces:
        `from sklearn.utils.extmath import softmax`
    """
    if copy:
        x = np.copy(x)
    max_val = np.max(x, axis=axis, keepdims=True)
    x -= max_val
    np.exp(x, x)
    sum_exp = np.sum(x, axis=axis, keepdims=True)
    x /= sum_exp
    return x
    
    
def log_sum_exp(x, axis=-1, keepdims=False):
    """
    References:
        numpy.logaddexp
        numpy.logaddexp2
        scipy.misc.logsumexp
    """
    max_val = np.max(x, axis=axis, keepdims=True)
    x -= max_val
    np.exp(x, x)
    sum_exp = np.sum(x, axis=axis, keepdims=keepdims)
    lse = np.log(sum_exp, sum_exp)
    if not keepdims:
        max_val = np.squeeze(max_val, axis=axis)
    return max_val + lse
    
    
def l2_normalize(x, axis=None, epsilon=1e-12, copy=True):
    """L2 normalize an array along an axis.
    
    Args:
        x : array_like of floats
            Input data.
        axis : None or int or tuple of ints, optional
            Axis or axes along which to operate.
        epsilon: float, optional
            A small value such as to avoid division by zero.
        copy : bool, optional
            Copy x or not.
    """
    if copy:
        x = np.copy(x)
    x /= np.maximum(np.linalg.norm(x, axis=axis, keepdims=True), epsilon)
    return x
    
    
def minmax_normalize(x, axis=None, epsilon=1e-12, copy=True):
    """minmax normalize an array along a given axis.
    
    Args:
        x : array_like of floats
            Input data.
        axis : None or int or tuple of ints, optional
            Axis or axes along which to operate.
        epsilon: float, optional
            A small value such as to avoid division by zero.
        copy : bool, optional
            Copy x or not.
    """
    if copy:
        x = np.copy(x)
    
    minval = np.min(x, axis=axis, keepdims=True)
    maxval = np.max(x, axis=axis, keepdims=True)
    maxval -= minval
    maxval = np.maximum(maxval, epsilon)
    
    x -= minval
    x /= maxval
    return x


def zscore_normalize(x, mean=None, std=None, axis=None, epsilon=1e-12, copy=True):
    """z-score normalize an array along a given axis.
    
    Args:
        x : array_like of floats
            Input data.
        mean:  array_like of floats, optional
            mean for z-score
        std: array_like of floats, optional
            std for z-score
        axis : None or int or tuple of ints, optional
            Axis or axes along which to operate.
        epsilon: float, optional
            A small value such as to avoid division by zero.
        copy : bool, optional
            Copy x or not.
    """
    if copy:
        x = np.copy(x)
    if mean is None:
        mean = np.mean(x, axis=axis, keepdims=True)
    if std is None:
        std = np.std(x, axis=axis, keepdims=True)
    mean = np.asarray(mean, dtype=x.dtype)
    std = np.asarray(std, dtype=x.dtype)
    std = np.maximum(std, epsilon)
    
    x -= mean
    x /= std
    return x


def get_order_of_magnitude(number):
    number = np.where(number == 0, 1, number)
    oom = np.floor(np.log10(np.abs(number)))
    return oom.astype(np.int32)
    
    
def top_k(x, k, axis=-1, largest=True, sorted=True):
    """Finds values and indices of the k largest/smallest 
    elements along a given axis.

    Args:
        x: numpy ndarray
            1-D or higher with given axis at least k.
        k: int
            Number of top elements to look for along the given axis.
        axis: int
            The axis to sort along.
        largest: bool
            Controls whether to return largest or smallest elements
        sorted: bool
            If true the resulting k elements will be sorted by the values.

    Returns:
        topk_values: 
            The k largest/smallest elements along the given axis.
        topk_indices: 
            The indices of the k largest/smallest elements along the given axis.
    """
    if axis is None:
        axis_size = x.size
    else:
        axis_size = x.shape[axis]
    assert 1 <= k <= axis_size

    x = np.asanyarray(x)
    if largest:
        index_array = np.argpartition(x, axis_size-k, axis=axis)
        topk_indices = np.take(index_array, -np.arange(k)-1, axis=axis)
    else:
        index_array = np.argpartition(x, k-1, axis=axis)
        topk_indices = np.take(index_array, np.arange(k), axis=axis)
    topk_values = np.take_along_axis(x, topk_indices, axis=axis)
    if sorted:
        sorted_indices_in_topk = np.argsort(topk_values, axis=axis)
        if largest:
            sorted_indices_in_topk = np.flip(sorted_indices_in_topk, axis=axis)
        sorted_topk_values = np.take_along_axis(
            topk_values, sorted_indices_in_topk, axis=axis)
        sorted_topk_indices = np.take_along_axis(
            topk_indices, sorted_indices_in_topk, axis=axis)
        return sorted_topk_values, sorted_topk_indices
    return topk_values, topk_indices
    
    
def sum_by_indices_list(x: np.ndarray, indices_list: List[List[int]] = None, axis=-1):
    """Sums of array elements according to a given list of index lists over a given axis.

    Args:
        x (np.ndarray): Input array to perform the sum operation.
        indices_list (List[List[int]]): List of index lists corresponding to the axis along which to sum.
        axis (int): Axis along which to perform the sum operation. Defaults to the last axis.

    Returns:
        np.ndarray: Output array after performing the sum operation along the specified axis.
            Has the same shape as the input array with the exception of the dimension along the axis 
            specified by indices_list, which has a length equal to the number of index lists in indices_list.
    """
    axis = normalize_axis_index(axis, x.ndim)
    new_shape = list(x.shape)
    new_shape[axis] = len(indices_list)
    dst = np.empty(new_shape, dtype=x.dtype)
    for new_index, old_indices in enumerate(indices_list):
        dest_dims = (slice(None),) * axis + (new_index,)
        dst[dest_dims] = np.sum(x.take(old_indices, axis), axis=axis, keepdims=False)
    return dst
