from distutils.util import execute

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

# Pedalboard / Chain management ================

def execute_chain(chain: Chain, image: Sonolize):
    return chain(image.scan)

# Image management =============================

def initialize_image(data: ImageForm):
    image = Sonolize(
        data.image.file,
        ScanType.HORIZONTAL,
        lock_alpha=True
    )
    image.get_pixels()
    image.scan_image()

    return image
