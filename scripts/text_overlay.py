import logging
import os
import time

import gradio
from modules import script_callbacks, scripts, shared
from modules.processing import Processed, StableDiffusionProcessing
from modules.shared import opts

from lib.add_time_watermark import Position, draw_text

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

class TextOverlayScript(scripts.Script):
  def title(self):
    logger.debug(f'title()')
    logger.debug(f'Current cwd absolute path: {os.path.abspath(os.getcwd())}')
    return extensionTitle

  def show(self, is_img2img):
    logger.debug(f'show({is_img2img})')
    return scripts.AlwaysVisible

  def ui(self, is_img2img):
    logger.debug(f'ui({is_img2img})')
    with gradio.Group():
      with gradio.Row():
        enabled = gradio.Checkbox(label='Enable text overlay', value=opts.data.get(getOptionId('enabled'), True))
        font_size = gradio.Slider(minimum=10, maximum=50, step=1, label='Font size', value=opts.data.get(getOptionId('font_size'), 20))
      with gradio.Row():
        font_color = gradio.ColorPicker(label='Font color', value=opts.data.get(getOptionId('font_color'), '#ffffff'))
        position = gradio.Dropdown(choices=[p.name for p in Position], label='Text position', value=opts.data.get(getOptionId('position'), Position.BOTTOM_RIGHT.name))
      with gradio.Row():
        text_input = gradio.Textbox(label="Overlay Text", value=opts.data.get(getOptionId('text'), "Generation Time: {time}"))

    return [enabled, font_size, font_color, position, text_input]

  def process(self, processing: StableDiffusionProcessing, enabled, font_size, font_color, position, text_input):
    logger.debug(f'process({enabled}, {font_size}, {font_color}, {position}, {text_input})')
    self.enabled = enabled
    # if font_size is 100 for a 1048576 pixels image, final calculated font_size will be 32
    # scale accordingly
    self.font_size = font_size
    self.font_color = font_color
    self.position = Position[position]
    self.text_input = text_input
    if not self.enabled:
      return

    self.start_time = time.time()

  def postprocess(self, processing: StableDiffusionProcessing, processed: Processed, enabled, font_size, font_color, position, text_input):
    if not self.enabled:
      return

    end_time = time.time()
    generation_time = end_time - self.start_time
    time_text = f'{generation_time:.2f}s'

    overlay_text = self.text_input.replace("{time}", time_text)

    for i in range(len(processed.images)):
      img = processed.images[i]
      img = draw_text(img, overlay_text, self.font_size, self.font_color, self.position)
      processed.images[i] = img

    logger.info(f'Added text overlay: {overlay_text}')

# Add this to save the settings
def on_ui_settings():
  section = ('text_overlay', "Text Overlay")
  shared.opts.add_option("text_overlay_enabled", shared.OptionInfo(True, "Enable text overlay by default", section=section))
  shared.opts.add_option("text_overlay_font_size", shared.OptionInfo(20, "Default font size", section=section))
  shared.opts.add_option("text_overlay_font_color", shared.OptionInfo("#ffffff", "Default font color", section=section))
  shared.opts.add_option("text_overlay_position", shared.OptionInfo("BOTTOM_RIGHT", "Default text position", section=section))
  shared.opts.add_option("text_overlay_text", shared.OptionInfo("Generation Time: {time}", "Default overlay text", section=section))

script_callbacks.on_ui_settings(on_ui_settings)
