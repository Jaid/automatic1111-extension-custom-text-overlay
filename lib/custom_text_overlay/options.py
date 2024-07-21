from lib.custom_text_overlay.logger import logger
from modules import shared
from src.custom_text_overlay.extension import extensionId, extensionTitle
from typing import Any
import gradio

optionDefinitions = {
  'template_engine': shared.OptionInfo('jinja2', 'Template engine to use for overlay texts', component=gradio.Dropdown, component_args={'choices': ['jinja2', 'basic']})
}

def getOptionId(suffix: (str | None) = None) -> str:
  prefix = extensionId
  if suffix is not None:
    return f'{prefix}_{suffix}'
  return prefix

def getOption(optionId: str, defaultValue: Any) -> (Any):
  fullOptionId = getOptionId(optionId)
  if not hasattr(shared.opts, fullOptionId):
    return defaultValue
  value = getattr(shared.opts, fullOptionId, defaultValue)
  return value

def onUiSettings():
  section = (extensionId, extensionTitle)
  for optionId, optionInfo in optionDefinitions.items():
    optionInfo.section = section
    fullOptionId = getOptionId(optionId)
    shared.opts.add_option(fullOptionId, optionInfo)
