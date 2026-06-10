from . import resources
from qgis.core import Qgis
from qgis.core import QgsApplication
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon

from .core.hdfs_service import HDFSService
from .core.geojson_service import GeoJSONService
from .tasks.hdfs_task import HDFSTask

from .ui.dialogs.copy_from_hdfs_dialog import CopyFromHdfsDialog
from .ui.dialogs.copy_to_hdfs_dialog import CopyToHdfsDialog
from .ui.dialogs.fix_geojson_dialog import FixGeoJsonDialog
from .utils.logger import get_logger

logger = get_logger(__name__)



class Controller:

    def __init__(self, iface):
        self.iface = iface
        self.hdfs_service = HDFSService()
        self.geojson_service = GeoJSONService()
        self.actions = []

    # GUI INIT
    def init_gui(self):
        self.unload()    
        
        icon = QIcon(":/plugins/QHadoopTools/icons/hdfsToLocal.png")
        print("ICON NULL:", icon.isNull())

        self._add_action(
            "Copy From HDFS",
            self.copy_from_hdfs,
            QIcon(":/plugins/QHadoopTools/icons/hdfsToLocal.png")
        )

        self._add_action(
            "Copy To HDFS",
            self.copy_to_hdfs,
            QIcon(":/plugins/QHadoopTools/icons/localToHdfs.png")
        )

        self._add_action(
            "Fix GeoJSON",
            self.fix_geojson,
            QIcon(":/plugins/QHadoopTools/icons/jsonToGeojson.png")
        )


    def _add_action(self, name, callback, icon=None):

        action = QAction(
            icon if icon else QIcon(),
            name,
            self.iface.mainWindow()
        )

        action.triggered.connect(callback)

        self.iface.addPluginToMenu("QHadoop Tools", action)
        self.iface.addToolBarIcon(action)

        self.actions.append(action)


    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu("QHadoop Tools", action)
            self.iface.removeToolBarIcon(action)

   
    def _execute_copy_from_hdfs(self, data):
        
        self.iface.messageBar().pushMessage(
            "QHadoop Tools",
            "Processing... See Task Manager for progress",
            level=Qgis.Info,
            duration=3
        )

        task = HDFSTask(
            "Downloading from HDFS...",
            data,
            operation="download"
        )
        
        task.setDependentLayers([])

        task.taskCompleted.connect(
            lambda: QMessageBox.information(
                self.iface.mainWindow(),
                "Success",
                "File downloaded successfully"
            )
        )

        task.taskTerminated.connect(
            lambda: QMessageBox.critical(
                self.iface.mainWindow(),
                "Error",
                str(task.exception)
            )
        )

        QgsApplication.taskManager().addTask(task)


    def _execute_copy_to_hdfs(self, data):
        
        
        self.iface.messageBar().pushMessage(
            "QHadoop Tools",
            "processing... See Task Manager for progress",
            level=Qgis.Info,
            duration=3
        )

        task = HDFSTask(
            "Uploading to HDFS...",
            data,
            operation="upload"
        )
        
        task.setDependentLayers([])

        task.taskCompleted.connect(
            lambda: QMessageBox.information(
                self.iface.mainWindow(),
                "Success",
                "File uploaded successfully"
            )
        )

        task.taskTerminated.connect(
            lambda: QMessageBox.critical(
                self.iface.mainWindow(),
                "Error",
                str(task.exception)
            )
        )

        QgsApplication.taskManager().addTask(task)
           
        
    def copy_from_hdfs(self):

        dialog = CopyFromHdfsDialog(self.iface.mainWindow())

        dialog.execute_copy.connect(self._execute_copy_from_hdfs)
        dialog.test_connection.connect(self._test_connection)

        dialog.exec_()
        

    def copy_to_hdfs(self):

        dialog = CopyToHdfsDialog(self.iface.mainWindow())

        dialog.execute_copy.connect(self._execute_copy_to_hdfs)
        dialog.test_connection.connect(self._test_connection)

        dialog.exec_()
        
    
    def fix_geojson(self):
        dialog = FixGeoJsonDialog(self.iface.mainWindow())
        dialog.execute_fix.connect(self._execute_fix_geojson_task)
        dialog.exec_()

                                   
    def _execute_fix_geojson_task(self, data):

        data["service"] = self.geojson_service

        self.iface.messageBar().pushMessage(
            "QHadoop Tools",
            "Processing... See Task Manager for progress",
            level=Qgis.Info,
            duration=3
        )

        task = HDFSTask(
            "Fix GeoJSON",
            data,
            operation="fix_geojson"
        )

        task.setDependentLayers([])

        task.taskCompleted.connect(
            lambda: QMessageBox.information(
                self.iface.mainWindow(),
                "Success",
                "GeoJSON fixed successfully"
            )
        )

        task.taskTerminated.connect(
            lambda: QMessageBox.critical(
                self.iface.mainWindow(),
                "Error",
                str(task.exception)
            )
        )

        QgsApplication.taskManager().addTask(task)

        
    def _test_connection(self, conn_data):

        try:
            logger.info("[Controller] Testing HDFS connection")

            test_client = HDFSService(
                host=conn_data["host"],
                port=conn_data["port"],
                user=conn_data["user"]
            )

            test_client.list("/")

            QMessageBox.information(
                self.iface.mainWindow(),
                "Connection OK",
                "Successfully connected to HDFS"
            )

        except Exception as e:
            logger.error(f"[Controller] Connection failed: {e}")

            QMessageBox.critical(
                self.iface.mainWindow(),
                "Connection Failed",
                str(e)
            )

