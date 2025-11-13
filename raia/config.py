"""
RAIA Inspectors - Configuration Management

Global configuration for RAIA inspectors.
"""

import logging
from typing import Literal, Optional
from pydantic import BaseModel, Field

from raia.storage.base import BaseRAIAStorage
from raia.storage.sqlite import SQLiteRAIAStorage


logger = logging.getLogger(__name__)


class RAIAConfig(BaseModel):
    """
    Configuration for RAIA inspectors.
    """
    default_storage: Optional[BaseRAIAStorage] = Field(
        None,
        description="Default storage backend (will be created if None)"
    )
    app_name: Optional[str] = Field(None, description="Application name")
    environment: Optional[Literal["dev", "staging", "prod"]] = Field(None, description="Environment")
    enable_semantic_eval: bool = Field(False, description="Enable semantic evaluation")
    db_path: str = Field("raia_inspectors.db", description="SQLite database path")

    class Config:
        arbitrary_types_allowed = True

    def get_storage(self) -> BaseRAIAStorage:
        """
        Get or create the storage backend.

        Returns:
            BaseRAIAStorage instance
        """
        if self.default_storage is None:
            logger.info(f"Creating default SQLite storage at {self.db_path}")
            self.default_storage = SQLiteRAIAStorage(db_path=self.db_path)
        return self.default_storage


# Global configuration instance
_global_config: Optional[RAIAConfig] = None


def get_raia_config() -> RAIAConfig:
    """
    Get the global RAIA configuration.

    Returns:
        RAIAConfig instance
    """
    global _global_config
    if _global_config is None:
        _global_config = RAIAConfig()
        logger.info("Initialized default RAIA configuration")
    return _global_config


def set_raia_config(config: RAIAConfig) -> None:
    """
    Set the global RAIA configuration.

    Args:
        config: RAIAConfig instance to use globally
    """
    global _global_config
    _global_config = config
    logger.info(f"Updated RAIA configuration: app={config.app_name}, env={config.environment}")
