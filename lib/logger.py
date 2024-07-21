import copy
import logging
import os
import sys

from modules import shared

from src.extension import extensionId, extensionTitle

COLORS = {
  'DEBUG': '\033[0;36m', # CYAN
  'INFO': '\033[0;32m', # GREEN
  'WARNING': '\033[0;33m', # YELLOW
  'ERROR': '\033[0;31m', # RED
  'CRITICAL': '\033[0;37;41m', # WHITE ON RED
  'RESET': '\033[0m', # RESET COLOR
}

# Based on https://github.com/Mikubill/sd-webui-controlnet/blob/main/scripts/logging.py
class ColoredFormatter(logging.Formatter):
  def format(self, record):
    coloredRecord = copy.copy(record)
    levelName = coloredRecord.levelname
    seq = COLORS.get(levelName, COLORS['RESET'])
    coloredRecord.levelName = f'{seq}{levelName}{COLORS["RESET"]}'
    coloredRecord.msg = f'{seq}{coloredRecord.msg}{COLORS["RESET"]}'
    return super().format(coloredRecord)

logger = logging.getLogger(extensionTitle)
logger.propagate = False
if not logger.handlers:
  handler = logging.StreamHandler(sys.stdout)
  handler.setFormatter(ColoredFormatter('[%(levelName)s %(name)s] %(message)s'))
  logger.addHandler(handler)
logLevelString = getattr(shared.cmd_opts, f'{extensionId}_log_level', 'INFO')
logLevel = getattr(logging, logLevelString.upper(), None)
if logLevel is None:
  logger.setLevel(logging.INFO)
else:
  logger.setLevel(logLevel)
if os.getenv(f'AUTOMATIC1111_EXTENSION_{extensionId.upper()}_DEBUG', '0') == '1':
  logger.info('Activating debug logging because of environment variable')
  logger.setLevel(logging.DEBUG)
