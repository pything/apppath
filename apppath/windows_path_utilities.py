#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = ""

__all__ = ["get_win_folder"]

from typing import Any

from warg.os_utilities.platform_selection import SYSTEM_, is_py3

if is_py3():
    unicode = str


def _get_win_folder_from_registry(csidl_name: Any) -> Any:
    """This is a fallback technique at best. I'm not sure if using the
    registry for this guarantees us the correct answer for all CSIDL_*
    names."""
    if is_py3():
        import winreg as _winreg
    else:
        import _winreg

    shell_folder_name = {
        "CSIDL_APPDATA": "AppData",
        "CSIDL_COMMON_APPDATA": "Common AppData",
        "CSIDL_LOCAL_APPDATA": "Local AppData",
    }[csidl_name]

    key = _winreg.OpenKey(
        _winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
    )
    ddir, ttype = _winreg.QueryValueEx(key, shell_folder_name)
    return ddir


def _get_win_folder_with_pywin32(csidl_name: Any) -> Any:
    from win32com.shell import shellcon, shell

    ddir = shell.SHGetFolderPath(0, getattr(shellcon, csidl_name), 0, 0)
    # Try to make this a unicode path because SHGetFolderPath does
    # not return unicode strings when there is unicode data in the
    # path.
    try:
        ddir = unicode(ddir)

        # Downgrade to short path name if have highbit chars. See
        # <http://bugs.activestate.com/show_bug.cgi?id=85099>.
        has_high_char = False
        for c in ddir:
            if ord(c) > 255:
                has_high_char = True
                break
        if has_high_char:
            try:
                import win32api

                ddir = win32api.GetShortPathName(ddir)
            except ImportError:
                pass
    except UnicodeError:
        pass
    return ddir


def _get_win_folder_with_ctypes(csidl_name: Any) -> Any:
    from ctypes import windll, create_unicode_buffer

    csidl_const = {
        "CSIDL_APPDATA": 26,
        "CSIDL_COMMON_APPDATA": 35,
        "CSIDL_LOCAL_APPDATA": 28,
    }[csidl_name]

    buf = create_unicode_buffer(1024)
    windll.shell32.SHGetFolderPathW(None, csidl_const, None, 0, buf)

    # Downgrade to short path name if have highbit chars. See
    # <http://bugs.activestate.com/show_bug.cgi?id=85099>.
    has_high_char = False
    for c in buf:
        if ord(c) > 255:
            has_high_char = True
            break
    if has_high_char:
        buf2 = create_unicode_buffer(1024)
        if windll.kernel32.GetShortPathNameW(buf.value, buf2, 1024):
            buf = buf2

    return buf.value


def _get_win_folder_with_jna(csidl_name: Any) -> Any:
    import array
    from com.sun import jna
    from com.sun.jna.platform import win32

    buf_size = win32.WinDef.MAX_PATH * 2
    buf = array.zeros("c", buf_size)
    shell = win32.Shell32.INSTANCE
    shell.SHGetFolderPath(
        None,
        getattr(win32.ShlObj, csidl_name),
        None,
        win32.ShlObj.SHGFP_TYPE_CURRENT,
        buf,
    )
    ddir = jna.Native.toString(buf.tostring()).rstrip("\0")

    # Downgrade to short path name if have highbit chars. See
    # <http://bugs.activestate.com/show_bug.cgi?id=85099>.
    has_high_char = False
    for c in ddir:
        if ord(c) > 255:
            has_high_char = True
            break
    if has_high_char:
        buf = array.zeros("c", buf_size)
        kernel = win32.Kernel32.INSTANCE
        if kernel.GetShortPathName(ddir, buf, buf_size):
            ddir = jna.Native.toString(buf.tostring()).rstrip("\0")

    return ddir


get_win_folder = None


if SYSTEM_ == "win32":  # IMPORT TESTS
    try:
        from win32com import shell

        get_win_folder = _get_win_folder_with_pywin32
    except ImportError:
        try:
            from ctypes import windll

            get_win_folder = _get_win_folder_with_ctypes
        except ImportError:
            try:
                from com.sun import jna

                get_win_folder = _get_win_folder_with_jna
            except ImportError:
                get_win_folder = _get_win_folder_from_registry
