import glfw
import skia
from OpenGL import GL as gl
import time

WIDTH, HEIGHT = 640, 480


def main():
    if not glfw.init():
        return
    glfw.window_hint(glfw.STENCIL_BITS, 8)
    window = glfw.create_window(WIDTH, HEIGHT, 'Hello World', None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    context = skia.GrContext.MakeGL()
    backend_render_target = skia.GrBackendRenderTarget(
        WIDTH,
        HEIGHT,
        0,  # sampleCnt
        0,  # stencilBits
        skia.GrGLFramebufferInfo(0, gl.GL_RGBA8))
    surface = skia.Surface.MakeFromBackendRenderTarget(
        context, backend_render_target, skia.kBottomLeft_GrSurfaceOrigin,
        skia.kRGBA_8888_ColorType, skia.ColorSpace.MakeSRGB())
    assert surface is not None

    start = time.time()
    while (glfw.get_key(window, glfw.KEY_ESCAPE) != glfw.PRESS
           and not glfw.window_should_close(window)):
        t = time.time() - start

        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        with surface as canvas:
            canvas.drawCircle(100 + 10 * t, 100 + 10 * t, 40,
                              skia.Paint(Color=skia.ColorGREEN))
        surface.flushAndSubmit()

        glfw.swap_buffers(window)
        glfw.poll_events()

    context.abandonContext()
    glfw.terminate()


if __name__ == "__main__":
    main()
