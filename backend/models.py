from typing import Literal, Annotated, Union

from fastapi import UploadFile
from pydantic import BaseModel, Field


# Effects =================================

class EffectForm(BaseModel):
    type: str
    samplerate: Annotated[int,  Field(gt=100, le=44100)] = 22050

class DelayForm(EffectForm):
    type: Literal['Delay'] = 'Delay'
    delaytimeknb: Annotated[float, Field(gt=0, le=10)] = 1
    delayvolumeknb: Annotated[float, Field(ge=-1, le=1)] = 0

class CompressorForm(EffectForm):
    type: Literal['Compressor'] = 'Compressor'
    compattimeknb: Annotated[float, Field(ge=0, le=10)] = 0.1
    compreltimeknb: Annotated[float, Field(ge=0, le=10)] = 0.5
    compthresknb:  Annotated[float, Field(ge=0, le=1)] = 0.5
    compratknb:  Annotated[float, Field(gt=0, le=10)] = 0.5

EffectUnion = Annotated[Union[DelayForm, CompressorForm], Field(discriminator='type')]
# Requests =================================

# Edit request model
class ImageForm(BaseModel):

    # Image
    image: UploadFile