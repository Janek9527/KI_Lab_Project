import typing

import arcade
from game_sprite_buttons.game_sprite_button_base_class import HideableGuiElement


class ModifiedUIManager:
    ui_elements: typing.List[HideableGuiElement]

    def __init__(self):
        self.ui_elements = []

    def add_ui_element(self, v):
        self.ui_elements.append(v)

    def on_draw(self):
        for e in self.ui_elements:
            if e.is_visible == True:
                e.draw()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        pass

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        pass

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        pass
