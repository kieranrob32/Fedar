#!/usr/bin/env python3
"""Fedar - DNF Package Manager

A modern GTK-based package manager for DNF repositories.
"""

from src.core.app import main
from src.core.logger import logger


if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("Fedar - DNF Package Manager")
    logger.info("=" * 50)
    main()
