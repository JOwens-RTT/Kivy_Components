from ctypes import sizeof
from kivy.app import App
from kivy.graphics import *
from kivy.graphics.instructions import *
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.layout import Layout
from kivy.core.window import Window
from kivy.properties import (
    ListProperty,
    BooleanProperty,
    NumericProperty,
    StringProperty
)

class NavBarTabBase(Screen):
    pass

class NavBar(Layout):
    # Tabs
    tabs = ListProperty([])
    tabSpacing = NumericProperty(0.1)
    tabSizeHint = ListProperty([None, None])

    # Positioning and size
    orientToTop = BooleanProperty(True)
    extendPastBounds = BooleanProperty(False)

    # Color Scheme
    backgroundColor = ListProperty([1,1,1,1])
    tabBackgroundColor = ListProperty([1,0,0,1])
    tabColor = ListProperty([0,1,0,1])
    tabBorderColor = ListProperty([0,0,1,1])
    highlightColor = ListProperty([0.1,1,0.1,1])

    ################################################ INIT & ORGANIZATION METHODS ################################################

    def __init__(self, **kwargs):
        super(NavBar, self).__init__(**kwargs)
        # Extract kwargs
        parent = self.parent
        px,py = 0.0,0.0
        if parent is None:
            parent = Window
        else:
            px,py = parent.pos

        width, height = parent.size

        # Declare paramters
        self.barPos = px,py
        self.barSize = width * self.size_hint_x, height * self.size_hint_y
        self.contentPos = px, self.barSize[1]
        self.contentSize = width * self.size_hint_x, height - self.barSize[1]
        self.tabSize = [10,10]
        self.activeTab = 0

        # Create bindings
        fbind = self.fbind
        update = self._trigger_layout
        findTabs = self._findTabs
        fbind('tabs', update)
        fbind('tabSpacing', update)
        fbind('orientToTop', update)
        fbind('extendPastBounds', update)
        fbind('backgroundColor', update)
        fbind('tabBackgroundColor', update)
        fbind('tabColor', update)
        fbind('tabBorderColor', update)
        fbind('highlightColor', update)
        fbind('children', findTabs)
        fbind('size', update)
        fbind('pos', update)
        fbind('size_hint', update)

    def _findTabs(self, *largs, **kwargs):
        self.tabs.clear()
        self.activeTab = 0
        
        # Search children for NavBarTabs
        for child in self.children:
            if isinstance(child, NavBarTabBase):
                # NavBarTab found. Add to tabs.
                self.tabs.append(child)
        self.tabs.reverse()

        
    ################################################ UPDATE METHODS ################################################

    def do_layout(self, *largs, **kwargs):
        width, height = kwargs.get("size", self.size)
        x, y = kwargs.get("pos", self.pos)
        self._calcTabSize()
        for tab in self.tabs:
            self.drawTab(self.tabs.index(tab))
        self.drawBackground()

    def _calcTabSize(self):
        # Make sure tab spacing is in range [0,1] or 0.1 if not specified
        if self.tabSpacing is None:
            self.tabSpacing = 0.1
        else:
            self.tabSpacing = self._limit(self.tabSpacing, 0.0, 1.0)

        tabWidth, tabHeight = self.tabSizeHint

        # Calculate tab sizes based on layout style
        if self.extendPastBounds:
            # Tabs should be allowed to exit the bounds of the control
            
            if tabWidth is None:
                # Allow space for 4 tabs at a time by default
                tabWidth = 1.0 / (4 * (1 + self.tabSpacing) + self.tabSpacing)
                
            if tabHeight is None:
                # Fill entire vertical space
                tabHeight = 1.0
            
            self.tabSizeHint = self._limit(tabWidth, 0.0, 1.0), self._limit(tabHeight, 0.0, 1.0)
            self.tabSpacing = (1.0 - 4 * tabWidth) / (5)
        else:
            # Tabs should be contained within the bounds of the control. DO NOT use the user defined tab size recommendations.
            numOfChildren = len(self.tabs)

            # Calculate tab width hint
            tabWidth = 1.0 / (numOfChildren * (1 + self.tabSpacing) + self.tabSpacing)
            if tabHeight is None:
                # Fill entire vertical space
                tabHeight = 1.0
            else:
                # Fill vertical space to specified limit
                tabHeight = self._limit(self.tabSizeHint[1], 0.0, 1.0)
            self.tabSizeHint = tabWidth, tabHeight
            self.tabSpacing = (1.0 - numOfChildren * tabWidth) / (numOfChildren + 1)

    ################################################ DRAW METHODS ################################################

    def drawRect(self, pos, size, color):
        canvas = self.canvas
        rect = InstructionGroup()
        rect.add(Color(rgba=color))
        rect.add(Rectangle(pos=pos, size=size))
        canvas.add(rect)

    def drawBackground(self):
        print("Drawing background...")
        self.drawRect(self.contentPos, self.contentSize, self.backgroundColor)
        self.drawRect(self.barPos, self.barSize, self.tabBackgroundColor)

    def drawTab(self, index):
        # NavBar size and location
        x, y = self.barPos
        width, height = self.barSize

        # Tab size and location
        tabWidth = width * self.tabSizeHint[0]
        tabHeight = height * self.tabSizeHint[1]
        tabX, tabY = x, y
        color = self.tabColor
        if index == self.activeTab: color = self.highlightColor

        # Calculate tab width, spacing, and Y location
        numOfTabs = len(self.tabs)
        spacing = self.tabSpacing * width
        elementWidth = tabWidth + spacing
        verticalSpacing = (height - tabHeight) / 2.0
        tabY = y + verticalSpacing

        # Calculate tab position if tabs are anchored to either the left or right
        distFromLeft = spacing + self.activeTab * elementWidth
        distFromRight = (numOfTabs - self.activeTab) * elementWidth
        halfWidth = 0.5 * width

        # Determine tab justification
        if distFromLeft < halfWidth or not self.extendPastBounds:
            # Left justify tabs
            tabX = x + spacing + index * elementWidth
        elif distFromRight < halfWidth:
            # Right justify tabs
            tabX = (x + width) - (numOfTabs - index) * elementWidth
        else:
            # Center justify on active tab
            activeX = (x + width - tabWidth) / 2
            displacement = index - self.activeTab
            tabX = activeX + displacement * elementWidth

        self.drawRect((tabX,tabY), (tabWidth,tabHeight), color)



    ################################################ DATA MANIPULATION METHODS ################################################

    def _limit(self, value, min, max):
        #if value is None: return None
        if min is not None and value < min: value = min
        elif max is not None and value > max: value = max
        return value


class MainApp(App):
    def build(self):
        Window.size = 600,600
        self.root = root = NavBar(
            #size=(600,600), 
            size_hint=(1.0,0.1)
        )
        root.add_widget(NavBarTabBase())
        root.add_widget(NavBarTabBase())
        root.add_widget(NavBarTabBase())
        root.add_widget(NavBarTabBase())
        root.add_widget(NavBarTabBase())
        return root

if __name__ == '__main__':
    MainApp().run()