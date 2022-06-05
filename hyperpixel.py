#!/usr/bin/env python3
import os
import sys
import signal
import pygame
import math
from pygame import gfxdraw
from core import isMac

if not isMac():
    from hyperpixel2r import Touch

"""
HyperPixel 2 Base Screen Object

Run with: sudo python3 hue.py
"""
WIDTH=480
HEIGHT=480

class Hyperpixel2r:
    screen = None
    def __init__(self, bordered=True, debug=False, fps=60):
        self._init_display()

        self.screen.fill((0, 0, 0))

        if not isMac():
            pygame.display.update()

        self.center = (240, 240)
        self.radius = 240
        self.inner_radius = 150
        self._draw_bounds = bordered
        self._debug = debug
        self._desiredFPS = fps

        self._running = False
        self._origin = pygame.math.Vector2(*self.center)
        self._clock = pygame.time.Clock()

        # On Pi Zero, needed to run: sudo apt install libsdl2-ttf-2.0-0
        pygame.font.init()
        self.debugFont = pygame.font.Font(None, 40)

        # Draw a White Circle Outline to indicate the edge of the display
        if self._draw_bounds:
          self.draw_bounds()

    def draw_bounds(self, antiAlias=True):
        """
        Draws a circular border at the extent of the screen
        """
        if antiAlias:
          for i in range(0,5):
            pygame.gfxdraw.aacircle(self.screen, self.center[1], self.center[1], self.radius-i, (250,250,250))
        else:
            pygame.draw.circle(self.screen, (250, 250, 250), self.center, self.radius, 4)

    def _debugFPSText(self):
        print("FPS: " + str(int(self._clock.get_fps())))

    def _exit(self, sig, frame):
        self._running = False
        print("\nExiting!...\n")

    def _init_display(self):
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679

        if not isMac():
            DISPLAY = os.getenv("DISPLAY")
            if DISPLAY:
                print("Display: {0}".format(DISPLAY))

            if os.getenv('SDL_VIDEODRIVER'):
                print("Using driver specified by SDL_VIDEODRIVER: {}".format(os.getenv('SDL_VIDEODRIVER')))
                pygame.display.init()
                size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
                self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.NOFRAME | pygame.HWSURFACE)
                return
            else:
                # Iterate through drivers and attempt to init/set_mode
                for driver in ['rpi', 'kmsdrm', 'fbcon', 'directfb', 'svgalib']:
                    os.putenv('SDL_VIDEODRIVER', driver)
                    try:
                        pygame.display.init()
                        size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
                        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.NOFRAME | pygame.HWSURFACE)
                        print("Using driver: {0}, Framebuffer size: {1:d} x {2:d}".format(driver, *size))
                        return
                    except pygame.error as e:
                        print('Driver "{0}" failed: {1}'.format(driver, e))
                        continue
                    break
        else:
            pygame.init()
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."

    def _updatefb(self):
        fbdev = os.getenv('SDL_FBDEV', '/dev/fb0')
        with open(fbdev, 'wb') as fb:
            fb.write(self.screen.convert(16, 0).get_buffer())

    def touch(self, x, y, state):
        target = pygame.math.Vector2(x, y)
        distance = self._origin.distance_to(target)
        angle = pygame.Vector2().angle_to(self._origin - target)

        if distance < self.inner_radius and distance > self.inner_radius - 40:
            return

        angle %= 360
        angle /= 360.0

        if distance < self.inner_radius:
            self._val = angle
        else:
            self._hue = angle

    # OVERRIDE THIS CLASS FOR THE MAIN RUN LOOP
    def run(self):
        self._running = True
        signal.signal(signal.SIGINT, self._exit)
        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self._running = False
                        break

            # DRAW CODE GOES HERE
            pygame.display.flip()
            self._clock.tick(self._desiredFPS)

        pygame.quit()
        sys.exit(0)