from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sonolize import Sonolize, ScanType, Delay, Compressor, Chain

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
    chain1 = Chain()
    #if delaycheckmark:
    #    chain1 += Delay(delaytimeknb,
    #                    delayvolumeknb)
    #if compcheckmark:
    #    chain1 += Compressor(compattimeknb,
    #                         compreltimeknb,
    #                         compthresknb,
    #                         compratknb)
    img_obj.set_scan(
        chain1(img_obj.get_scan())
    )
    img_obj._save()

    return FileResponse(path='testimages/test1.png', status_code=200)
