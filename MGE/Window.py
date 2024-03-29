import sys
from ctypes import c_int, c_uint8, byref

from .Common import AllEvents, WindowEvents
from .Keyboard import KeyboardState
from .Time import Time, fps_to_time, get_fps_from_time
from ._sdl import sdl2, sdlgfx
from .Color import Color
from .Texture import _get_sdl2_texture_size
from .Camera import Camera
from .Image import Image, Icon, DefaultIcon, image_to_icon
from .Platform import Platform
from .Constants import *
from .Mesh import rotate_point

__all__ = ["Window"]

class Window:
    def __init__(self, title="MGE", icon: Icon = DefaultIcon, resolution=(1280, 720), location=(300, 300), logical_resolution=(0, 0), shape=None, camera=Camera(), render_driver=All, flags=WindowFlag.Shown | WindowFlag.Resizable):
        self.__Window_Active__ = True

        self._title = title
        self._location = location
        self._resolution = resolution
        self._logical_resolution = logical_resolution

        self.camera = camera

        self._shape = shape
        if self._shape is None:
            self.window = sdl2.SDL_CreateWindow(self._title, self._location[0], self._location[1], self._resolution[0], self._resolution[1], flags)
        else:
            self.window = sdl2.SDL_CreateShapedWindow(self._title.encode(), self._location[0], self._location[1], self._resolution[0], self._resolution[1], flags)
            sdl2.SDL_SetWindowShape(self.window, self._shape, sdl2.SDL_WindowShapeMode())
        self.context = None
        self.renderer = None
        if (flags >> 1) & 1:
            self.context = sdl2.SDL_GL_CreateContext(self.window)
        else:
            self.renderer = sdl2.SDL_CreateRenderer(self.window, render_driver, 0x00000002 | 0x00000008 if Platform.drivers[render_driver].hardware or render_driver == -1 else 0x00000001 | 0x00000008)
        self.__Window_Id__ = sdl2.SDL_GetWindowID(self.window)
        self.logicalResolution = self._logical_resolution
        self.icon = self._icon = icon

        self._variables = {}

        self._limit_time = 60
        self._cache = {"clear_screen": True, "fill": True, "times": {"standard_time": Time(fps_to_time(self._limit_time)), "title_time": Time(0.5), "optimized_time": {"time_start": Time(0.5), "time_loop": Time(fps_to_time(2))}}}
        self.fps = 0

        self.draw_objects = []
        self.render_all_objects = True

    def __repr__(self):
        return f"<%s.%s resolution=%dx%d at 0x%X>" % (
            self.__class__.__module__,
            self.__class__.__name__,
            self._resolution[0],
            self._resolution[1],
            id(self)
        )

    @property
    def flags(self):
        return sdl2.SDL_GetWindowFlags(self.window)

    @property
    def limit_time(self):
        return self._limit_time

    @limit_time.setter
    def limit_time(self, value):
        self._limit_time = value
        self._cache["times"]["standard_time"].delta_time = fps_to_time(self._limit_time) if self._limit_time > 0 else 0

    @property
    def variables(self):
        return self._variables

    @variables.setter
    def variables(self, variables):
        self._variables = variables

    def update(self, still_frame_optimization: bool = False):
        if self.__Window_Active__:
            if still_frame_optimization:
                if AllEvents() or any(KeyboardState()):
                    self._cache["times"]["optimized_time"]["time_start"].restart()
                else:
                    if self._cache["times"]["optimized_time"]["time_start"].tick():
                        if not self._cache["times"]["optimized_time"]["time_loop"].tick(True):
                            return False
            if self._cache["times"]["standard_time"].tick(True):
                self.fps = get_fps_from_time(self._cache["times"]["standard_time"])

                self._resolution = list(sdl2.SDL_GetWindowSize(self.window))

                if WindowEvents(self.__Window_Id__, 14):
                    self.close()
                    return

                self.draw_objects.clear()
                self._cache["clear_screen"] = True
                self._cache["fill"] = True

                if (self.flags >> 1) & 1:
                    sdl2.SDL_GL_SwapWindow(self.window)
                else:
                    sdl2.SDL_RenderPresent(self.renderer)
                return True
        return False

    def recreate(self, title="MGE", icon: Icon = DefaultIcon, resolution=(1280, 720), location=(300, 300), logical_resolution=(0, 0), shape=None, camera=Camera(), flags=WindowFlag.Shown | WindowFlag.Resizable):
        self.close()
        self.__init__(title=title, icon=icon, resolution=resolution, location=location, logical_resolution=logical_resolution, shape=shape, camera=camera, flags=flags)

    def restore(self):
        sdl2.SDL_RestoreWindow(self.window)

    def show(self):
        sdl2.SDL_ShowWindow(self.window)

    def hide(self):
        sdl2.SDL_HideWindow(self.window)

    def maximize(self):
        sdl2.SDL_MaximizeWindow(self.window)

    def minimize(self):
        sdl2.SDL_MinimizeWindow(self.window)

    def close(self):
        self.clear(True)
        if self.window is not None:
            sdl2.SDL_DestroyWindow(self.window)
        if self.renderer is not None:
            sdl2.SDL_DestroyRenderer(self.renderer)
        if self.context is not None:
            sdl2.SDL_GL_DeleteContext(self.context)
        self.window = self.renderer = None
        self.__Window_Active__ = False

    def clear(self, force=False, color=(0, 0, 0, 255)):
        if self.__Window_Active__ and not (self.flags >> 1) & 1:
            if force or self._cache["clear_screen"]:
                tmp = self.color
                self.color = color
                sdl2.SDL_RenderClear(self.renderer)
                self.color = tmp
                self._cache["clear_screen"] = False
                self._cache["fill"] = True

    def getImage(self):
        _Image = Image()
        _Image.image = sdl2.SDL_CreateRGBSurface(0, self._resolution[0], self._resolution[1], 32, 0, 0, 0, 0).contents
        sdl2.SDL_RenderReadPixels(self.renderer, None, sdl2.SDL_PIXELFORMAT_ARGB8888, _Image.image.pixels, _Image.image.pitch)
        _Image._size = self._resolution
        _Image._format = ImageFormat.ARGB
        return _Image

    def blit(self, surface: Image | sdl2.SDL_Surface | sdl2.SDL_Texture, location=(0, 0), size=None, rotation: int = 0):
        if self.__Window_Active__ and not (self.flags >> 1) & 1:
            create_texture = False
            #if isinstance(surface, Surface):
            #    texture = surface.surface
            #    _size = surface.size if size is None else size
            if isinstance(surface, Image):
                texture = sdl2.SDL_CreateTextureFromSurface(self.renderer, surface.image)
                sdl2.SDL_SetTextureScaleMode(texture, 1)
                create_texture = True
                _size = surface.image.size if size is None else size
            elif isinstance(surface, sdl2.SDL_Surface):
                texture = sdl2.SDL_CreateTextureFromSurface(self.renderer, surface)
                sdl2.SDL_SetTextureScaleMode(texture, 1)
                create_texture = True
                _size = (surface.w, surface.h) if size is None else size
            elif isinstance(surface, sdl2.SDL_Texture):
                texture = surface
                _size = _get_sdl2_texture_size(texture) if size is None else size
            else:
                return

            #os.environ["SDL_RENDER_SCALE_QUALITY"] = "1"
            if rotation != 0:
                sdl2.SDL_RenderCopyExF(self.renderer, texture, None, sdl2.SDL_FRect(*location, *_size), rotation, sdl2.SDL_FPoint(_size[0] // 2, _size[1] // 2), sdl2.SDL_FLIP_NONE)
            else:
                sdl2.SDL_RenderCopy(self.renderer, texture, None, sdl2.SDL_Rect(*location, *_size))
            if create_texture:
                sdl2.SDL_DestroyTexture(texture)

    def drawPixel(self, location, color: Color):
        sdlgfx.pixelRGBA(self.renderer, *location, *color.RGBA)

    def drawSquare(self, location, size, rotation, radius, color: Color):
        if self.__Window_Active__ and not (self.flags >> 1) & 1:
            def _square(renderer_, location_, size_, radius_, color_):
                if radius_ > 0:
                    sdlgfx.roundedBoxRGBA(renderer_, location_[0], location_[1], location_[0] + size_[0] - 1, location_[1] + size_[1] - 1, radius_, *color_.RGBA)
                else:
                    sdlgfx.boxRGBA(renderer_, location_[0], location_[1], location_[0] + size_[0] - 1, location_[1] + size_[1] - 1, *color_.RGBA)
            if rotation != 0:
                mask = sdl2.SDL_CreateRGBSurface(0, size[0], size[1], 32, 0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000).contents
                _renderer = sdl2.SDL_CreateSoftwareRenderer(mask)
                _square(_renderer, [0, 0], size, radius, color)
                _texture = sdl2.SDL_CreateTextureFromSurface(self.renderer, mask).contents
                sdl2.SDL_SetTextureScaleMode(_texture, 1)
                self.blit(_texture, [location[0], location[1]], size, rotation)
                sdl2.SDL_DestroyTexture(_texture)
                sdl2.SDL_DestroyRenderer(_renderer)
                sdl2.SDL_FreeSurface(mask)
            else:
                _square(self.renderer, location, size, radius, color)

    def drawEdgesSquare(self, location, size, rotation, line_size, radius, color: Color):
        if self.__Window_Active__ and not (self.flags >> 1) & 1:
            if line_size != 0:
                def _hollow_square(renderer_, location_, size_, line_size_, radius_, color_):
                    for num in range(line_size_ if line_size_ > 0 else -line_size_):
                        num = num if line_size_ > 0 else -num
                        if radius_ > 0:
                            sdlgfx.roundedRectangleRGBA(renderer_, location_[0] - num, location_[1] - num, location_[0] + size_[0] + num, location_[1] + size_[1] + num, radius_, *color_.RGBA)
                        else:
                            sdlgfx.rectangleRGBA(renderer_, location_[0] - num, location_[1] - num, location_[0] + size_[0] + num, location_[1] + size_[1] + num, *color_.RGBA)
                if rotation not in [0, 90, 180, 240, 360]:
                    _size = [size[0] + (line_size * 2 if line_size > 1 else 0), size[1] + (line_size * 2 if line_size > 1 else 0)]
                    _location = [line_size if line_size > 1 else 0, line_size if line_size > 1 else 0]
                    mask = sdl2.SDL_CreateRGBSurface(0, _size[0], _size[1], 32, 0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000).contents
                    _renderer = sdl2.SDL_CreateSoftwareRenderer(mask)
                    _hollow_square(_renderer, _location, size, line_size, radius, color)
                    self.blit(mask, [location[0] - _location[0], location[1] - _location[1]], None, rotation)
                    sdl2.SDL_DestroyRenderer(_renderer)
                    sdl2.SDL_FreeSurface(mask)
                else:
                    _hollow_square(self.renderer, location, size, line_size, radius, color)

    def drawLine(self, start, end, size, color: Color):
        if self.__Window_Active__ and not (self.flags >> 1) & 1:
            if size != 0:
                if size == 1:
                    sdlgfx.aalineRGBA(self.renderer, *start, *end, *color.RGBA)
                else:
                    sdlgfx.thickLineRGBA(self.renderer, *start, *end, size if size > 0 else -size, *color.RGBA)

    def drawPolygon(self, location, scale, rotation: int, mesh: list[list[int, int]], color: Color):
        if self.__Window_Active__ and not (self.flags >> 1) & 1:
            _mesh = [(round(point[0] * scale[0]), round(point[1] * scale[1])) for point in mesh]

            if rotation != 0:
                _max_vx = max(round(point[0] * scale[0]) for point in mesh)
                _max_vy = max(round(point[1] * scale[1]) for point in mesh)
                _mesh = [rotate_point(v[0], v[1], _max_vx / 2, _max_vy / 2, rotation) for v in _mesh]

            _vx = [point[0] + location[0] for point in _mesh]
            _vy = [point[1] + location[1] for point in _mesh]
            _n = len(_vx)

            sdlgfx.filledPolygonRGBA(self.renderer, (sdl2.Sint16 * _n)(*map(int, _vx)), (sdl2.Sint16 * _n)(*map(int, _vy)), _n, *color.RGBA)

    def drawEdgesPolygon(self, location, scale, rotation, mesh, color: Color):
        if self.__Window_Active__ and not (self.flags >> 1) & 1:
            _mesh = [(round(point[0] * scale[0]), round(point[1] * scale[1])) for point in mesh]

            if rotation != 0:
                _max_vx = max(round(point[0] * scale[0]) for point in mesh)
                _max_vy = max(round(point[1] * scale[1]) for point in mesh)
                _mesh = [rotate_point(v[0], v[1], _max_vx / 2, _max_vy / 2, rotation) for v in _mesh]

            _vx = [point[0] + location[0] for point in _mesh]
            _vy = [point[1] + location[1] for point in _mesh]
            _n = len(_vx)

            sdlgfx.polygonRGBA(self.renderer, (sdl2.Sint16 * _n)(*map(int, _vx)), (sdl2.Sint16 * _n)(*map(int, _vy)), _n, *color.RGBA)

    @property
    def color(self) -> tuple:
        if not (self.flags >> 1) & 1:
            r, g, b, a = c_uint8(0), c_uint8(0), c_uint8(0), c_uint8(0)
            ret = sdl2.SDL_GetRenderDrawColor(self.renderer, byref(r), byref(g), byref(b), byref(a))
            if ret is None:
                sys.exit("Window_error")
            return r.value, g.value, b.value, a.value
        return 0, 0, 0, 0

    @color.setter
    def color(self, color: Color | list[int, int, int, int]):
        if not (self.flags >> 1) & 1:
            ret = sdl2.SDL_SetRenderDrawColor(self.renderer, *color)
            if ret < 0:
                sys.exit("Window_error")

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title: str):
        if self._title != title:
            if self._cache["times"]["title_time"].tick(True):
                self._title = title
                sdl2.SDL_SetWindowTitle(self.window, str(title).encode())

    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, icon: Image | Icon):
        if isinstance(icon, Icon):
            icon = icon
        elif isinstance(icon, Image):
            icon = image_to_icon(icon)
        else:
            sys.exit()
        sdl2.SDL_SetWindowIcon(self.window, icon.icon)
        self._icon = icon

    @property
    def shape(self):
        return self._shape

    @shape.setter
    def shape(self, shape):
        if self._shape != shape:
            self._shape = shape
            if sdl2.SDL_IsShapedWindow(self.window):
                sdl2.SDL_SetWindowShape(self.window, self._shape, sdl2.SDL_WindowShapeMode())
            else:
                self.recreate(title=self._title, icon=self._icon, resolution=self._resolution, location=self._location, shape=self._shape, camera=self.camera, flags=self.flags)

    @property
    def opacity(self):
        return sdl2.SDL_GetWindowOpacity(self.window)

    @opacity.setter
    def opacity(self, opacity):
        sdl2.SDL_SetWindowOpacity(self.window, opacity)

    @property
    def location(self):
        if self.__Window_Active__:
            x, y = c_int(), c_int()
            sdl2.SDL_GetWindowPosition(self.window, x, y)
            return x.value, y.value
        return self._location

    @location.setter
    def location(self, location):
        if self.__Window_Active__:
            sdl2.SDL_SetWindowPosition(self.window, location[0], location[1])
        self._location = location[0], location[1]

    @property
    def resolution(self) -> tuple:
        if self.__Window_Active__:
            return sdl2.SDL_GetWindowSize(self.window)
        return self._resolution

    @resolution.setter
    def resolution(self, resolution):
        if self.__Window_Active__:
            sdl2.SDL_SetWindowSize(self.window, resolution[0], resolution[1])
        self._resolution = resolution

    @property
    def minimumResolution(self):
        w, h = c_int(), c_int()
        sdl2.SDL_GetWindowMinimumSize(self.window, w, h)
        return w.value, h.value

    @minimumResolution.setter
    def minimumResolution(self, resolution):
        sdl2.SDL_SetWindowMinimumSize(self.window, resolution[0], resolution[1])

    @property
    def maximumResolution(self):
        w, h = c_int(), c_int()
        sdl2.SDL_GetWindowMaximumSize(self.window, w, h)
        return w.value, h.value

    @maximumResolution.setter
    def maximumResolution(self, resolution):
        sdl2.SDL_SetWindowMaximumSize(self.window, resolution[0], resolution[1])

    @property
    def logicalResolution(self) -> tuple:
        if not (self.flags >> 1) & 1:
            r1, r2 = c_int(), c_int()
            sdl2.SDL_RenderGetLogicalSize(self.renderer, r1, r2)
            self._logical_resolution = [r1.value, r2.value]
        return self._logical_resolution if self._logical_resolution[0] != 0 and self._logical_resolution[1] != 0 else self.resolution

    @logicalResolution.setter
    def logicalResolution(self, resolution):
        if not (self.flags >> 1) & 1:
            sdl2.SDL_RenderSetLogicalSize(self.renderer, resolution[0], resolution[1])
            self._logical_resolution = resolution

    @property
    def borderless(self):
        return bool((self.flags >> 4) & 1)

    @borderless.setter
    def borderless(self, v: bool):
        sdl2.SDL_SetWindowBordered(self.window, v)

    @property
    def resizable(self):
        return bool((self.flags >> 5) & 1)

    @resizable.setter
    def resizable(self, v: bool):
        sdl2.SDL_SetWindowResizable(self.window, v)

    @property
    def alwaysOnTop(self):
        return bool((self.flags >> 15) & 1)

    @alwaysOnTop.setter
    def alwaysOnTop(self, v: bool):
        sdl2.SDL_SetWindowAlwaysOnTop(self.window, v)
