import time

import gradio
from modules import scripts
from modules.processing import Processed, StableDiffusionProcessing
from modules.ui_components import InputAccordion

from lib.drawText import drawText
from lib.logger import logger
from lib.extension import extensionId, extensionTitle
from lib.align import Position

import pprint

debugLog = ''

templateBracketLeft = '{{'
templateBracketRight = '}}'

normalFontSize = 32 # for 1024x1024 pixels or anything with the same megapixel value

def getOptionId(suffix: (str | None) = None) -> str:
  prefix = extensionId
  if suffix is not None:
    return f'{prefix}_{suffix}'
  return prefix

class TextOverlayScript(scripts.Script):
  def title(self):
    return extensionTitle

  def show(self, is_img2img):
    return scripts.AlwaysVisible

  def ui(self, is_img2img):
    minWidth = 200
    with InputAccordion(False, label=extensionTitle, elem_id=self.elem_id(extensionId)) as enabled:
      with gradio.Accordion('Text'):
        with gradio.Row():
          with gradio.Column(min_width=minWidth):
            textEnabled1 = gradio.Checkbox(label='Top left text', value=True)
            textTemplate1 = gradio.Textbox(label='Top left text template', value='Time: {{time}}s', lines=1, show_label=False)
          with gradio.Column(min_width=minWidth):
            textEnabled2 = gradio.Checkbox(label='Top center text', value=True)
            textTemplate2 = gradio.Textbox(label='Top center text template', value='', lines=1)
          with gradio.Column(min_width=minWidth):
            textEnabled3 = gradio.Checkbox(label='Top right text', value=True)
            textTemplate3 = gradio.Textbox(label='Top right text template', value='', lines=1, show_label=False)
        with gradio.Row():
          with gradio.Column(min_width=minWidth):
            textEnabled4 = gradio.Checkbox(label='Center left text', value=True)
            textTemplate4 = gradio.Textbox(label='Center left text template', value='', lines=1, show_label=False)
          with gradio.Column(min_width=minWidth):
            textEnabled5 = gradio.Checkbox(label='Center text', value=True)
            textTemplate5 = gradio.Textbox(label='Center text template', value='Prompt: {{prompt}}', lines=1, show_label=False)
          with gradio.Column(min_width=minWidth):
            textEnabled6 = gradio.Checkbox(label='Center right text', value=True)
            textTemplate6 = gradio.Textbox(label='Center right text template', value='', lines=1, show_label=False)
        with gradio.Row():
          with gradio.Column(min_width=minWidth):
            textEnabled7 = gradio.Checkbox(label='Bottom left text', value=True)
            textTemplate7 = gradio.Textbox(label='Bottom left text template', value='Seed {{seed}}', lines=1, show_label=False)
          with gradio.Column(min_width=minWidth):
            textEnabled8 = gradio.Checkbox(label='Bottom center text', value=True)
            textTemplate8 = gradio.Textbox(label='Bottom center text template', value='', lines=1, show_label=False)
          with gradio.Column(min_width=minWidth):
            textEnabled9 = gradio.Checkbox(label='Bottom right text', value=True)
            textTemplate9 = gradio.Textbox(label='Bottom right text template', value='', lines=1, show_label=False)
      with gradio.Accordion('Style'):
        gradio.HTML('<p><h2>General</h2><hr style="margin-top: 0; margin-bottom: 1em"/></p>')
        with gradio.Row():
          with gradio.Column(min_width=minWidth):
            textColor = gradio.ColorPicker(label='Text color', value='#ffffff')
            textScale = gradio.Slider(minimum=10, maximum=300, step=10, label='Text scale', value=120)
          with gradio.Column(min_width=minWidth):
            paddingScale = gradio.Slider(minimum=0, maximum=200, step=1, label='Padding scale', value=40)
            marginScale = gradio.Slider(minimum=0, maximum=200, step=1, label='Margin scale', value=0)
        gradio.HTML('<p style="margin-top: 2em"><h2>Outline</h2><hr style="margin-top: 0; margin-bottom: 1em"/></p>')
        with gradio.Row():
          outlineScale = gradio.Slider(minimum=0, maximum=25, step=1, label='Outline scale', value=8)
          outlineColor = gradio.ColorPicker(label='Outline color', value='#000000')
          outlineOpacity = gradio.Slider(minimum=0, maximum=100, step=1, label='Outline opacity', value=100)
        gradio.HTML('<p style="margin-top: 2em"><h2>Background Box</h2><hr style="margin-top: 0; margin-bottom: 1em"/></p>')
        with gradio.Row():
          backgroundColor = gradio.ColorPicker(label='Background color', value='#000000')
          backgroundOpacity = gradio.Slider(minimum=0, maximum=100, step=1, label='Background opacity', value=0)

    return [
      enabled, textScale, textColor, backgroundColor, backgroundOpacity, paddingScale, marginScale, outlineScale, outlineColor, outlineOpacity, textEnabled1, textEnabled2, textEnabled3, textEnabled4, textEnabled5, textEnabled6, textEnabled7, textEnabled8, textEnabled9, textTemplate1, textTemplate2,
      textTemplate3, textTemplate4, textTemplate5, textTemplate6, textTemplate7, textTemplate8, textTemplate9
    ]

  def process(
    self, processing: StableDiffusionProcessing, enabled: bool, textScale: int, textColor: str, backgroundColor: str, backgroundOpacity: int, paddingScale: int, marginScale: int, outlineScale: int, outlineColor: str, outlineOpacity: int, textEnabled1: bool, textEnabled2: bool, textEnabled3: bool,
    textEnabled4: bool, textEnabled5: bool, textEnabled6: bool, textEnabled7: bool, textEnabled8: bool, textEnabled9: bool, textTemplate1: str, textTemplate2: str, textTemplate3: str, textTemplate4: str, textTemplate5: str, textTemplate6: str, textTemplate7: str, textTemplate8: str,
    textTemplate9: str
  ):
    if not enabled:
      return
    self.startTime = time.perf_counter()

  def postprocess(
    self, processing: StableDiffusionProcessing, processed: Processed, enabled: bool, textScale: int, textColor: str, backgroundColor: str, backgroundOpacity: int, paddingScale: int, marginScale: int, outlineScale: int, outlineColor: str, outlineOpacity: int, textEnabled1: bool, textEnabled2: bool,
    textEnabled3: bool, textEnabled4: bool, textEnabled5: bool, textEnabled6: bool, textEnabled7: bool, textEnabled8: bool, textEnabled9: bool, textTemplate1: str, textTemplate2: str, textTemplate3: str, textTemplate4: str, textTemplate5: str, textTemplate6: str, textTemplate7: str,
    textTemplate8: str, textTemplate9: str
  ):
    if not enabled:
      return
    enabledTextTemplates: list[int] = []
    for textTemplateIndex in range(1, 10):
      if locals()[f'textEnabled{textTemplateIndex}'] and locals()[f'textTemplate{textTemplateIndex}'].strip() != '':
        enabledTextTemplates.append(textTemplateIndex)
    if len(enabledTextTemplates) == 0:
      return
    endTime = time.perf_counter()
    generationTimeSeconds = endTime - self.startTime
    keysFromImg = [
      'cfg_scale',
      'width',
      'height',
      'seed',
      'subseed',
      'prompt',
      'negative_prompt',
    ]

    log = pprint.pformat(vars(processed), indent=2, depth=4, width=300)
    logger.debug(f'Processed: {log}')

    logger.debug(f'Processing {len(processed.images)} images')
    images = processed.images[processed.index_of_first_image:]
    for imageIndex in range(len(images)):
      processedImageIndex = imageIndex + processed.index_of_first_image
      img = images[imageIndex]
      replacements = {
        'time.00': f'{generationTimeSeconds:.2f}',
        'time.0': f'{generationTimeSeconds:.1f}',
        'time': f'{generationTimeSeconds:.0f}',
        'processed_image_index': processedImageIndex,
        'real_image_index': imageIndex,
      }
      furtherReplacementsSources = {
        'img': img,
        'processed': processed,
        'processing': processing,
      }
      replacements = self.makeReplacementTable(replacements, keysFromImg, furtherReplacementsSources)
      specialReplacements = {
        'all_seeds': 'seed',
        'all_subseeds': 'subseed',
        'all_prompts': 'prompt',
        'all_negative_prompts': 'negative_prompt',
      }
      for key, value in specialReplacements.items():
        if getattr(processed, key) is not None:
          if imageIndex < len(getattr(processed, key)):
            replacements[value] = str(getattr(processed, key)[imageIndex])

      for textTemplateIndex in enabledTextTemplates:
        textTemplate = locals()[f'textTemplate{textTemplateIndex}'].strip()
        position = Position(textTemplateIndex)
        text = textTemplate
        for key, value in replacements.items():
          text = text.replace(f'{templateBracketLeft}{key}{templateBracketRight}', str(value))
        pixels = img.width * img.height
        fontSize = int((textScale / 100) * (normalFontSize * (pixels / 1048576)))
        margin = int((marginScale / 100) * fontSize)
        padding = int((paddingScale / 100) * fontSize)
        outline = int((outlineScale / 100) * fontSize)
        img = drawText(img, text=text, fontSize=fontSize, textColor=textColor, position=position, backgroundColor=backgroundColor, backgroundOpacity=backgroundOpacity, margin=margin, padding=padding, outline=outline, outlineColor=outlineColor, outlineOpacity=outlineOpacity)
        processed.images[processedImageIndex] = img

  def makeReplacementTable(self, baseReplacements: dict, needles: list, haystacks: dict):
    replacements = baseReplacements.copy()
    for needle in needles:
      for hackstackName, hackstack in haystacks.items():
        value = getattr(hackstack, needle, None)
        if value is not None:
          logger.debug(f'{templateBracketLeft}{needle}{templateBracketRight} = {hackstackName}.{needle}')
          replacements[needle] = value
          break
      else:
        logger.debug(f'{templateBracketLeft}{needle}{templateBracketRight} = ?')
        replacements[needle] = '?'
    return replacements
