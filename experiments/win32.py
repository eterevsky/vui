import ctypes
from ctypes import Structure, WINFUNCTYPE, byref, c_int, c_char_p, c_void_p, c_wchar_p
from ctypes.wintypes import HANDLE, HBRUSH, HICON, HINSTANCE, HWND, LPARAM, MSG, UINT, WPARAM

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

HCURSOR = HANDLE
LRESULT = LPARAM
WNDPROC = WINFUNCTYPE(LRESULT, HWND, UINT, WPARAM, LPARAM)

CW_USEDEFAULT = -2147483648

SW_HIDE = 0
SW_SHOWNORMAL = 1
SW_NORMAL = 1
SW_SHOWMINIMIZED = 2
SW_SHOWMAXIMIZED = 3
SW_MAXIMIZE = 3
SW_SHOWNOACTIVATE = 4
SW_SHOW = 5
SW_MINIMIZE = 6
SW_SHOWMINNOACTIVE = 7
SW_SHOWNA = 8
SW_RESTORE = 9
SW_SHOWDEFAULT = 10
SW_FORCEMINIMIZE = 11
SW_MAX = 11

WS_OVERLAPPED = 0
WS_POPUP = -2147483648
WS_CHILD = 1073741824
WS_MINIMIZE = 536870912
WS_VISIBLE = 268435456
WS_DISABLED = 134217728
WS_CLIPSIBLINGS = 67108864
WS_CLIPCHILDREN = 33554432
WS_MAXIMIZE = 16777216
WS_CAPTION = 12582912
WS_BORDER = 8388608
WS_DLGFRAME = 4194304
WS_VSCROLL = 2097152
WS_HSCROLL = 1048576
WS_SYSMENU = 524288
WS_THICKFRAME = 262144
WS_GROUP = 131072
WS_TABSTOP = 65536
WS_MINIMIZEBOX = 131072
WS_MAXIMIZEBOX = 65536
WS_TILED = WS_OVERLAPPED
WS_ICONIC = WS_MINIMIZE
WS_SIZEBOX = WS_THICKFRAME

WM_DESTROY = 2
WM_PAINT = 15
WM_CLOSE = 16

DEFAULT_CHARSET = 1
OUT_DEFAULT_PRECIS = 0
CLIP_DEFAULT_PRECIS = 0

DEFAULT_QUALITY = 0
DRAFT_QUALITY = 1
PROOF_QUALITY = 2
NONANTIALIASED_QUALITY = 3
ANTIALIASED_QUALITY = 4
CLEARTYPE_QUALITY = 5
CLEARTYPE_NATURAL_QUALITY = 6

FF_DONTCARE = (0<<4)
FF_ROMAN = (1<<4)
FF_SWISS = (2<<4)
FF_MODERN = (3<<4)
FF_SCRIPT = (4<<4)
FF_DECORATIVE = (5<<4)

DEFAULT_PITCH = 0
FIXED_PITCH = 1
VARIABLE_PITCH = 2

FW_DONTCARE = 0

PROCESS_DPI_UNAWARE = 0
PROCESS_SYSTEM_DPI_AWARE = 1
PROCESS_PER_MONITOR_DPI_AWARE = 2

DPI_AWARENESS_CONTEXT_UNAWARE = c_void_p(-1)
DPI_AWARENESS_CONTEXT_SYSTEM_AWARE = c_void_p(-2)
DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE = c_void_p(-3)
DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = c_void_p(-4)
DPI_AWARENESS_CONTEXT_UNAWARE_GDISCALED = c_void_p(-5)

class WNDCLASSA(Structure):
    _fields_ = [
        ('style', UINT),
        ('lpfnWndProc', WNDPROC),
        ('cbClsExtra', c_int),
        ('cbWndExtra', c_int),
        ('hInstance', HINSTANCE),
        ('hIcon', HICON),
        ('hCursor', HCURSOR),
        ('hbrBackground', HBRUSH),
        ('lpszMenuName', c_char_p),
        ('lpszClassName', c_char_p)
    ]


class WNDCLASSW(Structure):
    _fields_ = [
        ('style', UINT),
        ('lpfnWndProc', WNDPROC),
        ('cbClsExtra', c_int),
        ('cbWndExtra', c_int),
        ('hInstance', HINSTANCE),
        ('hIcon', HICON),
        ('hCursor', HCURSOR),
        ('hbrBackground', HBRUSH),
        ('lpszMenuName', c_wchar_p),
        ('lpszClassName', c_wchar_p)
    ]


# class StrictHandle(Structure):
#     _fields_ = [()]


class Renderer(object):
    def __init__(self):
        self.hwnd = None
        self.dc = None
        self.font = gdi32.CreateFontW(
            30, 0,
            0, 0,
            FW_DONTCARE,
            0, 0, 0,
            DEFAULT_CHARSET,
            OUT_DEFAULT_PRECIS,
            CLIP_DEFAULT_PRECIS,
            CLEARTYPE_QUALITY,
            FF_DONTCARE | DEFAULT_PITCH,
            'Times New Roman')

    def set_hwnd(self, hwnd):
        self.hwnd = hwnd
        self.dc = user32.GetDC(hwnd)
        gdi32.SelectObject(self.dc, self.font)

    def window_proc(self, hwnd, uMsg, wParam, lParam):
        if uMsg == WM_DESTROY:
            # print('window_proc', hwnd, 'WM_DESTROY', wParam, lParam)
            user32.PostQuitMessage(0)
        elif uMsg == WM_PAINT:
            s = 'Hello world. Привет'
            gdi32.TextOutW(self.dc, 100, 100, s, len(s))
        else:
            # print('window_proc', hwnd, uMsg, wParam, lParam)
            return user32.DefWindowProcW(hwnd, uMsg, wParam, lParam)
        return 0


def main():
    renderer = Renderer()

    res = user32.SetProcessDpiAwarenessContext(c_void_p(-2))
    print('SetProcessDpiAwarenessContext:', res)

    window_class = WNDCLASSW()
    window_class.style = 0
    window_class.lpfnWndProc = WNDPROC(renderer.window_proc)
    window_class.cbClasExtra = 0
    window_class.cbWndExtra = 0
    window_class.hInstance = None
    window_class.hIcon = None
    window_class.hCursor = None
    window_class.hbrBackground = None
    window_class.lpszMenuName = 'MenuName'
    window_class.lpszClassName = 'ClassName'

    res = user32.RegisterClassW(byref(window_class))
    print('RegisterClass:', res)

    hwnd = user32.CreateWindowExW(
        0,  # dwExStyle
        window_class.lpszClassName,
        'WindowName',
        WS_SYSMENU | WS_THICKFRAME,  # dwStyle
        CW_USEDEFAULT,  # X
        CW_USEDEFAULT,  # Y
        CW_USEDEFAULT,  # nWidth
        CW_USEDEFAULT,  # nHeight
        None,  # hWndParent
        None,  # hMenu
        window_class.hInstance,  # hInstance
        None  # lpParam
    )
    print('CreateWindowEx:', hwnd)
    if not hwnd: return

    renderer.set_hwnd(hwnd)

    res = user32.ShowWindow(hwnd, SW_NORMAL)
    print('ShowWindow:', res)

    msg = MSG()
    while True:
        res = user32.GetMessageW(byref(msg), None, 0, 0)
        # print('GetMessage:', res)
        # print('MSG:', msg.hWnd, msg.message, msg.wParam, msg.lParam, msg.time)
        if not res: break
        user32.TranslateMessage(byref(msg))
        user32.DispatchMessageW(byref(msg))

    # if not glfw.init():
    #     raise RuntimeError('Failed to initialize GLFW')
    # version = glfw.get_version_string().decode('ASCII')
    # print('GLFW', version)
    # window = glfw.create_window(640, 480, 'Title', None, None)

    # print(ctypes.windll.user32.RegisterClassA)
    # print(ctypes.windll.user32.GetDC)
    # print(ctypes.windll.gdi32.TextOutA)

    # while not glfw.window_should_close(window):
    #     # glfw.swap_buffers(window)
    #     glfw.poll_events()

    # glfw.terminate()


if __name__ == '__main__':
    main()