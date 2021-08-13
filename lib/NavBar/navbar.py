from ctypes import sizeof
from kivy.app import App
from kivy.graphics import *
from kivy.graphics.instructions import *
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.layout import Layout
from kivy.core.window import Window
from kivy.core.text.markup import MarkupLabel as CoreMarkupLabel
from kivy.core.text import Label as CoreLabel, DEFAULT_FONT
from kivy.uix.label import Label
from kivy.clock import Clock
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

class NavBarTabBase(Screen):
    text = StringProperty("Tab")
    fontSize = NumericProperty(5)
    textColor = ColorProperty([1,1,1,1])
    bold = BooleanProperty(False)
    underline = BooleanProperty(False)
    halign = OptionProperty('auto', options=['left', 'center', 'right', 'justify', 'auto'])
    valign = OptionProperty('bottom', options=['bottom', 'middle', 'center', 'top'])
    textSize = ListProperty([None,None])

class NavBar(Layout):
    # Tabs
    tabs = ListProperty([])
    tabSpacing = NumericProperty(0.1)
    tabSizeHint = ListProperty([None, None])
    tabShape = StringProperty("RoundedRectangle")
    tabRadius = NumericProperty(20)
    tabBorderThickness = NumericProperty(5)
    tabBorderEnable = BooleanProperty(True)

    # Positioning and size
    orientToTop = BooleanProperty(True)
    extendPastBounds = BooleanProperty(True)

    # Color Scheme
    backgroundColor = ListProperty([1,1,1,1])
    tabBackgroundColor = ListProperty([1,0,0,1])
    tabColor = ListProperty([0,1,0,1])
    tabBorderColor = ListProperty([0,0,1,1])
    highlightColor = ListProperty([0.1,1,0.1,1])

    # Text and Font

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
        self.labels = {}

        # Create bindings
        fbind = self.fbind
        update = self._trigger_layout
        findTabs = self._findTabs
        fbind('tabs', update)
        #fbind('tabSpacing', update)
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
        #parent.fbind('size', self._update_size)

    def _update_size(self, *largs, **kwargs):
        # Extract kwargs
        parent = self.parent
        px,py = 0.0,0.0
        if parent is None:
            parent = Window
        # else:
        #     px,py = parent.pos

        width, height = parent.size

        # Declare paramters
        self.barPos = px,py
        self.barSize = width * self.size_hint_x, height * self.size_hint_y
        self.contentPos = px, self.barSize[1]
        self.contentSize = width * self.size_hint_x, height - self.barSize[1]
        self.tabSize = [10,10]
        self.activeTab = 0
        self.labels = {}
        self.size = self.barSize[0] + self.contentSize[0], self.barSize[1] + self.contentSize[1]

    def _findTabs(self, *largs, **kwargs):
        self.tabs.clear()
        self.activeTab = 0
        
        # Search children for NavBarTabs
        for child in self.children:
            if isinstance(child, NavBarTabBase):
                # NavBarTab found. Add to tabs.
                self.tabs.append(child)
                if not(child in self.labels):
                    self.labels[child] = Label(
                        text=child.text,
                        font_size=child.fontSize,
                        color=child.textColor,
                        valign=child.valign,
                        halign=child.halign,
                        underline=child.underline,
                        bold=child.bold,
                        text_size=child.textSize
                    )
                    App.get_running_app().root.add_widget(self.labels[child])
        self.tabs.reverse()

        
    ################################################ UPDATE METHODS ################################################

    def do_layout(self, *largs, **kwargs):
        self._calcTabSize()
        self.drawBackground()
        for tab in self.tabs:
            self.drawTab(self.tabs.index(tab))

    def _calcTabSize(self):
        # Make sure tab spacing is in range [0,1] or 0.1 if not specified
        if self.tabSpacing is None:
            self.tabSpacing = 0.1
        else:
            self.tabSpacing = self._limit(self.tabSpacing, 0.0, 1.0)

        print("Tab spacing: {}".format(self.tabSpacing))

        tabWidth, tabHeight = self.tabSizeHint
        print("User supplied tab size: ({}, {})".format(tabWidth, tabHeight))

        # Calculate tab sizes based on layout style
        if self.extendPastBounds:
            print("Extending past bounds!")
            # Tabs should be allowed to exit the bounds of the control
            if tabWidth is None:
                # Allow space for 4 tabs at a time by default
                tabWidth = 1.0 / (4 * (1 + self.tabSpacing) + self.tabSpacing)
                print("  Tab width autoset to: {}".format(tabWidth))
                
            if tabHeight is None:
                # Fill entire vertical space
                tabHeight = 1.0
                print("  Tab hight autoset to: {}".format(tabHeight))
            
            self.tabSizeHint = self._limit(tabWidth, 0.0, 1.0), self._limit(tabHeight, 0.0, 1.0)
            self.tabSpacing = (1.0 - 4 * tabWidth) / (5)
            print("  Final size and spacing: size=({}, {}), spacing={}".format(tabWidth, tabHeight, self.tabSpacing))
        else:
            print("Containing tabs to bounds!")
            # Tabs should be contained within the bounds of the control. DO NOT use the user defined tab size recommendations.
            numOfChildren = len(self.tabs)
            print("  Number of tabs: {}".format(numOfChildren))
            print(" Spacing: {}".format(self.tabSpacing))

            # Calculate tab width hint
            tabWidth = 1.0 / (numOfChildren * (1.0 + self.tabSpacing) + self.tabSpacing)
            print("  Autosetting tab width: {:.3f}".format(tabWidth))
            if tabHeight is None:
                # Fill entire vertical space
                tabHeight = 1.0
                print("  Autosetting tab height: {}".format(tabHeight))
            else:
                # Fill vertical space to specified limit
                tabHeight = self._limit(self.tabSizeHint[1], 0.0, 1.0)
                print("  Using user defined tab height: {}".format(tabHeight))
            self.tabSizeHint = tabWidth, tabHeight
            self.tabSpacing = (1.0 - numOfChildren * tabWidth) / (numOfChildren + 1)
            print("  Final size and spacing: size=({}, {}), spacing={}".format(tabWidth, tabHeight, self.tabSpacing))

    ################################################ DRAW METHODS ################################################

    def drawRect(self, pos, size, color):
        print("Drawing Rectangle\n  pos: {}, size: {}, color: {}".format(pos, size, color))
        canvas = self.canvas.before
        rect = InstructionGroup()
        rect.add(Color(rgba=color))
        rect.add(Rectangle(pos=pos, size=size))
        canvas.add(rect)

    def drawRoundedRect(self, pos, size, color, radius):
        print("Drawing Rectangle\n  pos: {}, size: {}, color: {}".format(pos, size, color))
        # Split components
        x,y = pos
        width, height = size

        # Calculate key verticies
        vA = x, y
        vB = x + width - 2*radius, y
        vC = x + width - 2*radius, y + height - 2*radius
        vD = x, y + height - 2*radius
        v1 = x + radius, y
        v2 = x + width - radius, y + radius
        v3 = x + radius, y + height - radius
        v4 = x, y + radius
        v5 = x + radius, y + radius

        # Calculate dimensions
        innerWidth = width - 2 * radius
        innerHeight = height - 2 * radius
        circleSize = radius * 2, radius * 2

        # Create Instruction Group
        rect = InstructionGroup()
        rect.add(Color(rgba=color))                                     # Color setting
        rect.add(Ellipse(pos=vA, size=circleSize))                      # Lower Left Circle
        rect.add(Ellipse(pos=vB, size=circleSize))                      # Lower Right Circle
        rect.add(Ellipse(pos=vC, size=circleSize))                      # Upper Right Circle
        rect.add(Ellipse(pos=vD, size=circleSize))                      # Upper Left Circle
        rect.add(Rectangle(pos=v1, size=(innerWidth, radius)))          # Bottom Edge
        rect.add(Rectangle(pos=v2, size=(radius, innerHeight)))         # Right Edge
        rect.add(Rectangle(pos=v3, size=(innerWidth, radius)))          # Top Edge
        rect.add(Rectangle(pos=v4, size=(radius, innerHeight)))         # Left Edge
        rect.add(Rectangle(pos=v5, size=(innerWidth, innerHeight)))     # Middle Fill
       
        # Draw to canvas
        canvas = self.canvas.before
        canvas.add(rect)

    def drawRectBorder(self, pos, size, thickness, color):
        print("Drawing Rectangle Border\n  pos: {}, size: {}, color: {}".format(pos, size, color))
        canvas = self.canvas.before
        rect = InstructionGroup()
        rect.add(Color(rgba=color))
        rect.add(Line(rectangle=(pos[0] + thickness,pos[1] + thickness,size[0] - thickness * 2, size[1] - thickness * 2), width=thickness))
        canvas.add(rect)

    def drawRoundRectBorder(self, pos, size, thickness, color, radius):
        print("Drawing Rectangle Border\n  pos: {}, size: {}, color: {}".format(pos, size, color))
        canvas = self.canvas.before
        rect = InstructionGroup()
        rect.add(Color(rgba=color))
        rect.add(Line(rounded_rectangle=(pos[0] + thickness,pos[1] + thickness,size[0] - thickness * 2, size[1] - thickness * 2, radius), width=thickness))
        canvas.add(rect)

    def drawBackground(self):
        print("Drawing background...")
        self.drawRect(self.contentPos, self.contentSize, self.backgroundColor)
        self.drawRect(self.barPos, self.barSize, self.tabBackgroundColor)

    def drawTab(self, index, text=""):
        # NavBar size and location
        x, y = self.barPos
        width, height = self.barSize
        print("Draw Tab\n  Tab#: {}, x: {}, y: {}, width: {}, height: {}".format(index, x, y, width, height))

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

        
        if self.tabShape == "Rectangle":
            if self.tabBorderEnable:
                thickness = self.tabBorderThickness
                self.drawRect((tabX + thickness, tabY + thickness), (tabWidth - 2 * thickness,tabHeight - 2 * thickness), color)
                self.drawRectBorder((tabX,tabY), (tabWidth,tabHeight), thickness, self.tabBorderColor)
            else:
                self.drawRect((tabX,tabY), (tabWidth,tabHeight), color)
        elif self.tabShape == "RoundedRectangle":
            
            if self.tabBorderEnable:
                thickness = self.tabBorderThickness
                self.drawRoundedRect((tabX + thickness, tabY + thickness), (tabWidth - 2 * thickness,tabHeight - 2 * thickness), color, self.tabRadius)
                self.drawRoundRectBorder((tabX,tabY), (tabWidth,tabHeight), self.tabBorderThickness, self.tabBorderColor, self.tabRadius)
            else:
                self.drawRoundedRect((tabX,tabY), (tabWidth,tabHeight), color, self.tabRadius)
        else:
            raise Exception("Requested Tab background shape not implemented!!! tabShape = {} is not a valid keyword.".format(self.tabShape))

        # Display Text
        tab = self.tabs[index]
        tabLabel = self.labels[tab]
        tabLabel.text = tab.text
        tabLabel.pos = tabX,tabY
        tabLabel.size = tabWidth,tabHeight

        print("Adding Label\n  Text: {}, pos: {}, size: {}, font_size: {}, color: {}".format(tabLabel.text, tabLabel.pos, tabLabel.size, tabLabel.font_size, tabLabel.color))

    ################################################ DATA MANIPULATION METHODS ################################################

    def _limit(self, value, min, max):
        #if value is None: return None
        if min is not None and value < min: value = min
        elif max is not None and value > max: value = max
        return value

    ################################################ TEXT METHODS ################################################

    

class MainApp(App):
    def build(self):
        Window.size = 600,600
        self.root = root = NavBar(
            size_hint=(1.0,0.1),
            
        )
        root.add_widget(NavBarTabBase(text="Tab 1", fontSize=24, halign='center', valign='center', bold=True))
        root.add_widget(NavBarTabBase(text="Tab 2", fontSize=24, halign='center', valign='center'))
        root.add_widget(NavBarTabBase(text="Tab 3", fontSize=24, halign='center', valign='center'))
        root.add_widget(NavBarTabBase(text="Tab 4", fontSize=24, halign='center', valign='center'))
        root.add_widget(NavBarTabBase(text="Tab 5", fontSize=24, halign='center', valign='center'))
        return root

if __name__ == '__main__':
    MainApp().run()