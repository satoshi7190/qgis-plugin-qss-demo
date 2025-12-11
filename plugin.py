import os

from PyQt5.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .ui.dock import DockPanel

PLUGIN_NAME = "QSS Demo Plugin"


class Plugin:
    def __init__(self, iface):
        self.iface = iface
        self.win = self.iface.mainWindow()
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = PLUGIN_NAME
        self.toolbar = self.iface.addToolBar(PLUGIN_NAME)
        self.toolbar.setObjectName(PLUGIN_NAME)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
    ):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.toolbar.addAction(action)
        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)
        self.actions.append(action)
        return action

    def initGui(self):
        # メニュー設定
        icon_path = os.path.join(os.path.dirname(__file__), "imgs/icon.png")
        self.add_action(
            icon_path=icon_path,
            text="Dock Panel Toggle",
            callback=self.toggle_show_pane,
            parent=self.win,
        )
        self.status_dock = DockPanel(self.iface)
        self.win.addDockWidget(Qt.RightDockWidgetArea, self.status_dock)
        self.status_dock.show()

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(PLUGIN_NAME, action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar


    def toggle_show_pane(self):
        if self.status_dock.isVisible():
            self.status_dock.hide()
        else:
            self.status_dock.show()
            self.status_dock.raise_()  # 最前面に
            self.status_dock.activateWindow()  # フォーカスを与える