import glfw
import math
import skia
import time
from OpenGL import GL


class Renderer(object):
    def __init__(self, window):
        self.window = window
        self.context = skia.GrContext.MakeGL()
        self.width, self.height = glfw.get_window_size(window)
        backend_render_target = skia.GrBackendRenderTarget(
            self.width,
            self.height,
            0,  # sampleCnt
            0,  # stencilBits
            skia.GrGLFramebufferInfo(0, GL.GL_RGBA8))
        self.surface = skia.Surface.MakeFromBackendRenderTarget(
            self.context, backend_render_target, skia.kBottomLeft_GrSurfaceOrigin,
            skia.kRGBA_8888_ColorType, skia.ColorSpace.MakeSRGB())
        self.start = time.time()
        assert self.surface is not None

    def __del__(self):
        self.context.abandonContext()

    def render(self):
        t = time.time() - self.start
        with self.surface as canvas:
            canvas.drawCircle(self.width/2 + 100 * math.cos(t), self.height/2 + 100 * math.sin(t), 40,
                              skia.Paint(Color=skia.ColorGREEN))
        self.surface.flushAndSubmit()




def main():
    if not glfw.init():
        raise RuntimeError('Failed to initialize GLFW')

    monitors = glfw.get_monitors()
    for i, monitor in enumerate(monitors):
        name = glfw.get_monitor_name(monitor)
        primary = (glfw.get_monitor_pos(monitor) ==
                   glfw.get_monitor_pos(glfw.get_primary_monitor()))
        print('Monitor #{}: {}{}'.format(i, name.decode('utf8'),
              ' (primary)' if primary else ''))
        width_mm, height_mm = glfw.get_monitor_physical_size(monitor)
        diag_mm = math.sqrt(width_mm*width_mm + height_mm*height_mm)
        print('Diagonal: {:.1f}"'.format(diag_mm / 25.4))
        mode = glfw.get_video_mode(monitor)
        print('Video mode: {}x{} {}Hz {}'.format(mode.size.width, mode.size.height,
              mode.refresh_rate, mode.bits))
        xscale, yscale = glfw.get_monitor_content_scale(monitor)
        print('Scale: {}|{}'.format(xscale, yscale))
        print('Virtual position:', glfw.get_monitor_pos(monitor))
        print('Work ares:', glfw.get_monitor_workarea(monitor))
        print()

    glfw.window_hint(glfw.RESIZABLE, True)
    glfw.window_hint(glfw.STENCIL_BITS, 8)
    glfw.window_hint(glfw.CLIENT_API, glfw.OPENGL_API)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = glfw.create_window(640, 480, 'Title', None, None)
    if window is None:
        glfw.terminate()
        raise RuntimeError('Failed to create a window')

    width, height = glfw.get_window_size(window)
    print('Window size: {}x{}'.format(width, height))
    print('Frame size:', glfw.get_window_frame_size(window))
    width, height = glfw.get_framebuffer_size(window)
    print('Framebuffer size: {}x{}'.format(width, height))
    print('Client API:', glfw.get_window_attrib(window, glfw.CLIENT_API))
    version_major = glfw.get_window_attrib(window, glfw.CONTEXT_VERSION_MAJOR)
    version_minor = glfw.get_window_attrib(window, glfw.CONTEXT_VERSION_MINOR)
    revision = glfw.get_window_attrib(window, glfw.CONTEXT_REVISION)
    print('Version: {}.{} rev{}'.format(version_major, version_minor, revision))

    glfw.make_context_current(window)
    renderer = Renderer(window)

    while not glfw.window_should_close(window):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        renderer.render()
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


if __name__ == '__main__':
    main()