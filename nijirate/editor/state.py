import threading
from multiprocessing import Pipe, Lock
from typing import List, Optional

import pygame

from editor.component import Component
from editor.previewer.gizmos import BoundingBox, get_bounding_box


class State:
    def __init__(self):
        self.observers = []

        self._do_wireframe = False  # wireframe view
        self._scenegraph: List[Component] = []  # all items to be serialised -> does not include gizmos!
        self._selected: List[Component] = []  # all currently selected items
        self._selection_box: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self._boundingbox: Optional[BoundingBox] = None

    # wireframe - get set

    def set_wireframe(self, value):
        self._do_wireframe = value

    def get_wireframe(self):
        return self._do_wireframe

    # scenegraph - get

    def get_scenegraph(self):
        return self._scenegraph

    def set_scenegraph(self, value):
        self._scenegraph = value

    # selected - get set

    def get_selected(self):
        return self._selected

    def set_selected(self, value):
        self._selected = value
        self._boundingbox = get_bounding_box(value)

    # selectionbox - get set

    def get_selection_box(self):
        return self._selection_box

    def set_selection_box(self, value):
        if value is None:
            raise Exception("selection box cannot be None, use a"
                            "rect with 0 area instead")
        self._selection_box = value

    # boundingbox - get

    def get_boundingbox(self) -> Optional[BoundingBox]:
        return self._boundingbox


class ModelManager:
    def __init__(self, pipe: Pipe, state: Optional[State] = None):
        listenert = threading.Thread(target=self._listen, args=(pipe,))
        listenert.start()

        self._pipe = pipe

        self._cachelock = Lock()
        self._cache = None, False  # we protect the cache with a mutex

        self._dirty = False

        self.state = State() if state is None else state

    def _listen(self, pipe):
        while True:
            fstate = pipe.recv()
            self._cachelock.acquire()
            self._cache = (fstate, True)
            self._cachelock.release()

    def _read_cache(self) -> bool:
        """returns True if this state was updated, False otherwise"""
        with self._cachelock:
            fstate, valid = self._cache
            if not valid:
                return False  # do not update state
            self.state = fstate
            self._cache = None, False
            return True

    def mark_dirty(self):
        self._dirty = True

    def update_state(self):
        if self._read_cache():
            return  # if we read from the cache, avoid sending the state back for no reason
        # send state if it's dirty
        if self._dirty:
            self._pipe.send(self)
        self._dirty = False

    def get_state(self):
        return self.state
