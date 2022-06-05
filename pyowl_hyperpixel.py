#!/usr/bin/env python3
# Designed to run on Raspberry Pi Zero with 480x480 Pimoroni Round Display.
import pygame
import os
from sys import platform
import signal
from core import remap, in_radius, isMac
import color
from pyowl_monitor import OwlMonitor
import threading

# Default HyperPixel Display size is 480x480
WIDTH = 480
HEIGHT = 480

from hyperpixel import Hyperpixel2r

# Touchscreen Python stuff for HyperPixel display
if not isMac():
    from hyperpixel2r import Touch

class UILabel():
    def __init__(self, txt, location, size=(256,30), 
        bg=color.BLACK, 
        color=color.WHITE, 
        font_name="fonts/UniversTE20-Thin.ttf", 
        font_size=24):
        self.bg = bg  
        self.fg = color
        self.size = size
        self.font = pygame.font.Font(font_name, font_size)
        self.txt = txt
        self.txt_surf = self.font.render(self.txt, 1, self.fg)
        self.txt_rect = self.txt_surf.get_rect(center=[s//2 for s in self.size])
        self.surface = pygame.surface.Surface(size)
        self.rect = self.surface.get_rect(center=location)

    def draw(self, screen):
        screen.blit(self.surface, self.rect)


    def update(self, screen):
        self.surface.fill(self.bg)
        self.txt_surf = self.font.render(self.txt, True, self.fg)
        self.surface.blit(self.txt_surf, self.txt_rect)
        self.draw(screen);

class PyOwlDisplay(Hyperpixel2r):
    def __init__(self):
        Hyperpixel2r.__init__(self)
        self.monitor = OwlMonitor(beingOnStartup = False);
        self.clock = pygame.time.Clock()
        self.consumingText = UILabel("Consuming: ???W", (WIDTH/2, 100), color=color.RED)
        self.generatingText = UILabel("Generating: ???W", ((WIDTH/2, 200)), color=color.BLUE)
        self.exportingText = UILabel("Exporting: ???W", ((WIDTH/2, 300)), color=color.GREEN)
        self.setupGUI()
        self.monitoringThread = threading.Thread(target=self.monitor.startMonitoring)
        self.monitoringThread.setDaemon(True)
        self.monitoringThread.start()

    def setupGUI(self):
        # TODO: SETUP TOUCH
        if platform != "darwin":
            pygame.mouse.set_visible(False)
        else:
            pygame.init()

    def updateText(self):
        self.consumingText.txt = self.monitor.consumingString()
        self.generatingText.txt = self.monitor.generatingString()
        self.exportingText.txt = self.monitor.exportingString()
        self.consumingText.update(self.screen)
        self.generatingText.update(self.screen)
        self.exportingText.update(self.screen)


    def touch(self, x, y, state):
        touch = pygame.math.Vector2(x, y)
        distance = self._origin.distance_to(touch)
        angle = pygame.math.Vector2().angle_to(self._origin - touch)
        angle %= 360

        value = (distance / 240.0)
        value = min(1.0, value)
        print("touch, angle: %s, distance: %s, value: %s " % (str(angle), str(distance), str(value)))

    def run(self):
        # Loop until the user clicks the close button.
        self._running = True
        signal.signal(signal.SIGINT, self._exit)
        while self._running:
            for event in pygame.event.get():   # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    done = True   # Flag that we are done so we exit this loop


            self.screen.fill(color.BLACK)
            self.draw_bounds()
            self.updateText()

            # Go ahead and update the screen with what we've drawn.
            pygame.display.flip()
            self.clock.tick(60)

print("Creating display...")
display = PyOwlDisplay()
print("Display created...")
if not isMac():
    touch = Touch()

    @touch.on_touch
    def handle_touch(touch_id, x, y, state):
        display.touch(x, y, state)

print("Running display...")
display.run()

# Be IDLE friendly. If you forget this line, the program will 'hang'
# on exit.
pygame.quit()
