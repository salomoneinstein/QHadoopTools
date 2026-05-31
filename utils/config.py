"""
Global configuration for QHadoopTools plugin.
"""


class Config:

    # WebHDFS connection
    HDFS_HOST: str = "localhost"
    HDFS_PORT: int = 50070
    HDFS_USER: str = "hadoop"

    # Networking
    TIMEOUT: int = 120
    RETRIES: int = 3
    RETRY_DELAY: float = 2.0

    # Logging
    LOG_LEVEL: str = "INFO"   # DEBUG, INFO, WARNING, ERROR
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Misc
    CHUNK_SIZE: int = 1024 * 1024  # 1MB for streaming