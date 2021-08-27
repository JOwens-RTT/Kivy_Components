from ctypes import sizeof

from typing import List
from kivy.app import App
from kivy.graphics import *
from kivy.graphics.instructions import *
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.layout import Layout
from kivy.core.window import Window
from kivy.core.text.markup import MarkupLabel as CoreMarkupLabel
from kivy.core.text import Label as CoreLabel, DEFAULT_FONT
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.uix.widget import Widget
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

class NavBarTabBase(RelativeLayout):
    text = StringProperty("Tab")
    fontSize = NumericProperty(5)
    textColor = ColorProperty([1,1,1,1])
    bold = BooleanProperty(False)
    underline = BooleanProperty(False)
    halign = OptionProperty('auto', options=['left', 'center', 'right', 'justify', 'auto'])
    valign = OptionProperty('bottom', options=['bottom', 'middle', 'center', 'top'])
    textSize = ListProperty([None,None])

    def __init__(self, **kwargs):
        super(NavBarTabBase, self).__init__(**kwargs)
        self.fbind('text', self.update)
        self.fbind('textSize', self.update)

    def update(self, *largs, **kwargs):
        pass
        
    def enable(self, enabled):
        if enabled: self.opacity = 1.0
        else: self.opacity = 0.0

class NavBar(Layout):
    # Tabs
    tabs = ListProperty([])
    tabSpacing = NumericProperty(0.1)
    tabSizeHint = ListProperty([None, None])
    tabShape = StringProperty("Rectangle")
    tabRadius = NumericProperty(5)
    tabBorderThickness = NumericProperty(5)
    tabBorderEnable = BooleanProperty(False)
    tabBarHeight = NumericProperty(0.1)
    valign = OptionProperty('center', options=['top', 'center','bottom'])
    tabFontSize = NumericProperty(None)

    # Positioning and size
    orientToTop = BooleanProperty(True)
    extendPastBounds = BooleanProperty(False)
    removeIncompleteTabs = BooleanProperty(False)
    chevronMargin = ListProperty([20,10])
    chevronWidth = NumericProperty(5)

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
        self.barSize = width * self.size_hint_x, height * self.size_hint_y * self.tabBarHeight
        self.contentPos = px, self.barSize[1]
        self.contentSize = width * self.size_hint_x, height * self.size_hint_y - self.barSize[1]
        self.tabSize = [10,10]
        self.activeTab = 0
        self.labels = {}
        self._tabsFound = False
        self._tabSpacingHint = 0.0
        self.loaded = False
        
        # Create bindings
        fbind = self.fbind
        update = self._trigger_layout
        findTabs = self._findTabs
        fbind('_tabsFound', update)
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
        
    def _update_size(self, *largs, **kwargs):
        # Extract kwargs
        parent = self.parent
        px,py = 0.0,0.0
        if parent is None:
            parent = Window
        elif parent is not Window:
            px,py = parent.pos

        # Calculate own width and height
        pWidth, pHeight = parent.size
        width = pWidth * self.size_hint_x
        height = pHeight * self.size_hint_y

        # Calculate dimensions of the nav bar and its content
        self.barSize = width, height * self.tabBarHeight
        self.contentSize = width, height - self.barSize[1]

        # Calculate the bar and content position
        if self.orientToTop:
            self.barPos = px, py + self.contentSize[1]
            self.contentPos = px, py
        else:
            self.barPos = px, py
            self.contentPos = px, py + self.barSize[1]

        # Assign self.size
        self.size = width, height

    def _findTabs(self, *largs, **kwargs):
        self.activeTab = 0
        firstFind = self.tabs == 0
        
        # Search children for NavBarTabs
        for child in self.children:
            if isinstance(child, NavBarTabBase) and not child in self.tabs:
                # NavBarTab found. Add to tabs.
                child.enable(False)
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
                    self.add_widget(self.labels[child])
        if firstFind: 
            self.tabs.reverse()
            self.tabs[0].enable(True)
        self._tabsFound = not self._tabsFound

    def real_remove_widget(self, screen):
        self.remove_widget(screen)
        self._manager.real_remove_widget(screen)

    def switch_tab(self, tab):
        oldTab = self.tabs[self.activeTab]
        oldTab.enable(False)
        tab.enable(True)
        if tab in self.tabs:
            self.activeTab = self.tabs.index(tab)
        self._trigger_layout()

    def getCurrent(self):
        return self.tabs[self.activeTab]

    def next(self):
        newIndex = self.activeTab + 1
        if newIndex > len(self.tabs) - 1:
            newIndex = 0
        elif newIndex < 0:
            newIndex = len(self.tabs) - 1
        self.switch_tab(self.tabs[newIndex])

    def prev(self):
        newIndex = self.activeTab - 1
        if newIndex > len(self.tabs) - 1:
            newIndex = 0
        elif newIndex < 0:
            newIndex = len(self.tabs) - 1
        self.switch_tab(self.tabs[newIndex])
        
    ################################################ UPDATE METHODS ################################################

    def do_layout(self, *largs, **kwargs):
        self.canvas.before.clear()
        self._update_size()
        self._calcTabSize()
        self.drawBackground()

        #self.drawChevron([200,200], [200,200], [10,10], 20, True, [1,0,0,1])

        if not self.loaded and len(self.tabs) > 0:
            self.loaded = True
            self.switch_tab(self.tabs[0])

        for tab in self.tabs:
            # Draw tabs in bar
            self.drawTab(self.tabs.index(tab))
            
            # Update tab content space
            tab.size = self.contentSize
            tab.pos = self.contentPos

            # Update tab text size
            if self.tabFontSize is not None:
                self.labels[tab].font_size = self.tabFontSize

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
            self._tabSpacingHint = (1.0 - 4 * tabWidth) / (5)
        else:
            # Tabs should be contained within the bounds of the control. DO NOT use the user defined tab size recommendations.
            numOfChildren = len(self.tabs)

            # Calculate tab width hint
            tabWidth = 1.0 / (numOfChildren * (1.0 + self.tabSpacing) + self.tabSpacing)
            
            if tabHeight is None:
                # Fill entire vertical space
                tabHeight = 1.0
            else:
                # Fill vertical space to specified limit
                tabHeight = self._limit(self.tabSizeHint[1], 0.0, 1.0)
            self.tabSizeHint = tabWidth, tabHeight
            self._tabSpacingHint = (1.0 - numOfChildren * tabWidth) / (numOfChildren + 1)

    ################################################ DRAW METHODS ################################################

    def drawChevron(self, pos, size, margin, thickness, isleft, color):
        x,y = pos
        width,height = size
        mw,mh = margin

        xVerts = [x+mw, x+width-mw-thickness, x+width-mw, x+mw+thickness, x+width-mw, x+width-mw-thickness, x+mw]
        yVerts = [y+height/2, y+height-mh, y+height-mh, y+height/2, y+mh, y+mh, y+height/2]

        boundX = x + width/2
        boundY = y + height/2

        if isleft is False:
            for i in range(len(xVerts)):
                xVerts[i] = self.invertX(boundX, xVerts[i])

        verts = xVerts + yVerts
        verts[::2] = xVerts
        verts[1::2] = yVerts

        canvas = self.canvas.before
        chevron = InstructionGroup()
        chevron.add(Color(rgba=color))
        chevron.add(Line(points=verts, width=thickness))
        canvas.add(chevron)

    def invertX(self, centerX, x):
        return centerX - (x - centerX)


    def invertY(self, boundBoxCenter, point):
        x,y = point
        bbx, bby = boundBoxCenter
        y = bby - (y - bby)

    def drawRect(self, pos, size, color):
        canvas = self.canvas.before
        rect = InstructionGroup()
        rect.add(Color(rgba=color))
        rect.add(Rectangle(pos=pos, size=size))
        canvas.add(rect)

    def drawRoundedRect(self, pos, size, color, radius):
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
        canvas = self.canvas.before
        rect = InstructionGroup()
        rect.add(Color(rgba=color))
        rect.add(Line(rectangle=(pos[0] + thickness,pos[1] + thickness,size[0] - thickness * 2, size[1] - thickness * 2), width=thickness))
        canvas.add(rect)

    def drawRoundRectBorder(self, pos, size, thickness, color, radius):
        canvas = self.canvas.before
        rect = InstructionGroup()
        rect.add(Color(rgba=color))
        rect.add(Line(rounded_rectangle=(pos[0] + thickness,pos[1] + thickness,size[0] - thickness * 2, size[1] - thickness * 2, radius), width=thickness))
        canvas.add(rect)

    def drawBackground(self):
        self.drawRect(self.contentPos, self.contentSize, self.backgroundColor)
        self.drawRect(self.barPos, self.barSize, self.tabBackgroundColor)

    def drawTab(self, index, text=""):
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
        spacing = self._tabSpacingHint * width
        elementWidth = tabWidth + spacing
        verticalSpacing = (height - tabHeight) / 2.0
        if self.valign == 'top':
            tabY = y + 2 * verticalSpacing
        elif self.valign == 'center':
            tabY = y + verticalSpacing
        else:
            tabY = y

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

        # Determine if the tab is in or out of bounds
        if tabX < x and tabX + tabWidth > x:
            # tab half in left bounds
            self._drawHalfTab([tabX, tabY], [tabWidth, tabHeight], color, 2, True, index)
        elif tabX + tabWidth > x + width and tabX < x + width:
            # out half in right bounds
            self._drawHalfTab([tabX, tabY], [tabWidth, tabHeight], color, 2, False, index)
        elif tabX >= x and tabX + tabWidth <= x + width:
            # tab fully in bounds
            self._drawFullTab([tabX,tabY], [tabWidth, tabHeight], text, color, index)
        else:
            # Tab fully out of bounds
            tab = self.tabs[index]
            if tab in self.labels:
                tabLabel = self.labels[tab]
                tabLabel.text = ""
                tabLabel.pos = tabX,tabY
                tabLabel.size = tabWidth,tabHeight

    def _drawFullTab(self, pos, size, text, color, index):
        tabX, tabY = pos
        tabWidth, tabHeight = size

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
        if tab in self.labels:
            tabLabel = self.labels[tab]
            tabLabel.text = tab.text
            tabLabel.pos = tabX,tabY
            tabLabel.size = tabWidth,tabHeight

    def _drawHalfTab(self, pos, size, color, chevronWidth, isLeft, index):
        tabX, tabY = pos
        tabWidth, tabHeight = size
        tabWidth *= 0.5
        if isLeft:
            tabX += tabWidth

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
        if tab in self.labels:
            tabLabel = self.labels[tab]
            tabLabel.text = ""
            tabLabel.pos = tabX,tabY
            tabLabel.size = tabWidth,tabHeight

        # Display Chevron
        self.drawChevron([tabX, tabY], [tabWidth,tabHeight], self.chevronMargin, self.chevronWidth, isLeft, tab.textColor)

    ################################################ DATA MANIPULATION METHODS ################################################

    def _limit(self, value, min, max):
        #if value is None: return None
        if min is not None and value < min: value = min
        elif max is not None and value > max: value = max
        return value

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
            self.root = root = NavBar(
                size_hint=(1.0,1.0),
                tabBarHeight=0.1,
                tabShape="RoundedRectangle",
                tabRadius=10,
                tabBorderThickness=2.5,
                tabBorderEnable=False,
                extendPastBounds=True,
                highlightColor=(0.2,1.0,0.3,1.0),
                tabColor=(0.5,0.5,0.5,1.0),
                tabBackgroundColor=(0.2,0.2,0.2,1.0),
                backgroundColor=(0.2,0.2,0.2,1.0),
                tabSizeHint=(None, 0.8),
                orientToTop=False,
                valign="center"
            )
            tab1 = NavBarTabBase(text="Tab 1", fontSize=20, halign='center', valign='center', bold=True, size=root.tabSize, pos=root.contentPos)
            float1 = FloatLayout(size=tab1.size, pos=tab1.pos)
            float1.add_widget(Label(text="Hello, World!", pos_hint={'center_x': 0.5, 'center_y': 0.5}))
            tab1.add_widget(float1)        
            tab2 = NavBarTabBase(text="Tab 2", fontSize=20, halign='center', valign='center', bold=True, size=root.tabSize, pos=root.contentPos)
            float2 = FloatLayout(size=tab2.size, pos=tab2.pos)
            float2.add_widget(Label(text="Goodbye!", pos_hint={'center_x': 0.5, 'center_y': 0.5}))
            tab2.add_widget(float2)
            root.add_widget(tab1)
            root.add_widget(tab2)
            root.add_widget(NavBarTabBase(text="Tab 3", fontSize=20, halign='center', valign='center', bold=True))
            root.add_widget(NavBarTabBase(text="Tab 4", fontSize=20, halign='center', valign='center', bold=True))
            root.add_widget(NavBarTabBase(text="Tab 5", fontSize=20, halign='center', valign='center', bold=True))

            return root

        def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
            super()._on_keyboard_down(keyboard, keycode, text, modifiers)
            button = keycode[1]
            if button == 'right':
                self.root.next()
            elif button == 'left':
                self.root.prev()
            else:
                return False
            return True
            
    app = MainApp().run()
