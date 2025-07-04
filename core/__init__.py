#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core module for TikTok Virtual Streamer
抖音虚拟主播核心模块
"""

__version__ = "1.0.0"
__author__ = "TikTok Virtual Streamer Team"

from .live_data_manager import LiveDataManager

__all__ = [
    'LiveDataManager'
]