from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon

from .controller import Controller
from .utils.logger import get_logger

logger = get_logger(__name__)


class QHadoopTools:
    """
    Main QGIS Plugin class.
    Responsible for UI integration.
    """

    def __init__(self, iface):
        self.iface = iface
        self.controller = Controller(iface)
        self.plugin_dir = ""
        self.actions = []
        self.menu = "&QHadoopTools"


    # Initialize GUI
    def initGui(self):
        self.controller.init_gui()


    # Add menu/toolbar action
    def add_action(self, icon_path, text, callback):

        icon = QIcon(icon_path)
        action = QAction(icon, text, self.iface.mainWindow())

        action.triggered.connect(callback)

        self.iface.addToolBarIcon(action)
        self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

    # Cleanup plugin
    def unload(self):
        self.controller.unload()

        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)
