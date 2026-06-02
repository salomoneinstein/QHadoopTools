from . import resources
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon

from .core.hdfs_service import HDFSService
from .core.geojson_service import GeoJSONService

from .ui.dialogs.copy_from_hdfs_dialog import CopyFromHdfsDialog
from .ui.dialogs.copy_to_hdfs_dialog import CopyToHdfsDialog
from .ui.dialogs.fix_geojson_dialog import FixGeoJsonDialog

from .utils.logger import logger


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

    # ------------------------
    # FEATURES
    # ------------------------

    #COPY FROM HDFS (CON SEÑALES)
    def copy_from_hdfs(self):

        dialog = CopyFromHdfsDialog(self.iface.mainWindow())

        #conectar señal del dialog
        dialog.execute_copy.connect(self._execute_copy_from_hdfs)

        dialog.exec_()


    def _execute_copy_from_hdfs(self, data):

        try:
            conn = data["connection"]

            service = HDFSService(
                host=conn["host"],
                port=conn["port"],
                user=conn["user"]
            )

            service.download(
                data["remote_path"],
                data["local_path"]
            )

            QMessageBox.information(
                self.iface.mainWindow(),
                "Success",
                "File downloaded successfully"
            )

        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Error",
                str(e)
            )

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



    def _execute_copy_to_hdfs(self, data):

        try:
            conn = data["connection"]

            service = HDFSService(
                host=conn["host"],
                port=conn["port"],
                user=conn["user"]
            )

            service.upload(
                data["local_path"],
                data["remote_path"]
            )

            QMessageBox.information(
                self.iface.mainWindow(),
                "Success",
                "File uploaded successfully"
            )

        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Error",
                str(e)
            )
            

    #FIX GEOJSON
    def fix_geojson(self):

        dialog = FixGeoJsonDialog(self.iface.mainWindow())

        dialog.execute_copy.connect(self._execute_fix_geojson)

        dialog.exec_()

    def _execute_fix_geojson(self, data):

        try:
            logger.info("[Controller] Fix GeoJSON")

            self.geojson_service.fix(
                data["input_path"]
            )

            QMessageBox.information(
                self.iface.mainWindow(),
                "Success",
                "GeoJSON fixed successfully"
            )

        except Exception as e:
            logger.error(f"[Controller] Fix failed: {e}")

            QMessageBox.critical(
                self.iface.mainWindow(),
                "Error",
                str(e)
            )
            
            

            
    #COPY TO HDFS
    def copy_to_hdfs(self):

        dialog = CopyToHdfsDialog(self.iface.mainWindow())

        dialog.execute_copy.connect(self._execute_copy_to_hdfs)
        dialog.test_connection.connect(self._test_connection)

        dialog.exec_()
        
    

        
    def _test_connection(self, conn_data):

        try:
            logger.info("[Controller] Testing HDFS connection")

            # crear cliente temporal
            test_client = HDFSService(
                host=conn_data["host"],
                port=conn_data["port"],
                user=conn_data["user"]
            )

            #prueba simple: listar raíz
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

