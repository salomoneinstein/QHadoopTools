from qgis.core import QgsTask, QgsMessageLog, Qgis
from ..core.hdfs_service import HDFSService
from ..utils.logger import get_logger
logger = get_logger(__name__)


class HDFSTask(QgsTask):

    def __init__(self, description, data, operation):
        super().__init__(description, QgsTask.CanCancel)
        self.data = data
        self.operation = operation
        self.exception = None


    def run(self):
        try:

            base_text = None

            if self.operation == "upload":
                base_text = "Uploading to HDFS..."

            elif self.operation == "download":
                base_text = "Downloading from HDFS..."

            elif self.operation == "fix_geojson":
                base_text = "Fixing GeoJSON..."

            def progress_callback(value):
                if self.isCanceled():
                    raise Exception("Cancelled")
                
                self.setProgress(value)
                self.setDescription(base_text)

            if self.operation in ("upload", "download"):

                conn = self.data["connection"]

                service = HDFSService(
                    host=conn["host"],
                    port=conn["port"],
                    user=conn["user"]
                )

                if self.operation == "download":
                    service.download(
                        self.data["remote_path"],
                        self.data["local_path"],
                        progress_callback=progress_callback
                    )

                elif self.operation == "upload":
                    service.upload(
                        self.data["local_path"],
                        self.data["remote_path"],
                        progress_callback=progress_callback
                    )

            elif self.operation == "fix_geojson":

                service = self.data["service"]

                service.fix(
                    input_file=self.data["input_file"],
                    output_file=self.data.get("output_file"),
                    progress_callback=progress_callback
                )

            return True

        except Exception as e:
            self.exception = e
            return False


    def finished(self, result):
        if result:
            QgsMessageLog.logMessage(
                "Proceso completado correctamente",
                "QHadoopTools",
                Qgis.Success
            )
        else:
            QgsMessageLog.logMessage(
                f"Error: {self.exception}",
                "QHadoopTools",
                Qgis.Critical
            )