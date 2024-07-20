import logging
import os

from lib.extension import extensionId, extensionTitle

logger = logging.getLogger(extensionTitle)
logger.setLevel(logging.DEBUG)
if os.getenv(f'AUTOMATIC1111_EXTENSION_${extensionId.upper()}_DEBUG', '0') == '1':
  logger.info('Activating debug logging')
  logger.setLevel(logging.DEBUG)
