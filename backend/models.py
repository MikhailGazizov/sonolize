from typing import Literal, Annotated, Union

from fastapi import UploadFile
from pydantic import BaseModel, Field


# Effects =================================

class EffectForm(BaseModel):
    type: str
    samplerate: int = 100

class DelayForm(EffectForm):
    type: Literal['Delay'] = 'Delay'
    delaytimeknb: float = 1
    delayvolumeknb: float = 0.5

class CompressorForm(EffectForm):
    type: Literal['Compressor'] = 'Compressor'
    compattimeknb: float = 0.1
    compreltimeknb: float = 0.5
    compthresknb: float = 0.5
    compratknb: float = 0.5

EffectUnion = Annotated[Union[DelayForm, CompressorForm], Field(discriminator='type')]
# Requests =================================

# Edit request model
class ImageForm(BaseModel):

    # Image
    image: UploadFile