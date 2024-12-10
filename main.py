from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from PIL import Image
from io import BytesIO
from pydantic import BaseModel
from sonolize import Sonolize, ScanType, Delay, Chain

app = FastAPI()

class ImageForm(BaseModel):
    image: str
    image: str

origins = [
    "http://localhost/",
    "http://localhost:8080",
    "http://localhost:8000/",
    "http://127.0.0.1",
    "http://127.0.0.1:8000/process-image/",
    "file:///C:/Users/Mike/PycharmProjects/sonolize/index.html",
    '192.168.1.75'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post('/process-image/')
async def process_image(image: UploadFile = File(...), ):

    print(image[0])
    """lol = Sonolize(image, scan_type=ScanType.VERTICAL, lock_alpha=False)
    print(lol.pixels[0])
    d1 = Chain([Delay(1, 0.2, 10)])
    lol.scan = d1(lol.scan)

    lol.pixels = lol._unscan_image()
    lol._save()"""
    return FileResponse(path='test1.png', status_code=200)
