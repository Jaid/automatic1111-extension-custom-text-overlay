import time

import gradio
from modules import scripts
from modules.processing import Processed, StableDiffusionProcessing
from modules.ui_components import InputAccordion

from lib.drawText import drawText
from lib.logger import logger
from lib.extension import extensionId, extensionTitle
from lib.align import Position

templateBracketLeft = '{{'
templateBracketRight = '}}'

normalFontSize = 32 # for 1024x1024 pixels or anything with the same megapixel value
normalPadding = 8 # for 1024x1024 pixels or anything with the same megapixel value
normalMargin = 0 # for 1024x1024 pixels or anything with the same megapixel value

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
    logger.debug(f'ui({is_img2img})')
    minWidth = 200
    with InputAccordion(False, label=extensionTitle, elem_id=self.elem_id(extensionId)) as enabled:
      with gradio.Accordion('Text'):
        with gradio.Row():
          with gradio.Column(min_width=minWidth):
            textTemplate1 = gradio.Textbox(label="Top left text", value='Time: {{time}}s', lines=1)
          with gradio.Column(min_width=minWidth):
            textTemplate2 = gradio.Textbox(label="Top center text", value='', lines=1)
          with gradio.Column(min_width=minWidth):
            textTemplate3 = gradio.Textbox(label="Top right text", value='', lines=1)
        with gradio.Row():
          with gradio.Column(min_width=minWidth):
            textTemplate4 = gradio.Textbox(label="Center left text", value='', lines=1)
          with gradio.Column(min_width=minWidth):
            textTemplate5 = gradio.Textbox(label="Center text", value='', lines=1)
          with gradio.Column(min_width=minWidth):
            textTemplate6 = gradio.Textbox(label="Center right text", value='', lines=1)
        with gradio.Row():
          with gradio.Column(min_width=minWidth):
            textTemplate7 = gradio.Textbox(label="Bottom left text", value='Seed {{seed}}', lines=1)
          with gradio.Column(min_width=minWidth):
            textTemplate8 = gradio.Textbox(label="Bottom center text", value='', lines=1)
          with gradio.Column(min_width=minWidth):
            textTemplate9 = gradio.Textbox(label="Bottom right text", value='', lines=1)
      with gradio.Accordion('Style'):
        gradio.HTML('<p><h2>General</h2><hr style="margin-top: 0; margin-bottom: 1em"/></p>')
        with gradio.Row():
          with gradio.Column(min_width=minWidth):
            textColor = gradio.ColorPicker(label='Text color', value='#ffffff')
            textScale = gradio.Slider(minimum=10, maximum=200, step=1, label='Text scale', value=120)
          with gradio.Column(min_width=minWidth):
            paddingScale = gradio.Slider(minimum=0, maximum=200, step=1, label='Padding scale', value=40)
            marginScale = gradio.Slider(minimum=0, maximum=200, step=1, label='Margin scale', value=0)
        gradio.HTML('<p style="margin-top: 2em"><h2>Outline</h2><hr style="margin-top: 0; margin-bottom: 1em"/></p>')
        with gradio.Row():
          outlineScale = gradio.Slider(minimum=0, maximum=25, step=1, label='Outline scale', value=10)
          outlineColor = gradio.ColorPicker(label='Outline color', value='#000000')
          outlineOpacity = gradio.Slider(minimum=0, maximum=255, step=1, label='Outline opacity', value=255)
        gradio.HTML('<p style="margin-top: 2em"><h2>Background Box</h2><hr style="margin-top: 0; margin-bottom: 1em"/></p>')
        with gradio.Row():
          backgroundColor = gradio.ColorPicker(label='Background color', value='#000000')
          backgroundOpacity = gradio.Slider(minimum=0, maximum=255, step=1, label='Background opacity', value=0)

    return [enabled, textScale, textColor, backgroundColor, backgroundOpacity, paddingScale, marginScale, outlineScale, outlineColor, outlineOpacity, textTemplate1, textTemplate2, textTemplate3, textTemplate4, textTemplate5, textTemplate6, textTemplate7, textTemplate8, textTemplate9]

  def process(self, processing: StableDiffusionProcessing, enabled: bool, textScale: int, textColor: str, backgroundColor: str, backgroundOpacity: int, paddingScale: int, marginScale: int, outlineScale: int, outlineColor: str, outlineOpacity: int, textTemplate1: str, textTemplate2: str, textTemplate3: str, textTemplate4: str, textTemplate5: str, textTemplate6: str, textTemplate7: str, textTemplate8: str, textTemplate9: str):
    if not enabled:
      return
    self.startTime = time.time()

        # self.images = images_list
        # self.prompt = p.prompt
        # self.negative_prompt = p.negative_prompt
        # self.seed = seed
        # self.subseed = subseed
        # self.subseed_strength = p.subseed_strength
        # self.info = info
        # self.comments = "".join(f"{comment}\n" for comment in p.comments)
        # self.width = p.width
        # self.height = p.height
        # self.sampler_name = p.sampler_name
        # self.cfg_scale = p.cfg_scale
        # self.image_cfg_scale = getattr(p, 'image_cfg_scale', None)
        # self.steps = p.steps
        # self.batch_size = p.batch_size
        # self.restore_faces = p.restore_faces
        # self.face_restoration_model = opts.face_restoration_model if p.restore_faces else None
        # self.sd_model_name = p.sd_model_name
        # self.sd_model_hash = p.sd_model_hash
        # self.sd_vae_name = p.sd_vae_name
        # self.sd_vae_hash = p.sd_vae_hash
        # self.seed_resize_from_w = p.seed_resize_from_w
        # self.seed_resize_from_h = p.seed_resize_from_h
        # self.denoising_strength = getattr(p, 'denoising_strength', None)
        # self.extra_generation_params = p.extra_generation_params
        # self.index_of_first_image = index_of_first_image
        # self.styles = p.styles
        # self.job_timestamp = state.job_timestamp
        # self.clip_skip = opts.CLIP_stop_at_last_layers
        # self.token_merging_ratio = p.token_merging_ratio
        # self.token_merging_ratio_hr = p.token_merging_ratio_hr

        # self.eta = p.eta
        # self.ddim_discretize = p.ddim_discretize
        # self.s_churn = p.s_churn
        # self.s_tmin = p.s_tmin
        # self.s_tmax = p.s_tmax
        # self.s_noise = p.s_noise
        # self.s_min_uncond = p.s_min_uncond
        # self.sampler_noise_scheduler_override = p.sampler_noise_scheduler_override
        # self.prompt = self.prompt if not isinstance(self.prompt, list) else self.prompt[0]
        # self.negative_prompt = self.negative_prompt if not isinstance(self.negative_prompt, list) else self.negative_prompt[0]
        # self.seed = int(self.seed if not isinstance(self.seed, list) else self.seed[0]) if self.seed is not None else -1
        # self.subseed = int(self.subseed if not isinstance(self.subseed, list) else self.subseed[0]) if self.subseed is not None else -1
        # self.is_using_inpainting_conditioning = p.is_using_inpainting_conditioning

        # self.all_prompts = all_prompts or p.all_prompts or [self.prompt]
        # self.all_negative_prompts = all_negative_prompts or p.all_negative_prompts or [self.negative_prompt]
        # self.all_seeds = all_seeds or p.all_seeds or [self.seed]
        # self.all_subseeds = all_subseeds or p.all_subseeds or [self.subseed]
        # self.infotexts = infotexts or [info] * len(images_list)
        # self.version = program_version()

  def postprocess_image(self, processing: StableDiffusionProcessing, processed, enabled: bool, textScale: int, textColor: str, backgroundColor: str, backgroundOpacity: int, paddingScale: int, marginScale: int, outlineScale: int, outlineColor: str, outlineOpacity: int, textTemplate1: str, textTemplate2: str, textTemplate3: str, textTemplate4: str, textTemplate5: str, textTemplate6: str, textTemplate7: str, textTemplate8: str, textTemplate9: str):
    if not enabled:
      return
    endTime = time.time()
    generationTimeSeconds = endTime - self.startTime
    keysFromImg = [
      'seed',
      'width',
      'height',
    ]
    # logger.debug(processed.images[0])
    processedImages = [processed.image]
    for i in range(len(processedImages)):
      for textTemplateIndex in range(1, 10):
        textTemplate = locals()[f'textTemplate{textTemplateIndex}']
        if not textTemplate:
          continue
        position = Position(textTemplateIndex)
        replacements = {
          'time.00': f'{generationTimeSeconds:.2f}',
          'time.0': f'{generationTimeSeconds:.1f}',
          'time': f'{generationTimeSeconds:.0f}',
          'processed_image_index': str(i),
        }
        img = processedImages[i]
        for key in keysFromImg:
          value = getattr(img, key, None)
          if value is not None:
            logger.debug(f'Found {key} in img: {value}')
            replacements[key] = str(value)
            continue
          backupValue = getattr(processed, key, None)
          if backupValue is not None:
            logger.debug(f'Found {key} in processed: {backupValue}')
            replacements[key] = str(backupValue)
            continue
          backupValue2 = getattr(processing, key, None)
          if backupValue2 is not None:
            logger.debug(f'Found {key} in processing: {backupValue2}')
            replacements[key] = str(backupValue2)
            continue
          replacements[key] = '?'
        text = textTemplate
        for key, value in replacements.items():
          text = text.replace(f'{templateBracketLeft}{key}{templateBracketRight}', value)
        pixels = img.width * img.height
        fontSize = int((textScale / 100) * (normalFontSize * (pixels / 1048576) ** 0.5))
        margin = int((marginScale / 100) * fontSize)
        padding = int((paddingScale / 100) * fontSize)
        outline = int((outlineScale / 100) * fontSize)
        logger.debug(f'fontSize: {fontSize}, margin: {margin}, padding: {padding}')
        img = drawText(img, text=text, fontSize=fontSize, textColor=textColor, position=position, backgroundColor=backgroundColor, backgroundOpacity=backgroundOpacity, margin=margin, padding=padding, outline=outline, outlineColor=outlineColor, outlineOpacity=outlineOpacity)
        # processed.images[i] = img
        processed.image = img

    logger.debug(f'Added text overlay: {text}')
