from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from PIL import Image
from typing import Annotated, Optional
from io import BytesIO
from pydantic import BaseModel
from backend.sonolize import Sonolize, ScanType, Delay, Compressor, Chain

app = FastAPI()

class ImageForm(BaseModel):
    image: str
    image: str

"""
origins = [
    "http://localhost/",
    "http://localhost:8080",
    "http://localhost:8000/",
    "http://127.0.0.1",
    "http://127.0.0.1:8000/process-image/",
    "file:///C:/Users/Mike/PycharmProjects/sonolize/index.html",
    '192.168.1.75'
]"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/process-image/')
async def process_image(
                        delaycheckmark: bool = Form(default=False),
                        delaytimeknb: float = Form(...),
                        delayvolumeknb: float = Form(...),
                        compcheckmark: bool = Form(default=False),
                        compattimeknb: float = Form(...),
                        compreltimeknb: float = Form(...),
                        compthresknb: float = Form(...),
                        compratknb: float = Form(...),
                        image: UploadFile = File(...)):

    img_obj = Sonolize(image.file, ScanType.HORIZONTAL, lock_alpha = True)
    if delaycheckmark == True:
        chain1 = Chain([Delay(delaytimeknb, delayvolumeknb)])
        img_obj.scan = chain1(img_obj.scan)
        img_obj.pixels = img_obj._unscan_image()
    if compcheckmark == True:
        chain1 = Chain([Compressor(compattimeknb, compreltimeknb, compthresknb, compratknb)])
        img_obj.scan = chain1(img_obj.scan)
        img_obj.pixels = img_obj._unscan_image()
    img_obj._save()

    return FileResponse(path='backend/testimages/test1.png', status_code=200)
