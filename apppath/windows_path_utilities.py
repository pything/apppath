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


'''
import ctypes
from ctypes.wintypes import HWND, UINT, WPARAM, LPARAM, LPVOID
LRESULT = LPARAM  # synonymous
import os
import sys
try:
    import winreg
    unicode = str
except ImportError:
    import _winreg as winreg  # Python 2.x

class Environment(object):
    path = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
    hklm = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    key = winreg.OpenKey(hklm, path, 0, winreg.KEY_READ | winreg.KEY_WRITE)
    SendMessage = ctypes.windll.user32.SendMessageW
    SendMessage.argtypes = HWND, UINT, WPARAM, LPVOID
    SendMessage.restype = LRESULT
    HWND_BROADCAST = 0xFFFF
    WM_SETTINGCHANGE = 0x1A
    NO_DEFAULT_PROVIDED = object()

    def get(self, name, default=NO_DEFAULT_PROVIDED):
        try:
            value = winreg.QueryValueEx(self.key, name)[0]
        except WindowsError:
            if default is self.NO_DEFAULT_PROVIDED:
                raise ValueError("No such registry key", name)
            value = default
        return value

    def set(self, name, value):
        if value:
            winreg.SetValueEx(self.key, name, 0, winreg.REG_EXPAND_SZ, value)
        else:
            winreg.DeleteValue(self.key, name)
        self.notify()

    def notify(self):
        self.SendMessage(self.HWND_BROADCAST, self.WM_SETTINGCHANGE, 0, u'Environment')

Environment = Environment()  # singletion - create instance

PATH_VAR = 'PATH'

def append_path_envvar(addpath):
    def canonical(path):
        path = unicode(path.upper().rstrip(os.sep))
        return winreg.ExpandEnvironmentStrings(path)  # Requires Python 2.6+
    canpath = canonical(addpath)
    curpath = Environment.get(PATH_VAR, '')
    if not any(canpath == subpath
                for subpath in canonical(curpath).split(os.pathsep)):
        Environment.set(PATH_VAR, os.pathsep.join((curpath, addpath)))

def remove_envvar_path(folder):
    """ Remove *all* paths in PATH_VAR that contain the folder path. """
    curpath = Environment.get(PATH_VAR, '')
    folder = folder.upper()
    keepers = [subpath for subpath in curpath.split(os.pathsep)
                if folder not in subpath.upper()]
    Environment.set(PATH_VAR, os.pathsep.join(keepers))
'''

"""

import _winreg as reg
import win32gui
import win32con


# read the value
key = reg.OpenKey(reg.HKEY_CURRENT_USER, 'Environment', 0, reg.KEY_ALL_ACCESS)
# use this if you need to modify the system variable and if you have admin privileges
#key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 0, reg.KEY_ALL_ACCESS) 
try
    value, _ = reg.QueryValueEx(key, 'PATH')
except WindowsError:
    # in case the PATH variable is undefined
    value = ''

# modify it
value = ';'.join([s for s in value.split(';') if not r'\myprogram' in s])

# write it back
reg.SetValueEx(key, 'PATH', 0, reg.REG_EXPAND_SZ, value)
reg.CloseKey(key)

# notify the system about the changes
win32gui.SendMessage(win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, 'Environment')
"""


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
