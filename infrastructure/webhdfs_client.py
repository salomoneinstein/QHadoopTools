import time
import random
from typing import Callable

from ..infrastructure.webhdfs import WebHDFS
from ..utils.logger import logger


class WebHDFSClient:

    PREFIX = "[WebHDFS]"

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        retries: int = 3,
        delay: float = 2.0,
        timeout: int = 120,
    ) -> None:

        if not host:
            raise ValueError("Host is required")

        if retries < 1:
            raise ValueError("Retries must be >= 1")

        self.retries = retries
        self.delay = delay

        self.client = WebHDFS(
            host=host,
            port=port,
            user=user,
            timeout=timeout
        )

    # ------------------------
    # Internal retry executor
    # ------------------------
    def _execute(
        self,
        action_name: str,
        operation: Callable[[], None],
        src: str,
        dst: str,
    ) -> None:

        for attempt in range(1, self.retries + 1):
            try:
                logger.info(
                    f"{self.PREFIX} {action_name} {src} → {dst} (attempt {attempt})"
                )

                operation()

                logger.info(f"{self.PREFIX} {action_name} completed")
                return

            except Exception as e:

                # ❗ No reintentar errores lógicos
                if isinstance(e, ValueError):
                    raise

                logger.error(
                    f"{self.PREFIX} {action_name} failed ({src} → {dst}) attempt {attempt}: {e}"
                )

                # Último intento
                if attempt == self.retries:
                    raise RuntimeError(
                        f"{self.PREFIX} {action_name} failed after {self.retries} attempts: {e}"
                    ) from e

                # Backoff exponencial + jitter
                wait = self.delay * (2 ** (attempt - 1)) + random.uniform(0, 1)
                time.sleep(wait)

    # ------------------------
    # Upload file
    # ------------------------
    def put(self, local_path: str, remote_path: str) -> None:

        if not local_path or not remote_path:
            raise ValueError("Local and remote paths are required")

        def upload():
            self.client.put_file(local_path, remote_path)

        self._execute("PUT", upload, local_path, remote_path)

    # ------------------------
    # Download file
    # ------------------------
    def get(self, remote_path: str, local_path: str) -> None:

        if not remote_path or not local_path:
            raise ValueError("Remote and local paths are required")

        def download():
            self.client.get_file(remote_path, local_path)

        self._execute("GET", download, remote_path, local_path)

    # ------------------------
    # List directory
    # ------------------------
    def list(self, path: str) -> list:

        if not path:
            raise ValueError("Path is required")

        def list_op():
            self._result = self.client.list_dir(path)

        self._execute("LIST", list_op, path, path)

        return getattr(self, "_result", [])
