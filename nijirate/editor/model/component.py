from abc import ABC, abstractmethod


class ComponentVisitor(ABC):
    @abstractmethod
    def visit_video_holder(self, vholder):
        pass

    @abstractmethod
    def visit_text(self, txt):
        pass

    @abstractmethod
    def visit_sprite(self, spr):
        pass


class Component(ABC):
    x: int
    y: int
    w: int
    h: int

    @abstractmethod
    def accept(self, visitor: ComponentVisitor):
        pass


class VideoHolder(Component):
    def accept(self, visitor: ComponentVisitor):
        visitor.visit_video_holder(self)


class Text(Component):
    content: str
    size: int

    def accept(self, visitor: ComponentVisitor):
        visitor.visit_text(self)


class Sprite(Component):
    path: str

    def accept(self, visitor: ComponentVisitor):
        visitor.visit_sprite(self)
