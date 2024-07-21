import time

import gradio
from jinja2 import Template
from modules import script_callbacks, scripts
from modules.processing import Processed, StableDiffusionProcessing
from modules.ui_components import InputAccordion

from lib.custom_text_overlay.align import Position
from lib.custom_text_overlay.drawText import drawText
from lib.custom_text_overlay.logger import logger
from lib.custom_text_overlay.options import getOption, onUiSettings
from src.custom_text_overlay.extension import extensionId, extensionTitle

templateBracketLeft = '{{'
templateBracketRight = '}}'

normalFontSize = 32 # for 1024x1024 pixels or anything with the same megapixel value
hookType = 'postprocess_image'

keysFromImg = [
  'cfg_scale',
  'width',
  'height',
  'seed',
  'subseed',
  'prompt',
  'negative_prompt',
]

specialReplacements = {
  'all_seeds': 'seed',
  'all_subseeds': 'subseed',
  'all_prompts': 'prompt',
  'all_negative_prompts': 'negative_prompt',
}

class CustomTextOverlay(scripts.Script):
  def title(self):
    return extensionTitle

  def show(self, is_img2img):
    return scripts.AlwaysVisible

  def ui(self, is_img2img):
    minWidth = 200
    templateEngine = getOption('template_engine')
    timeTemplate = "{{ ('%.1f'|format(time)).rstrip('0').rstrip('.') }}s" if templateEngine == 'jinja2' else '{{time}}s'
    seedTemplate = 'Seed {{seed}}'
    with InputAccordion(False, label=extensionTitle, elem_id=self.elem_id(extensionId)) as enabled:
      with gradio.Accordion('Text', open=True):
        with gradio.Row():
          with gradio.Column(min_width=minWidth):
            textEnabled1 = gradio.Checkbox(label='Top left text', value=True)
            textTemplate1 = gradio.Textbox(label='Top left text template', value=timeTemplate, lines=1, show_label=False)
          with gradio.Column(min_width=minWidth):
            textEnabled2 = gradio.Checkbox(label='Top center text', value=True)
            textTemplate2 = gradio.Textbox(label='Top center text template', value='', lines=1, show_label=False)
          with gradio.Column(min_width=minWidth):
            textEnabled3 = gradio.Checkbox(label='Top right text', value=True)
            textTemplate3 = gradio.Textbox(label='Top right text template', value='', lines=1, show_label=False)
        with gradio.Row():
          with gradio.Column(min_width=minWidth):
            textEnabled4 = gradio.Checkbox(label='Center left text', value=True)
            textTemplate4 = gradio.Textbox(label='Center left text template', value='', lines=1, show_label=False)
          with gradio.Column(min_width=minWidth):
            textEnabled5 = gradio.Checkbox(label='Center text', value=True)
            textTemplate5 = gradio.Textbox(label='Center text template', value='', lines=1, show_label=False)
          with gradio.Column(min_width=minWidth):
            textEnabled6 = gradio.Checkbox(label='Center right text', value=True)
            textTemplate6 = gradio.Textbox(label='Center right text template', value='', lines=1, show_label=False)
        with gradio.Row():
          with gradio.Column(min_width=minWidth):
            textEnabled7 = gradio.Checkbox(label='Bottom left text', value=True)
            textTemplate7 = gradio.Textbox(label='Bottom left text template', value=seedTemplate, lines=1, show_label=False)
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
            textScale = gradio.Slider(minimum=20, maximum=300, step=10, label='Text scale', value=120)
          with gradio.Column(min_width=minWidth):
            paddingScale = gradio.Slider(minimum=0, maximum=200, step=5, label='Padding scale', value=25)
            marginScale = gradio.Slider(minimum=0, maximum=200, step=5, label='Margin scale', value=0)
        gradio.HTML('<p style="margin-top: 2em"><h2>Outline</h2><hr style="margin-top: 0; margin-bottom: 1em"/></p>')
        with gradio.Row():
          outlineScale = gradio.Slider(minimum=0, maximum=25, step=1, label='Outline scale', value=12)
          outlineColor = gradio.ColorPicker(label='Outline color', value='#000000')
          outlineOpacity = gradio.Slider(minimum=0, maximum=100, step=5, label='Outline opacity', value=100)
        gradio.HTML('<p style="margin-top: 2em"><h2>Background Box</h2><hr style="margin-top: 0; margin-bottom: 1em"/></p>')
        with gradio.Row():
          backgroundColor = gradio.ColorPicker(label='Background color', value='#000000')
          backgroundOpacity = gradio.Slider(minimum=0, maximum=100, step=5, label='Background opacity', value=0)

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

  def collectReplacements(self, staticReplacements: dict = {}, replacementSources: dict = {}, imageIndex: int = 0, timeSeconds: float = 0):
    tempateEngine = getOption('template_engine')
    logger.info(tempateEngine)
    replacements = self.makeReplacementTable(staticReplacements, keysFromImg, replacementSources)
    if timeSeconds is not None:
      if tempateEngine == 'jinja2':
        replacements['time'] = timeSeconds
      else:
        replacements['time.00'] = f'{timeSeconds:.2f}'
        replacements['time.0'] = f'{timeSeconds:.1f}'
        replacements['time'] = int(timeSeconds)
    if imageIndex is not None:
      replacements['image_index'] = imageIndex
    if tempateEngine == 'jinja2':
      for sourceName, source in replacementSources.items():
        replacements[sourceName] = source
    for arrayKey, singleKey in specialReplacements.items():
      for replacementSource in replacementSources.values():
        if hasattr(replacementSource, arrayKey):
          value = getattr(replacementSource, arrayKey)
          if value is not None:
            if imageIndex < len(value):
              replacements[singleKey] = str(value[imageIndex])
              break
    return replacements

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

  def applyReplacements(self, templateString: str, replacements: dict):
    templateEngine = getOption('template_engine')
    templateHandler = self.applyReplacementsJinja if templateEngine == 'jinja2' else self.applyReplacementsBasic
    inputTemplate = templateString.strip()
    output = templateHandler(inputTemplate, replacements)
    if inputTemplate == output:
      return inputTemplate
    logger.debug(f'Resolving template “{inputTemplate}” to “{output}” with engine {templateEngine} and keys {", ".join(replacements.keys())}')
    return output

  def applyReplacementsJinja(self, templateString: str, replacements: dict):
    jinjaTemplate = Template(templateString)
    return jinjaTemplate.render(replacements)

  def applyReplacementsBasic(self, templateString: str, replacements: dict):
    for key, value in replacements.items():
      if isinstance(value, int) or isinstance(value, float):
        value = str(value)
      if not isinstance(value, str):
        continue
      templateString = templateString.replace(f'{templateBracketLeft}{key}{templateBracketRight}', value)
    return templateString

  def postprocess_image(self, processing: StableDiffusionProcessing, processed, enabled: bool, textScale: int, textColor: str, backgroundColor: str, backgroundOpacity: int, paddingScale: int, marginScale: int, outlineScale: int, outlineColor: str, outlineOpacity: int, textEnabled1: bool, textEnabled2: bool, textEnabled3: bool, textEnabled4: bool, textEnabled5: bool, textEnabled6: bool, textEnabled7: bool, textEnabled8: bool, textEnabled9: bool, textTemplate1: str, textTemplate2: str, textTemplate3: str, textTemplate4: str, textTemplate5: str, textTemplate6: str, textTemplate7: str, textTemplate8: str, textTemplate9: str):
    if not enabled or hookType != 'postprocess_image':
      return
    enabledTextTemplates: list[int] = []
    for textTemplateIndex in range(1, 10):
      if locals()[f'textEnabled{textTemplateIndex}'] and locals()[f'textTemplate{textTemplateIndex}'].strip() != '':
        enabledTextTemplates.append(textTemplateIndex)
    if len(enabledTextTemplates) == 0:
      return
    endTime = time.perf_counter()
    generationTimeSeconds = endTime - self.startTime
    self.startTime = endTime
    furtherReplacementsSources = {
      'img': processed.image,
      'processed': processed,
      'processing': processing,
    }
    replacements = self.collectReplacements(timeSeconds=generationTimeSeconds, replacementSources=furtherReplacementsSources, imageIndex=processing.iteration)

    for textTemplateIndex in enabledTextTemplates:
      textTemplate = locals()[f'textTemplate{textTemplateIndex}'].strip()
      text = self.applyReplacements(textTemplate, replacements)
      position = Position(textTemplateIndex)
      pixels = processed.image.width * processed.image.height
      fontSize = int((textScale / 100) * (normalFontSize * (pixels / 1048576)))
      margin = int((marginScale / 100) * fontSize)
      padding = int((paddingScale / 100) * fontSize)
      outline = int((outlineScale / 100) * fontSize)
      processed.image = drawText(processed.image, text=text, fontSize=fontSize, textColor=textColor, position=position, backgroundColor=backgroundColor, backgroundOpacity=backgroundOpacity, margin=margin, padding=padding, outline=outline, outlineColor=outlineColor, outlineOpacity=outlineOpacity)

  def postprocess(
    self, processing: StableDiffusionProcessing, processed: Processed, enabled: bool, textScale: int, textColor: str, backgroundColor: str, backgroundOpacity: int, paddingScale: int, marginScale: int, outlineScale: int, outlineColor: str, outlineOpacity: int, textEnabled1: bool, textEnabled2: bool,
    textEnabled3: bool, textEnabled4: bool, textEnabled5: bool, textEnabled6: bool, textEnabled7: bool, textEnabled8: bool, textEnabled9: bool, textTemplate1: str, textTemplate2: str, textTemplate3: str, textTemplate4: str, textTemplate5: str, textTemplate6: str, textTemplate7: str,
    textTemplate8: str, textTemplate9: str
  ):
    if not enabled or hookType != 'postprocess':
      return
    enabledTextTemplates: list[int] = []
    for textTemplateIndex in range(1, 10):
      if locals()[f'textEnabled{textTemplateIndex}'] and locals()[f'textTemplate{textTemplateIndex}'].strip() != '':
        enabledTextTemplates.append(textTemplateIndex)
    if len(enabledTextTemplates) == 0:
      return
    endTime = time.perf_counter()
    generationTimeSeconds = endTime - self.startTime

    images = processed.images[processed.index_of_first_image:]
    for imageIndex in range(len(images)):
      processedImageIndex = imageIndex + processed.index_of_first_image
      img = images[imageIndex]
      replacements = {
        'processed_image_index': processedImageIndex,
        'real_image_index': imageIndex,
      }
      furtherReplacementsSources = {
        'img': img,
        'processed': processed,
        'processing': processing,
      }
      replacements = self.collectReplacements(staticReplacements=replacements, replacementSources=furtherReplacementsSources, imageIndex=imageIndex, timeSeconds=generationTimeSeconds)

      for textTemplateIndex in enabledTextTemplates:
        textTemplate = locals()[f'textTemplate{textTemplateIndex}'].strip()
        text = self.applyReplacements(textTemplate, replacements)
        position = Position(textTemplateIndex)
        pixels = img.width * img.height
        fontSize = int((textScale / 100) * (normalFontSize * (pixels / 1048576)))
        margin = int((marginScale / 100) * fontSize)
        padding = int((paddingScale / 100) * fontSize)
        outline = int((outlineScale / 100) * fontSize)
        img = drawText(img, text=text, fontSize=fontSize, textColor=textColor, position=position, backgroundColor=backgroundColor, backgroundOpacity=backgroundOpacity, margin=margin, padding=padding, outline=outline, outlineColor=outlineColor, outlineOpacity=outlineOpacity)
        processed.images[processedImageIndex] = img

script_callbacks.on_ui_settings(onUiSettings)
