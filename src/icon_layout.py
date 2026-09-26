"""
icon_layout.py — Save and restore desktop icon positions on Windows.

Uses Win32 API via ctypes to read/write SysListView32 item positions
from the Shell desktop window. Works on Windows 10/11 x64.
"""

import ctypes
import ctypes.wintypes
import json
import os
import logging
import struct
from datetime import datetime

# ── Win32 constants ──────────────────────────────────────────────────────────
LVM_FIRST           = 0x1000
LVM_GETITEMCOUNT    = LVM_FIRST + 4
LVM_GETITEMTEXTW    = LVM_FIRST + 115
LVM_GETITEMPOSITION = LVM_FIRST + 16
LVM_SETITEMPOSITION = LVM_FIRST + 15

PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_READ      = 0x0010
PROCESS_VM_WRITE     = 0x0020
MEM_COMMIT           = 0x1000
MEM_RELEASE          = 0x8000
PAGE_READWRITE       = 0x04

# ── ctypes structures ─────────────────────────────────────────────────────────
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class LVITEMW(ctypes.Structure):
    _fields_ = [
        ("mask",       ctypes.c_uint),
        ("iItem",      ctypes.c_int),
        ("iSubItem",   ctypes.c_int),
        ("state",      ctypes.c_uint),
        ("stateMask",  ctypes.c_uint),
        ("pszText",    ctypes.c_void_p),
        ("cchTextMax", ctypes.c_int),
        ("iImage",     ctypes.c_int),
        ("lParam",     ctypes.c_ssize_t),
        ("iIndent",    ctypes.c_int),
    ]


# ── Low-level helpers ─────────────────────────────────────────────────────────

def _get_desktop_listview_hwnd() -> int:
    """
    Walk the shell window tree to find the SysListView32 that holds desktop icons.
    Hierarchy: Progman > SHELLDLL_DefView > SysListView32
    On some Windows builds there's an extra WorkerW layer.
    """
    user32 = ctypes.windll.user32

    progman = user32.FindWindowW("Progman", None)
    shell_view = user32.FindWindowExW(progman, None, "SHELLDLL_DefView", None)

    if not shell_view:
        # Try WorkerW windows (Windows 10 with wallpaper engine or similar)
        worker_w = 0
        def _enum_cb(hwnd, _):
            nonlocal shell_view, worker_w
            sv = user32.FindWindowExW(hwnd, None, "SHELLDLL_DefView", None)
            if sv:
                shell_view = sv
                worker_w = hwnd
            return True

        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
        user32.EnumWindows(EnumWindowsProc(_enum_cb), 0)

    if not shell_view:
        raise RuntimeError("Could not locate SHELLDLL_DefView — desktop not in standard state.")

    lv = user32.FindWindowExW(shell_view, None, "SysListView32", None)
    if not lv:
        raise RuntimeError("Could not locate SysListView32 inside SHELLDLL_DefView.")
    return lv


def _get_owner_pid(hwnd: int) -> int:
    pid = ctypes.c_ulong(0)
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value


# ── Public API ────────────────────────────────────────────────────────────────

def save_icon_positions(output_path: str) -> dict:
    """
    Read all desktop icon names and (x, y) positions.
    Saves them as JSON to *output_path*.
    Returns the layout dict: { icon_name: [x, y], ... }
    """
    kernel32 = ctypes.windll.kernel32
    user32   = ctypes.windll.user32

    lv  = _get_desktop_listview_hwnd()
    pid = _get_owner_pid(lv)

    # Open the desktop process for cross-process memory operations
    proc = kernel32.OpenProcess(
        PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE,
        False, pid
    )
    if not proc:
        raise PermissionError(f"OpenProcess failed (pid={pid}). Try running as administrator.")

    try:
        item_count = user32.SendMessageW(lv, LVM_GETITEMCOUNT, 0, 0)

        # Allocate remote buffers for POINT and LVITEMW + text
        MAX_TEXT = 512
        remote_point = kernel32.VirtualAllocEx(proc, None, ctypes.sizeof(POINT),
                                               MEM_COMMIT, PAGE_READWRITE)
        remote_item  = kernel32.VirtualAllocEx(proc, None, ctypes.sizeof(LVITEMW),
                                               MEM_COMMIT, PAGE_READWRITE)
        remote_text  = kernel32.VirtualAllocEx(proc, None, MAX_TEXT * 2,
                                               MEM_COMMIT, PAGE_READWRITE)

        layout = {}

        for i in range(item_count):
            # ── Get position ──────────────────────────────────────
            user32.SendMessageW(lv, LVM_GETITEMPOSITION, i, remote_point)
            pt = POINT()
            bytes_read = ctypes.c_size_t(0)
            kernel32.ReadProcessMemory(proc, remote_point, ctypes.byref(pt),
                                       ctypes.sizeof(POINT), ctypes.byref(bytes_read))

            # ── Get text ──────────────────────────────────────────
            LVIF_TEXT = 0x0001
            item = LVITEMW()
            item.mask       = LVIF_TEXT
            item.iItem      = i
            item.iSubItem   = 0
            item.pszText    = remote_text
            item.cchTextMax = MAX_TEXT

            kernel32.WriteProcessMemory(proc, remote_item, ctypes.byref(item),
                                        ctypes.sizeof(LVITEMW), None)
            user32.SendMessageW(lv, LVM_GETITEMTEXTW, i, remote_item)

            raw = (ctypes.c_wchar * MAX_TEXT)()
            kernel32.ReadProcessMemory(proc, remote_text, raw, MAX_TEXT * 2, None)
            name = raw.value.strip()

            if name:
                layout[name] = [pt.x, pt.y]

        # Free remote buffers
        for buf in (remote_point, remote_item, remote_text):
            kernel32.VirtualFreeEx(proc, buf, 0, MEM_RELEASE)

    finally:
        kernel32.CloseHandle(proc)

    # Persist to disk
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "saved_at": datetime.now().isoformat(),
            "layout": layout
        }, f, ensure_ascii=False, indent=2)

    logging.info(f"[IconLayout] Saved {len(layout)} icon positions → {output_path}")
    return layout


def restore_icon_positions(input_path: str) -> int:
    """
    Read a previously saved layout JSON and apply positions back to desktop icons.
    Returns the number of icons successfully repositioned.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Layout file not found: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    layout: dict = data.get("layout", {})
    if not layout:
        logging.warning("[IconLayout] Layout file is empty — nothing to restore.")
        return 0

    kernel32 = ctypes.windll.kernel32
    user32   = ctypes.windll.user32

    lv  = _get_desktop_listview_hwnd()
    pid = _get_owner_pid(lv)

    proc = kernel32.OpenProcess(
        PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE,
        False, pid
    )
    if not proc:
        raise PermissionError("OpenProcess failed. Try running as administrator.")

    try:
        item_count = user32.SendMessageW(lv, LVM_GETITEMCOUNT, 0, 0)
        MAX_TEXT = 512
        remote_item = kernel32.VirtualAllocEx(proc, None, ctypes.sizeof(LVITEMW),
                                              MEM_COMMIT, PAGE_READWRITE)
        remote_text = kernel32.VirtualAllocEx(proc, None, MAX_TEXT * 2,
                                              MEM_COMMIT, PAGE_READWRITE)

        restored = 0
        for i in range(item_count):
            LVIF_TEXT = 0x0001
            item = LVITEMW()
            item.mask       = LVIF_TEXT
            item.iItem      = i
            item.iSubItem   = 0
            item.pszText    = remote_text
            item.cchTextMax = MAX_TEXT

            kernel32.WriteProcessMemory(proc, remote_item, ctypes.byref(item),
                                        ctypes.sizeof(LVITEMW), None)
            user32.SendMessageW(lv, LVM_GETITEMTEXTW, i, remote_item)

            raw = (ctypes.c_wchar * MAX_TEXT)()
            kernel32.ReadProcessMemory(proc, remote_text, raw, MAX_TEXT * 2, None)
            name = raw.value.strip()

            if name in layout:
                x, y = layout[name]
                # Pack x,y into LPARAM: high word = y, low word = x
                lparam = (y << 16) | (x & 0xFFFF)
                user32.SendMessageW(lv, LVM_SETITEMPOSITION, i, lparam)
                restored += 1

        for buf in (remote_item, remote_text):
            kernel32.VirtualFreeEx(proc, buf, 0, MEM_RELEASE)

    finally:
        kernel32.CloseHandle(proc)

    # Refresh desktop
    user32.UpdateWindow(lv)
    logging.info(f"[IconLayout] Restored {restored}/{len(layout)} icon positions.")
    return restored


def get_default_layout_path() -> str:
    """Returns the default path for the layout snapshot file."""
    return os.path.join(os.path.expanduser("~"), ".sweeply_icon_layout.json")
