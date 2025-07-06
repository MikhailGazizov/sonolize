from fastapi import UploadFile
from pydantic import BaseModel

# Effects =================================

class EffectForm(BaseModel):
    samplerate: int = 100

class DelayForm(EffectForm):
    delaytimeknb: float = 1
    delayvolumeknb: float = 0.5

class CompressorForm(EffectForm):
    compattimeknb: float = 0.1
    compreltimeknb: float = 0.5
    compthresknb: float = 0.5
    compratknb: float = 0.5


# Requests =================================

# Edit request model
class ImageForm(DelayForm, CompressorForm):

    # Delay
    delaycheckmark: bool = False

    # Compressor
    compcheckmark: bool = False

    # Image
    image: UploadFile