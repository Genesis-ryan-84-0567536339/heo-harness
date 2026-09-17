"""
Heo-Harness: The Modular AI Agent Runtime Framework
Inspired by DeepSeek Harness & Cordis Meta-Framework.
Tác giả & Kiến trúc sư trưởng: Anh Cơ La (genesis.corp.os@gmail.com)
"""

__version__ = "3.0.0-alpha.1"
__author__ = "Anh Cơ La (Ryan)"
__author_email__ = "genesis.corp.os@gmail.com"

from heo_harness.core.context import Context
from heo_harness.core.bus import EventBus
from heo_harness.core.plugin import BasePlugin, PluginMetadata, PluginHealthStatus
from heo_harness.core.manager import PluginManager

__all__ = [
    "Context",
    "EventBus",
    "BasePlugin",
    "PluginMetadata",
    "PluginHealthStatus",
    "PluginManager",
    "__version__",
    "__author__",
    "__author_email__",
]
