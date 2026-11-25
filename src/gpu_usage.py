"""Leitura da ocupação da GPU pelos contadores de desempenho do Windows."""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
import ctypes
from ctypes import wintypes
import math
import os
import re


_ENGINE_INSTANCE = re.compile(r"^pid_\d+_(luid_0x[0-9a-f]+_0x[0-9a-f]+_phys_\d+_eng_\d+)_engtype_", re.I)
_MORE_DATA = 0x800007D2
_FORMAT_DOUBLE = 0x00000200


def busiest_engine_percent(samples: Iterable[tuple[str, float]]) -> int | None:
    """Soma os processos de cada motor e usa o maior valor entre os motores."""
    totals: dict[str, float] = defaultdict(float)
    for name, utilization in samples:
        engine = _ENGINE_INSTANCE.match(name)
        if engine and math.isfinite(utilization) and utilization >= 0:
            totals[engine[1].lower()] += utilization
    return round(min(100, max(totals.values()))) if totals else None


class _FormattedValue(ctypes.Structure):
    _fields_ = [("status", wintypes.DWORD), ("value", ctypes.c_double)]


class _FormattedItem(ctypes.Structure):
    _fields_ = [("name", wintypes.LPWSTR), ("counter", _FormattedValue)]


class GpuMonitor:
    def __init__(self):
        self._pdh = None
        self._query = wintypes.HANDLE()
        self._counter = wintypes.HANDLE()

    def _open(self) -> bool:
        try:
            pdh = ctypes.WinDLL("pdh.dll", winmode=0x800)  # LOAD_LIBRARY_SEARCH_SYSTEM32
        except OSError:
            return False
        handle = wintypes.HANDLE
        handle_pointer = ctypes.POINTER(handle)
        dword_pointer = ctypes.POINTER(wintypes.DWORD)
        for name, args in (
            ("PdhOpenQueryW", (wintypes.LPCWSTR, ctypes.c_size_t, handle_pointer)),
            ("PdhAddEnglishCounterW", (handle, wintypes.LPCWSTR, ctypes.c_size_t, handle_pointer)),
            ("PdhCollectQueryData", (handle,)),
            ("PdhGetFormattedCounterArrayW", (handle, wintypes.DWORD, dword_pointer, dword_pointer, ctypes.c_void_p)),
            ("PdhCloseQuery", (handle,)),
        ):
            function = getattr(pdh, name)
            function.argtypes = args
            function.restype = ctypes.c_uint32
        if pdh.PdhOpenQueryW(None, 0, ctypes.byref(self._query)):
            return False
        self._pdh = pdh
        if pdh.PdhAddEnglishCounterW(self._query, r"\GPU Engine(*)\Utilization Percentage", 0,
                                     ctypes.byref(self._counter)):
            self.close()
            return False
        return True

    def sample(self) -> int | None:
        if os.name != "nt" or (self._pdh is None and not self._open()):
            return None
        if self._pdh.PdhCollectQueryData(self._query):
            return None
        count = wintypes.DWORD()
        get_array = self._pdh.PdhGetFormattedCounterArrayW
        for _ in range(2):
            size = wintypes.DWORD()
            status = get_array(self._counter, _FORMAT_DOUBLE, ctypes.byref(size), ctypes.byref(count), None)
            if status != _MORE_DATA or not size.value:
                return None
            data = ctypes.create_string_buffer(size.value)
            status = get_array(self._counter, _FORMAT_DOUBLE, ctypes.byref(size), ctypes.byref(count), data)
            if status == 0:
                items = ctypes.cast(data, ctypes.POINTER(_FormattedItem))
                return busiest_engine_percent(
                    (items[index].name, items[index].counter.value)
                    for index in range(count.value)
                    if items[index].name and items[index].counter.status in (0, 1)
                )
            if status != _MORE_DATA:
                break
        return None

    def close(self):
        if self._pdh is not None:
            self._pdh.PdhCloseQuery(self._query)
            self._pdh = None
            self._query = wintypes.HANDLE()
            self._counter = wintypes.HANDLE()
