import logging
import os
import time

import gradio
from modules import script_callbacks, scripts, shared
from modules.processing import Processed, StableDiffusionProcessing
from modules.shared import opts

from lib.add_time_watermark import draw_text

extensionTitle = 'Text Overlay'
extensionId = 'text_overlay'

logger = logging.getLogger(extensionTitle)
logger.setLevel(logging.INFO)
if os.getenv('AUTOMATIC1111_EXTENSION_TEXT_OVERLAY_DEBUG', '0') == '1' or 1 == 1:
  logger.info('Activating debug logging')
  logger.setLevel(logging.DEBUG)
logger.debug(f'Loading {extensionTitle}')
logger.debug(f'Current cwd absolute path: {os.path.abspath(os.getcwd())}')

def getOptionId(suffix: (str | None) = None) -> str:
  prefix = extensionId
  if suffix is not None:
    return f'{prefix}_{suffix}'
  return prefix

class GenerationTimeWatermark(scripts.Script):
  def title(self):
    logger.debug(f'title()')
    logger.debug(f'Loading {extensionTitle}')
    logger.debug(f'Current cwd absolute path: {os.path.abspath(os.getcwd())}')
    return extensionTitle

  def show(self, is_img2img):
    logger.debug(f'show({is_img2img})')
    return scripts.AlwaysVisible

  def ui(self, is_img2img):
    logger.debug(f'ui({is_img2img})')
    with gradio.Group():
      with gradio.Row():
        enabled = gradio.Checkbox(label='Enable generation time watermark', value=opts.data.get(getOptionId('enabled'), True))
        font_size = gradio.Slider(minimum=10, maximum=50, step=1, label='Font size', value=opts.data.get(getOptionId('font_size'), 20))
      with gradio.Row():
        font_color = gradio.ColorPicker(label='Font color', value=opts.data.get(getOptionId('font_color'), '#ffffff'))
        position = gradio.Radio(choices=['top_left', 'top_right', 'bottom_left', 'bottom_right'], label='Watermark position', value=opts.data.get(getOptionId('position'), 'bottom_right'))

    return [enabled, font_size, font_color, position]

  def process(self, p: StableDiffusionProcessing, enabled, font_size, font_color, position):
    logger.debug(f'process({enabled}, {font_size}, {font_color}, {position})')
    self.enabled = enabled
    self.font_size = font_size
    self.font_color = font_color
    self.position = position

    if not self.enabled:
      return

    self.start_time = time.time()

  def postprocess(self, p: StableDiffusionProcessing, processed: Processed, enabled, font_size, font_color, position):
    if not self.enabled:
      return

    end_time = time.time()
    generation_time = end_time - self.start_time
    time_text = f'{generation_time:.2f}s'

    for i in range(len(processed.images)):
      img = processed.images[i]
      img = draw_text(img, time_text, self.font_size, self.font_color, self.position)
      processed.images[i] = img

    logger.info(f'Added generation time watermark: {time_text}')
