from kivy.app import App
from kivy.graphics import *
from kivy.uix.relativelayout import RelativeLayout

class MainApp(App):
    def __init__(self):
        super(MainApp, self).__init__()

    def build(self):

        self.root = root = RelativeLayout()

        with root.canvas.before:
            Color(1.0, 0, 0, 1.0)
            Rectangle(pos=(10,10), size=(500,500))

    


if __name__ == '__main__':
    MainApp().run()