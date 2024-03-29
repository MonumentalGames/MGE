from .Mesh import Mesh2D
from ._sdl.sdl2 import SDL_PIXELFORMAT_RGB24, SDL_PIXELFORMAT_ARGB4444, SDL_PIXELFORMAT_RGBA8888, SDL_PIXELFORMAT_ARGB8888

__all__ = ["WindowFlag", "WindowEvent", "RenderDriver", "ImageFormat",
           "ControllerType", "ControllerButton",
           "MouseButton", "KeyboardButton",
           "Vector", "Pivot2D", "Meshes2D", "All"]

All = -1

class WindowFlag:
    Fullscreen = 0X00000001
    Opengl = 0X00000002
    Shown = 0X00000004
    Hidden = 0X00000008
    Borderless = 0X00000010
    Resizable = 0X00000020
    Minimized = 0X00000040
    Maximized = 0X00000080
    MouseGrabbed = 0X00000100
    InputFocus = 0X00000200
    MouseFocus = 0X00000400
    FullscreenDesktop = (Fullscreen | 0X00001000)
    Foreign = 0X00000800
    AllowHighdpi = 0X00002000
    MouseCapture = 0X00004000
    AlwaysOnTop = 0X00008000
    SkipTaskbar = 0X00010000
    Utility = 0X00020000
    Tooltip = 0X00040000
    PopupMenu = 0X00080000
    KeyboardGrabbed = 0X00100000
    #WindowFlag_Vulkan = 0X10000000
    #WindowFlag_Metal = 0X20000000

class WindowEvent:
    NONE = 0
    SHOWN = 1
    HIDDEN = 2
    EXPOSED = 3
    MOVED = 4
    RESIZED = 5
    SIZE_CHANGED = 6
    MINIMIZED = 7
    MAXIMIZED = 8
    RESTORED = 9
    ENTER = 10
    LEAVE = 11
    FOCUS_GAINED = 12
    FOCUS_LOST = 13
    CLOSE = 14
    TAKE_FOCUS = 15
    HIT_TEST = 16
    ICCPROF_CHANGED = 17
    DISPLAY_CHANGED = 18

class RenderDriver:
    Direct3d = All
    Direct3d11 = All
    Direct3d12 = All
    OpenGL = All
    Software = All

class ImageFormat:
    RGB = (24, SDL_PIXELFORMAT_RGB24)
    ARGB = (32, SDL_PIXELFORMAT_ARGB8888)
    ARGB16 = (16, SDL_PIXELFORMAT_ARGB4444)
    RGBA = (32, SDL_PIXELFORMAT_RGBA8888)

class ControllerType:
    Unknown = 0
    Xbox360 = 1
    XboxONE = 2
    Ps3 = 3
    Ps4 = 4
    NintendoSwitchPRO = 5
    Virtual = 6
    Ps5 = 7
    AmazonLuna = 8
    GoogleStadia = 9
    NvidiaShield = 10
    NintendoSwitchJoyconLeft = 11
    NintendoSwitchJoyconRight = 12
    NintendoSwitchJoyconPair = 13

class ControllerButton:
    A = 0
    B = 1
    X = 2
    Y = 3
    Back = 4
    Guide = 5
    Start = 6
    LeftStick = 7
    RightStick = 8
    LeftShoulder = 9
    RightShoulder = 10
    Up = 11
    Down = 12
    Left = 13
    Right = 14
    Misc1 = 15
    Paddle1 = 16
    Paddle2 = 17
    Paddle3 = 18
    Paddle4 = 19
    Touchpad = 20

class MouseButton:
    Left = 1
    Middle = 2
    Right = 3
    X1 = 4
    X2 = 5

class KeyboardButton:
    KeyboardButton_A = 4
    KeyboardButton_B = 5
    KeyboardButton_C = 6
    KeyboardButton_D = 7
    KeyboardButton_E = 8
    KeyboardButton_F = 9
    KeyboardButton_G = 10
    KeyboardButton_H = 11
    KeyboardButton_I = 12
    KeyboardButton_J = 13
    KeyboardButton_K = 14
    KeyboardButton_L = 15
    KeyboardButton_M = 16
    KeyboardButton_N = 17
    KeyboardButton_O = 18
    KeyboardButton_P = 19
    KeyboardButton_Q = 20
    KeyboardButton_R = 21
    KeyboardButton_S = 22
    KeyboardButton_T = 23
    KeyboardButton_U = 24
    KeyboardButton_V = 25
    KeyboardButton_W = 26
    KeyboardButton_X = 27
    KeyboardButton_Y = 28
    KeyboardButton_Z = 29

    #KeyboardButton_Cedilla = 51

    KeyboardButton_1 = 30
    KeyboardButton_2 = 31
    KeyboardButton_3 = 32
    KeyboardButton_4 = 33
    KeyboardButton_5 = 34
    KeyboardButton_6 = 35
    KeyboardButton_7 = 36
    KeyboardButton_8 = 37
    KeyboardButton_9 = 38
    KeyboardButton_0 = 39

    KeyboardButton_Return = 40
    KeyboardButton_Esc = 41
    KeyboardButton_Back = 42
    KeyboardButton_Tab = 43
    KeyboardButton_Space = 44

    KeyboardButton_Minus = 45
    KeyboardButton_Equals = 46

    F1 = 58
    F2 = 59
    F3 = 60
    F4 = 61
    F5 = 62
    F6 = 63
    F7 = 64
    F8 = 65
    F9 = 66
    F10 = 67
    F11 = 68
    F12 = 69

    KeyboardButton_Right = 79
    KeyboardButton_Left = 80
    KeyboardButton_Down = 81
    KeyboardButton_Up = 82

    KeyboardButton_LeftShift = 225
    KeyboardButton_RightShift = 229
    KeyboardButton_Shift = (KeyboardButton_LeftShift, KeyboardButton_RightShift)
    KeyboardButton_LeftCtrl = 224
    KeyboardButton_RightCtrl = 228
    KeyboardButton_Ctrl = (KeyboardButton_LeftCtrl, KeyboardButton_RightCtrl)
    KeyboardButton_LeftAlt = 226
    KeyboardButton_RightAlt = 230
    KeyboardButton_Alt = (KeyboardButton_LeftAlt, KeyboardButton_RightAlt)

class Vector:
    X = 1
    Y = 2
    GLOBAL = 10
    LOCAL = 30

class Pivot2D:
    Center = 800
    TopLeftSide = 700
    TopRightSide = 750
    LowerLeftSide = 600
    LowerRightSide = 650

class Meshes2D:
    Plane = Mesh2D([])
    Star = Mesh2D([(150, 0), (186, 116), (300, 116), (212, 192), (250, 300), (150, 230), (50, 300), (88, 192), (0, 116), (114, 116)])
    Arrow = Mesh2D([(0, 100), (30, 100), (30, 300), (38, 300), (38, 100), (68, 100), (34, 0)])
