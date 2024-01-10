from abc import ABC, abstractmethod
from typing import List, Optional

import pygame

from editor.model.component import Component
from editor.model.gizmos import GizmoElement, BoundingBox, get_bounding_box


class StateObserver(ABC):
    @abstractmethod
    def onmessage(self, msg: (str, List[any])):
        pass


class State:
    def __init__(self):
        self.observers = []

        self._do_wireframe = False  # wireframe view
        self._scenegraph: List[Component] = []  # all items to be serialised -> does not include gizmos!
        self._selected: List[Component] = []  # all currently selected items
        self._selection_box: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self._boundingbox: Optional[BoundingBox] = None

    # observers

    def attach_observer(self, obs: StateObserver):
        self.observers.append(obs)

    def remove_observer(self, obs: StateObserver):
        self.observers.remove(obs)

    def broadcast_message(self, msg: str, args: any = None):
        for obs in self.observers:
            obs.onmessage((msg, args))

    # wireframe - get set

    def set_wireframe(self, value):
        self._do_wireframe = value
        self.broadcast_message("wireframe", value)

    def get_wireframe(self):
        return self._do_wireframe

    # scenegraph - get

    def get_scenegraph(self):
        return self._scenegraph

    def set_scenegraph(self, value):
        self._scenegraph = value
        self.broadcast_message("sgset", [value])

    # selected - get set

    def get_selected(self):
        return self._selected

    def set_selected(self, value):
        self._selected = value
        self._boundingbox = get_bounding_box(value)
        self.broadcast_message("selset", [value])
        # NOTE: if setting becomes annoying we can revert to only exposing get and mutating

    # selectedbox - get set

    def get_selected_box(self):
        return self._selection_box

    def set_selected_box(self, value):
        if value is None:
            raise Exception("selected box cannot be None, use a"
                            "rect with 0 area instead")
        self._selection_box = value

    # boundingbox - get

    def get_boundingbox(self) -> Optional[BoundingBox]:
        return self._boundingbox
