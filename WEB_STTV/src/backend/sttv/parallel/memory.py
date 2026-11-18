"""Sample simultaneous Windows process-tree working sets without dependencies."""

import ctypes
from ctypes import wintypes
import os
from threading import Event, Thread


class ProcessEntry(ctypes.Structure):
    _fields_ = [('size', wintypes.DWORD), ('usage', wintypes.DWORD), ('pid', wintypes.DWORD),
        ('heap', ctypes.c_size_t), ('module', wintypes.DWORD), ('threads', wintypes.DWORD),
        ('parent', wintypes.DWORD), ('priority', wintypes.LONG), ('flags', wintypes.DWORD),
        ('name', wintypes.WCHAR * 260)]


class MemoryCounters(ctypes.Structure):
    _fields_ = [('size', wintypes.DWORD), ('faults', wintypes.DWORD),
        *[(name, ctypes.c_size_t) for name in ('peak', 'working', 'peak_paged', 'paged',
          'peak_nonpaged', 'nonpaged', 'pagefile', 'peak_pagefile')]]


class Monitor:
    def __init__(self, root):
        self.root, self.stop = root, Event()
        self.data = {'method': 'windows_working_set_sample', 'interval_seconds': 1.0,
                     'samples': 0, 'coordinator_peak_bytes': 0, 'tree_peak_bytes': 0,
                     'temporary_peak_bytes': 0, 'errors': 0}
        self.thread = None
        if os.name != 'nt':
            self.data['method'] = 'unavailable'
            return
        self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        self.psapi = ctypes.WinDLL('psapi', use_last_error=True)
        self.kernel.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
        self.kernel.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
        for name in ('Process32FirstW', 'Process32NextW'):
            getattr(self.kernel, name).argtypes = [wintypes.HANDLE, ctypes.POINTER(ProcessEntry)]
        self.kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        self.kernel.OpenProcess.restype = wintypes.HANDLE
        self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        self.psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(MemoryCounters), wintypes.DWORD]
        self.thread = Thread(target=self.run, daemon=True)
        self.thread.start()

    def processes(self):
        handle = self.kernel.CreateToolhelp32Snapshot(2, 0)
        if handle == ctypes.c_void_p(-1).value:
            raise OSError('Cannot enumerate processes')
        parents, entry = {}, ProcessEntry()
        entry.size = ctypes.sizeof(entry)
        try:
            available = self.kernel.Process32FirstW(handle, ctypes.byref(entry))
            while available:
                parents[entry.pid] = entry.parent
                available = self.kernel.Process32NextW(handle, ctypes.byref(entry))
        finally:
            self.kernel.CloseHandle(handle)
        selected = {os.getpid()}
        while additions := {pid for pid, parent in parents.items() if parent in selected} - selected:
            selected.update(additions)
        return selected

    def sample(self):
        total, main = 0, 0
        for pid in self.processes():
            handle = self.kernel.OpenProcess(0x410, False, pid)
            if not handle:
                continue
            try:
                memory = MemoryCounters()
                memory.size = ctypes.sizeof(memory)
                if self.psapi.GetProcessMemoryInfo(handle, ctypes.byref(memory), memory.size):
                    total += memory.working
                    if pid == os.getpid():
                        main = memory.working
            finally:
                self.kernel.CloseHandle(handle)
        temporary = sum(path.stat().st_size for path in self.root.rglob('*') if path.is_file())
        self.data['samples'] += 1
        for key, value in (('tree_peak_bytes', total), ('coordinator_peak_bytes', main),
                           ('temporary_peak_bytes', temporary)):
            self.data[key] = max(self.data[key], value)

    def run(self):
        while not self.stop.is_set():
            try:
                self.sample()
            except OSError:
                self.data['errors'] += 1
            self.stop.wait(self.data['interval_seconds'])

    def close(self):
        self.stop.set()
        if self.thread is not None:
            self.thread.join()
