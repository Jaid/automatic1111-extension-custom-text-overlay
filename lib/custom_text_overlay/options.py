from lib.custom_text_overlay.logger import logger
from modules import shared
from src.custom_text_overlay.extension import extensionId, extensionTitle
from typing import Any
import gradio

defaults = {
  'template_engine': 'basic',
  'examples': True,
}

uiInfos = {
  'template_engine': {
    'label': 'Template engine to use for overlay texts',
    'component': gradio.Dropdown,
    'component_args': {
      'choices': ['basic', 'jinja2']
    }
  },
  'examples': {
    'label': 'Prefill template inbut fields with examples',
    'component': gradio.Checkbox
  }
}

def getOptionId(suffix: (str | None) = None) -> str:
  prefix = extensionId
  if suffix is not None:
    return f'{prefix}_{suffix}'
  return prefix

def getOption(optionId: str, defaultValue: Any = None) -> (Any):
  if optionId in defaults:
    defaultValue = defaults[optionId]
  fullOptionId = getOptionId(optionId)
  if not hasattr(shared.opts, fullOptionId):
    return defaultValue
  value = getattr(shared.opts, fullOptionId)
  return value

def onUiSettings():
  section = (extensionId, extensionTitle)
  for optionId, defaultValue in defaults.items():
    uiInfo: dict[str, Any] = {
      'default': defaultValue
    }
    if optionId in uiInfos:
      uiInfo = uiInfos[optionId]
    optionInfo = shared.OptionInfo(**uiInfo)
    optionInfo.section = section
    fullOptionId = getOptionId(optionId)
    shared.opts.add_option(fullOptionId, optionInfo)
