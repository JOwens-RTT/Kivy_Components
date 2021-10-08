from math import pi
from typing import Text
from kivy.app import App
from kivy.core import window
from kivy.core.image import Texture
from kivy.graphics import *
from kivy.graphics.instructions import *
from kivy.lang.builder import Instruction
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.layout import Layout
from kivy.uix.image import Image, AsyncImage
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock
import random
import math
from kivy.properties import (
    ListProperty,
    BooleanProperty,
    NumericProperty,
    StringProperty,
    ObjectProperty,
    ReferenceListProperty,
    OptionProperty,
    ColorProperty,
    DictProperty
)

class Screensaver(Layout):
    color = ListProperty([0,1,0,1])

    sleepTime = NumericProperty(.25)       # minutes

    fadeTime = NumericProperty(0.25)    # seconds

    def __init__(self, **kwargs):
        super(Screensaver, self).__init__(**kwargs)
        #super(Screensaver, self).__init__()
        self._loaded = False
        self._fadeAnimTime = 0
        self._animTime = 0
        self._fadeFlag = False
        self._stopAnimFlag = False
        self.opacity = 0.0
        self.direction = random.random() * 2 * math.pi
        self._asleep = False

        fbind = self.fbind
        update = self._trigger_layout
        fbind('size', update)
        fbind('pos', update)
        fbind('_bgc', update)
        fbind('color', update)
        fbind('opacity', update)

    def onLoad(self):
        print("Loaded")
        self._bgc = self.color
        self._startSleepTimer()

    def _fadeInHandler(self, dt) -> bool:
        self._fadeAnimTime += dt
        self.opacity = self._fadeAnimTime / self.fadeTime
        if self.opacity >= 1.0:
            self.opacity = 1.0
            self._fadeFlag = False
            self._asleep = True
            print("Asleep.")
            return False
        return True
        
    def _fadeOutHandler(self, dt) -> bool:
        self._fadeAnimTime += dt
        self.opacity = 1 - (self._fadeAnimTime / self.fadeTime)
        if self.opacity <= 0.0:
            self.opacity = 0.0
            self._fadeFlag = False
            self._asleep = False
            print("Awake.")
            self._startSleepTimer()
            return False
        return True

    def _startSleepTimer(self):
        if self._asleep: return
        print("Starting sleep timer.")
        self._sleepTimer = Clock.schedule_once(lambda dt: self._fadeIn(), self.sleepTime * 60)

    def resetSleep(self):
        '''
        Call this function when the user does an action to keep the screen awake,
        or to wake the screen after it goes to sleep.
        '''
        if self._asleep:
            self._fadeOut()
        else:
            print("Resetting sleep timer...")
            self._sleepTimer.cancel()
            self._startSleepTimer()

    def _fadeIn(self) -> None:
        if self._fadeFlag or self._asleep: return
        self._fadeFlag = True

        self._fadeAnimTime = 0.0
        fadeResolution = 100
        clockInterval = self.fadeTime / fadeResolution
        Clock.schedule_interval(self._fadeInHandler, clockInterval)
        print("Going to sleep...")

    def _fadeOut(self) -> None:
        if self._fadeFlag or (not self._asleep): return
        self._fadeFlag = True
        self._stopAnimFlag = True

        self._fadeAnimTime = 0.0
        fadeResolution = 100
        clockInterval = self.fadeTime / fadeResolution
        Clock.schedule_interval(self._fadeOutHandler, clockInterval)
        print("Waking...")

    def _drawRect(self, pos, size, color):
        canvas = self.canvas.before
        rect = InstructionGroup()
        rect.add(Color(rgba=color))
        rect.add(Rectangle(pos=pos, size=size))
        canvas.add(rect)

    def _drawBackground(self):
        self._drawRect(self.pos, self.size, self._bgc)

    def do_layout(self, *largs, **kwargs):
        if not self._loaded:
            self.onLoad()
            self._loaded = True

        x, y = self.pos
        width, height = self.size

        self._drawBackground()
        
if __name__ == '__main__':
    class KeyboardListener(Widget):
        def __init__(self, **kwargs):
            super(KeyboardListener, self).__init__(**kwargs)
            self._keyboard = Window.request_keyboard(
                self._keyboard_closed, self, 'text')
            if self._keyboard.widget:
                # If it exists, this widget is a VKeyboard object which can be used
                # to change the keyboard layout.
                pass
            self._keyboard.bind(on_key_down=self._on_keyboard_down)

        def _keyboard_closed(self):
            self._keyboard.unbind(on_key_down=self._on_keyboard_down)
            self._keyboard = None

        def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
            # Keycode is composed of an integer + a string
            # If escape is hit, release the keyboard
            if keycode[1] == 'escape':
                keyboard.release()
            
            # Return True to accept the key. Otherwise, it will be used by the system.
            return True

    class MainApp(App, KeyboardListener):
        def __init__(self, **kwargs):
            super(MainApp, self).__init__(**kwargs)

        def build(self):
            Window.size = 600,600
            
            self.root = root = FloatLayout(
                size_hint=(1.0,1.0),
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            self.saver = Screensaver(
                size_hint=(1.0,1.0),
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            self.background = Image(
                source="testImage.png",
                size_hint=(1,1),
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            root.add_widget(self.saver, canvas='after')
            root.add_widget(self.background)

            return root

        def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
            super()._on_keyboard_down(keyboard, keycode, text, modifiers)
            button = keycode[1]
            self.saver.resetSleep()
            return False

    app = MainApp().run()
