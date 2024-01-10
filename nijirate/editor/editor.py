from model import Model
from editor.view.viewer import Viewer


class Editor:
    """
    entry point for *just the editor*. to be launched after
    the splash menu
    """
    def __init__(self):
        self.model = Model()
        self.player = Viewer(self.model)

    def run(self):
        self.player.run()


if __name__ == "__main__":
    m = Editor()
    m.run()
