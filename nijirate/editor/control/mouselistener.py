from abc import abstractmethod, ABC


class MouseListener(ABC):
    def __init__(self):
        self._mouseprevpressed = False

    @abstractmethod
    def mousedown(self, pos):
        self._mouseprevpressed = True
        return True

    @abstractmethod
    def mousemotion(self, pos):
        pass

    @abstractmethod
    def mouseup(self, pos) -> None:
        pass

    def domouseup(self, pos):
        # only register mouse released events
        # on listeners that previously registered mousedown
        if self._mouseprevpressed:
            self.mouseup(pos)
        self._mouseprevpressed = False

