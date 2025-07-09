from distutils.util import execute
from typing import List

from pydantic.tools import parse_obj_as

import json

from backend.sonolize import *
from backend.models import *

# Effect management ============================

def create_delay(data: DelayForm):
    return Delay(
        delay_time= data.delaytimeknb,
        volume= data.delayvolumeknb,
        sample_rate= data.samplerate
    )

def create_compressor(data: CompressorForm):
    return Compressor(
        attack_time= data.compattimeknb,
        release_time= data.compreltimeknb,
        threshold= data.compthresknb,
        ratio= data.compratknb,
        sample_rate= data.samplerate
    )

def parse_json_effects(effects_json: str):
    effects_raw = json.loads(effects_json)
    return parse_obj_as(List[EffectUnion], effects_raw)

model_to_effect = {
    DelayForm: create_delay,
    CompressorForm: create_compressor
}

def create_effects_chain_from_form_list(effects: List[EffectUnion]):
    chain = Chain()
    for effect in effects:
        chain + model_to_effect[effect.__class__](effect)
    return chain

# Pedalboard / Chain management ================

def execute_chain(chain: Chain, image: Sonolize):
    image.get_pixels()
    image.scan_image()
    image.scan = chain(image.scan)
    return image.scan

# Image management =============================

def initialize_image(data):
    image = Sonolize(
        data.file,
        ScanType.HORIZONTAL,
        lock_alpha=True
    )
    image.get_pixels()
    image.scan_image()

    return image
