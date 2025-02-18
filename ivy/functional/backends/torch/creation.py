# global
import torch
import numpy as np
from torch import Tensor
from typing import Union, Tuple, Optional, Dict

# local
from ivy import dtype_from_str, default_dtype, dev_from_str, default_device
from ivy.functional.backends.torch.device import _callable_dev


def asarray(object_in, dtype: Optional[str] = None, dev: Optional[str] = None, copy: Optional[bool] = None):
    dev = default_device(dev)
    if isinstance(object_in, torch.Tensor) and dtype is None:
        dtype = object_in.dtype
    elif isinstance(object_in, (list, tuple, dict)) and len(object_in) != 0 and dtype is None:
        # Temporary fix on type
        # Because default_type() didn't return correct type for normal python array
        if copy is True:
            return torch.as_tensor(object_in).clone().detach().to(dev_from_str(dev))
        else:
            return torch.as_tensor(object_in).to(dev_from_str(dev))
    else:
        dtype = dtype_from_str(default_dtype(dtype, object_in))
    if copy is True:
        return torch.as_tensor(object_in, dtype=dtype).clone().detach().to(dev_from_str(dev))
    else:
        return torch.as_tensor(object_in, dtype=dtype).to(dev_from_str(dev))


def zeros(shape: Union[int, Tuple[int]],
          dtype: Optional[torch.dtype] = None,
          device: Optional[torch.device] = None) \
        -> Tensor:
    return torch.zeros(shape, dtype=dtype_from_str(default_dtype(dtype)), device=dev_from_str(default_device(device)))


def ones(shape: Union[int, Tuple[int]],
         dtype: Optional[torch.dtype] = None,
         device: Optional[Union[torch.device, str]] = None) \
        -> torch.Tensor:
    dtype_val: torch.dtype = dtype_from_str(dtype)
    dev = default_device(device)
    return torch.ones(shape, dtype=dtype_val, device=dev_from_str(dev))


def full_like(x: torch.Tensor, /,
              fill_value: Union[int, float],
              dtype: Optional[Union[torch.dtype, str]] = None,
              device: Optional[Union[torch.device, str]] = None) \
        -> torch.Tensor:
    if device is None:
        device = _callable_dev(x)
    if dtype is not None and dtype is str:
        type_dict: Dict[str, torch.dtype] = {'int8': torch.int8,
                                             'int16': torch.int16,
                                             'int32': torch.int32,
                                             'int64': torch.int64,
                                             'uint8': torch.uint8,
                                             'bfloat16': torch.bfloat16,
                                             'float16': torch.float16,
                                             'float32': torch.float32,
                                             'float64': torch.float64,
                                             'bool': torch.bool}
        return torch.full_like(x, fill_value, dtype=type_dict[default_dtype(dtype, fill_value)],
                               device=default_device(device))
    return torch.full_like(x, fill_value, dtype=dtype, device=default_device(device))


def ones_like(x : torch.Tensor,
              dtype: Optional[Union[torch.dtype, str]] = None,
              dev: Optional[Union[torch.device, str]] = None) \
        -> torch.Tensor:
    if dev is None:
        dev = _callable_dev(x)
    if dtype is not None and dtype is str:
        type_dict: Dict[str, torch.dtype] = {'int8': torch.int8,
            'int16': torch.int16,
            'int32': torch.int32,
            'int64': torch.int64,
            'uint8': torch.uint8,
            'bfloat16': torch.bfloat16,
            'float16': torch.float16,
            'float32': torch.float32,
            'float64': torch.float64,
            'bool': torch.bool}
        return torch.ones_like(x, dtype=type_dict[dtype], device=dev_from_str(dev))
    else:
        return torch.ones_like(x, dtype= dtype, device=dev_from_str(dev))

    return torch.ones_like(x, device=dev_from_str(dev))


def tril(x: torch.Tensor,
         k: int = 0) \
         -> torch.Tensor:
    return torch.tril(x, diagonal=k)


def triu(x: torch.Tensor,
         k: int = 0) \
         -> torch.Tensor:
    return torch.triu(x, diagonal=k)
    

def empty(shape: Union[int, Tuple[int]],
          dtype: Optional[torch.dtype] = None,
          device: Optional[torch.device] = None) \
        -> Tensor:
    return torch.empty(shape, dtype=dtype_from_str(default_dtype(dtype)), device=dev_from_str(default_device(device)))


def empty_like(x: torch.Tensor,
              dtype: Optional[Union[torch.dtype, str]] = None,
              dev: Optional[Union[torch.device, str]] = None) \
        -> torch.Tensor:
    if dev is None:
        dev = _callable_dev(x)
    if dtype is not None and dtype is str:
        type_dict: Dict[str, torch.dtype] = {'int8': torch.int8,
            'int16': torch.int16,
            'int32': torch.int32,
            'int64': torch.int64,
            'uint8': torch.uint8,
            'bfloat16': torch.bfloat16,
            'float16': torch.float16,
            'float32': torch.float32,
            'float64': torch.float64,
            'bool': torch.bool}
        return torch.empty_like(x, dtype=type_dict[dtype], device=dev_from_str(dev))
    else:
        return torch.empty_like(x, dtype= dtype, device=dev_from_str(dev))

    return torch.empty_like(x, device=dev_from_str(dev))

  
def _differentiable_linspace(start, stop, num, device):
    if num == 1:
        return torch.unsqueeze(start, 0)
    n_m_1 = num - 1
    increment = (stop - start) / n_m_1
    increment_tiled = increment.repeat(n_m_1)
    increments = increment_tiled * torch.linspace(1, n_m_1, n_m_1, device=device)
    res = torch.cat((torch.unsqueeze(torch.tensor(start), 0), start + increments), 0)
    return res


# noinspection PyUnboundLocalVariable,PyShadowingNames
def linspace(start, stop, num, axis=None, dev=None):
    num = num.detach().numpy().item() if isinstance(num, torch.Tensor) else num
    start_is_array = isinstance(start, torch.Tensor)
    stop_is_array = isinstance(stop, torch.Tensor)
    linspace_method = torch.linspace
    dev = default_device(dev)
    sos_shape = []
    if start_is_array:
        start_shape = list(start.shape)
        sos_shape = start_shape
        if num == 1:
            return start.unsqueeze(axis).to(dev_from_str(dev))
        start = start.reshape((-1,))
        linspace_method = _differentiable_linspace if start.requires_grad else torch.linspace
    if stop_is_array:
        stop_shape = list(stop.shape)
        sos_shape = stop_shape
        if num == 1:
            return torch.ones(stop_shape[:axis] + [1] + stop_shape[axis:], device=dev_from_str(dev)) * start
        stop = stop.reshape((-1,))
        linspace_method = _differentiable_linspace if stop.requires_grad else torch.linspace
    if start_is_array and stop_is_array:
        if num < start.shape[0]:
            start = start.unsqueeze(-1)
            stop = stop.unsqueeze(-1)
            diff = stop - start
            inc = diff / (num-1)
            res = [start]
            res += [start + inc*i for i in range(1, num-1)]
            res.append(stop)
        else:
            res = [linspace_method(strt, stp, num, device=dev_from_str(dev)) for strt, stp in zip(start, stop)]
        torch.cat(res, -1).reshape(start_shape + [num])
    elif start_is_array and not stop_is_array:
        if num < start.shape[0]:
            start = start.unsqueeze(-1)
            diff = stop - start
            inc = diff / (num - 1)
            res = [start]
            res += [start + inc * i for i in range(1, num - 1)]
            res.append(torch.ones_like(start, device=dev_from_str(dev)) * stop)
        else:
            res = [linspace_method(strt, stop, num, device=dev_from_str(dev)) for strt in start]
    elif not start_is_array and stop_is_array:
        if num < stop.shape[0]:
            stop = stop.unsqueeze(-1)
            diff = stop - start
            inc = diff / (num - 1)
            res = [torch.ones_like(stop, device=dev_from_str(dev)) * start]
            res += [start + inc * i for i in range(1, num - 1)]
            res.append(stop)
        else:
            res = [linspace_method(start, stp, num, device=dev_from_str(dev)) for stp in stop]
    else:
        return linspace_method(start, stop, num, device=dev_from_str(dev))
    res = torch.cat(res, -1).reshape(sos_shape + [num])
    if axis is not None:
        res = torch.transpose(res, axis, -1)
    return res.to(dev_from_str(dev))

# Extra #
# ------#

# noinspection PyShadowingNames
def array(object_in, dtype: Optional[str] = None, dev: Optional[str] = None):
    dev = default_device(dev)
    dtype = dtype_from_str(default_dtype(dtype, object_in))
    if isinstance(object_in, np.ndarray):
        return torch.Tensor(object_in).to(dev_from_str(dev))
    if dtype is not None:
        return torch.tensor(object_in, dtype=dtype, device=dev_from_str(dev))
    elif isinstance(object_in, torch.Tensor):
        return object_in.to(dev_from_str(dev))
    else:
        return torch.tensor(object_in, device=dev_from_str(dev))


def logspace(start, stop, num, base=10., axis=None, dev=None):
    power_seq = linspace(start, stop, num, axis, default_device(dev))
    return base ** power_seq
