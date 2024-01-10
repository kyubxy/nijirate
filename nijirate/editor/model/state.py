from abc import ABC, abstractmethod
from typing import List

from editor.model.component import Component


class StateObserver(ABC):
    @abstractmethod
    def onmessage(self, msg: (str, List[any])):
        pass


class State:
    def __init__(self):
        self.observers = []

        self.do_wireframe = False               # wireframe view
        self.scenegraph: List[Component] = []   # all items to be serialised -> does not include gizmos!
        self.selected: List[Component] = []     # all currently selected items

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
        self.do_wireframe = value
        self.broadcast_message("wireframe", value)

    def get_wireframe(self):
        return self.do_wireframe

    # scenegraph - get

    def get_scenegraph(self):
        return self.scenegraph

    def set_scenegraph(self, sg):
        self.scenegraph = sg
        self.broadcast_message("sgadd", [sg])
