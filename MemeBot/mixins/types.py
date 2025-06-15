"""
Type definitions for MemeBot mixins.
Defines the protocols that mixins expect from the main class.
"""
from __future__ import annotations

from logging import Logger
from maubot.matrix import MaubotMatrixClient
from MemeBot.config import Config


class MixinHost:
    """Base class defining the interface that mixin host classes must implement.
    
    This class ensures type safety by defining the exact interface that
    all mixins expect from the host class. Any class mixing in MemeBot mixins
    should inherit from this class or provide these attributes.
    """
    
    config: Config
    client: MaubotMatrixClient
    log: Logger
    next_global_promotion_time: float
    user_promotion_cooldowns: dict[str, float]
