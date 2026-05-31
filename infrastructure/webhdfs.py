import os
import requests
from typing import Dict, Any

from urllib.parse import urlparse, urlunparse
from ..utils.logger import logger


WEBHDFS_CONTEXT_ROOT = "/webhdfs/v1"


class WebHDFSError(Exception):
    """Custom exception for WebHDFS errors."""
    pass


class WebHDFS:
    """
    Modern WebHDFS client using requests.
    """

    def __init__(self, host: str, port: int, user: str, timeout: int = 120):
        if not host:
            raise ValueError("Host is required")

        if not port:
            raise ValueError("Port is required")

        if not user:
            raise ValueError("User is required")

        self.base_url = f"http://{host}:{port}{WEBHDFS_CONTEXT_ROOT}"
        self.user = user
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers.update({"Connection": "keep-alive"})


    # Core request method
    def _request(
        self,
        method: str,
        path: str,
        op: str,
        params: Dict[str, Any] = None,
        **kwargs
    ) -> requests.Response:

        # safe params
        params = {**(params or {}), "op": op, "user.name": self.user}

        if not path.startswith("/"):
            raise ValueError("HDFS path must start with '/'")

        url = f"{self.base_url}{path}"

        logger.debug(f"[WebHDFS] {method} {url} | params={params}")

        response = self.session.request(
            method=method,
            url=url,
            params=params,
            timeout=self.timeout,
            allow_redirects=False,
            **kwargs
        )

        self._check(response)
        return response


    # Upload file
    def put_file(self, local_path: str, remote_path: str, overwrite: bool = True) -> None:

        if not local_path or not remote_path:
            raise ValueError("Local and remote paths are required")

        logger.info(f"[WebHDFS] PUT {local_path} → {remote_path}")


        #NameNode request (CREATE → redirect)
        resp = self._request(
            method="PUT",
            path=remote_path,
            op="CREATE",
            params={"overwrite": str(overwrite).lower()},
        )

        redirect = resp.headers.get("Location")
        if not redirect:
            raise WebHDFSError("Missing redirect for upload")


        #corregir hostname (localhost → host real)
        parsed = urlparse(redirect)

        #host real que viene del formulario
        original_host = self.base_url.split("//")[1].split(":")[0]

        fixed_redirect = urlunparse((
            parsed.scheme,
            f"{original_host}:{parsed.port}" if parsed.port else original_host,
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment
        ))


        #asegurar user.name
        if "user.name=" not in fixed_redirect:
            separator = "&" if "?" in fixed_redirect else "?"
            fixed_redirect = f"{fixed_redirect}{separator}user.name={self.user}"


        #enviar con Content-Length (NO chunked)
        file_size = os.path.getsize(local_path)

        with open(local_path, "rb") as f:
            upload = self.session.put(
                url=fixed_redirect,
                data=f,
                headers={
                    "Content-Type": "application/octet-stream",
                    "Content-Length": str(file_size)
                },
                timeout=self.timeout
            )

        self._check(upload)

        logger.info("[WebHDFS] PUT completed")



    # Download file
    def get_file(self, remote_path: str, local_path: str) -> None:

        if not remote_path or not local_path:
            raise ValueError("Remote and local paths are required")

        logger.info(f"[WebHDFS] GET {remote_path} → {local_path}")

        #request NameNode (redirect)
        resp = self._request(
            method="GET",
            path=remote_path,
            op="OPEN"
        )

        redirect = resp.headers.get("Location")

        # archivo vacío
        if not redirect:
            with open(local_path, "wb"):
                pass
            logger.info("[WebHDFS] GET completed (empty file)")
            return


        #corregir hostname del redirect
        from urllib.parse import urlparse, urlunparse

        parsed = urlparse(redirect)

        original_host = self.base_url.split("//")[1].split(":")[0]

        fixed_redirect = urlunparse((
            parsed.scheme,
            f"{original_host}:{parsed.port}" if parsed.port else original_host,
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment
        ))

        # asegurar user.name
        if "user.name=" not in fixed_redirect:
            separator = "&" if "?" in fixed_redirect else "?"
            fixed_redirect = f"{fixed_redirect}{separator}user.name={self.user}"


        #download real
        download = self.session.get(
            url=fixed_redirect,
            stream=True,
            timeout=self.timeout
        )

        self._check(download)

        with open(local_path, "wb") as f:
            for chunk in download.iter_content(1024 * 1024):
                if chunk:
                    f.write(chunk)

        download.close()

        logger.info("[WebHDFS] GET completed")



    # List directory
    def list_dir(self, path: str) -> list:

        if not path:
            raise ValueError("Path is required")

        logger.info(f"[WebHDFS] LIST {path}")

        resp = self._request(
            method="GET",
            path=path,
            op="LISTSTATUS"
        )

        try:
            data = resp.json()
            items = data.get("FileStatuses", {}).get("FileStatus", [])
            result = [f.get("pathSuffix", "") for f in items]

            logger.info(f"[WebHDFS] LIST returned {len(result)} items")
            return result

        except Exception:
            return []


    # Error handling
    def _check(self, response: requests.Response) -> None:

        if response.status_code >= 400:
            try:
                error = response.json()
            except ValueError:
                error = response.text

            logger.error(f"[WebHDFS] HTTP {response.status_code}: {error}")

            raise WebHDFSError(
                f"HTTP {response.status_code}: {error}"
            )
            
            
    class ProgressFile:
        def __init__(self, file_obj, total_size, callback):
            self.file = file_obj
            self.total = total_size
            self.sent = 0
            self.callback = callback

        def read(self, size):
            data = self.file.read(size)
            if not data:
                return data

            self.sent += len(data)

            if self.callback:
                percent = int((self.sent / self.total) * 100)
                self.callback(percent)

            return data
