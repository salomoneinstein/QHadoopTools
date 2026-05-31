import os
from ..infrastructure.webhdfs_client import WebHDFSClient
from ..utils.logger import logger


class HDFSService:
    """
    Service layer for HDFS operations.
    Encapsulates client logic and provides clean API
    for controller layer.
    """


    PREFIX = "[HDFS]"
    
    def __init__(self, host="localhost", port=50070, user="hadoop"):
        self.client = WebHDFSClient(
            host=host,
            port=port,
            user=user
        )
        


    # Upload local → HDFS
    def upload(self, local_path: str, remote_path: str) -> None:

        if not local_path or not remote_path:
            raise ValueError("Local and remote paths are required")

        try:
            logger.info(f"{self.PREFIX} Uploading: {local_path} → {remote_path}")

            self.client.put(local_path, remote_path)

            logger.info(f"{self.PREFIX} Upload completed successfully")

        except Exception as e:
            logger.error(
                f"{self.PREFIX} Upload failed ({local_path} → {remote_path}): {e}"
            )
            raise RuntimeError(f"{self.PREFIX} Upload failed: {e}") from e


    # Download HDFS → local
    def download(self, remote_path: str, local_path: str):

        #intentar descarga directa (archivo)
        try:
            self.client.get(remote_path, local_path)
            return
        except Exception:
            pass  # no es archivo → posiblemente carpeta

        #listar contenido de la carpeta
        files = self.client.list(remote_path)

        #filtrar archivos reales 
        valid_files = [
            f for f in files
            if not f.startswith(".") and not f.startswith("_")
        ]

        if not valid_files:
            raise RuntimeError("No data files found in directory")

        #ordenar archivos 
        valid_files.sort()

        #descargar y unir
 
        first_file = valid_files[0]

        #descargar directamente
        
        remote_file = f"{remote_path.rstrip('/')}/{first_file}"
        self.client.get(remote_file, local_path)






    # List HDFS directory
    def list(self, remote_path: str) -> list:

        if not remote_path:
            raise ValueError("Remote path is required")

        try:
            logger.info(f"{self.PREFIX} Listing: {remote_path}")

            result = self.client.list(remote_path)
            result = [f for f in result if f.startswith("part-")]

            logger.info(f"{self.PREFIX} List completed ({len(result)} items)")

            return result

        except Exception as e:
            logger.error(
                f"{self.PREFIX} List failed ({remote_path}): {e}"
            )
            raise RuntimeError(f"{self.PREFIX} List failed") from e
            
