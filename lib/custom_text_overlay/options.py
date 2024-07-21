from lib.custom_text_overlay.logger import logger
from modules import shared
from src.custom_text_overlay.extension import extensionId, extensionTitle
from typing import Any
import gradio

templateEngines = ['basic', 'jinja2']

defaults = {
  'template_engine': templateEngines[0],
  'examples': True,
}

uiInfos = {
  'template_engine': {
    'label': 'Template engine to use for overlay texts',
    'component': gradio.Dropdown,
    'component_args': {
      'choices': templateEngines
    }
  },
  'examples': {
    'label': 'Prefill template input fields with examples',
    'comment_after': '<div>Alternatively, you can apply your current UI state to change the default values of the input fields.</div>',
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
      uiInfo.update(uiInfos[optionId])
    optionInfo = shared.OptionInfo(**uiInfo)
    optionInfo.section = section
    fullOptionId = getOptionId(optionId)
    shared.opts.add_option(fullOptionId, optionInfo)
