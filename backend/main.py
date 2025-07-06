from typing import Annotated
from fastapi import FastAPI, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from backend.sonolize import *
from backend.models import *
from backend.edit_functions import *
app = FastAPI()


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

app.mount("/static", StaticFiles(directory="./frontend/static"), name="static")
templates = Jinja2Templates(directory="./frontend/templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/', response_class=HTMLResponse)
async def edit(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get('/about', response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.post('/process-image/')
async def process_image(data: Annotated[ImageForm, Form()]):
    img_obj = initialize_image(data)
    chain1 = Chain()
    if data.delaycheckmark:
        chain1 += create_delay(data)
    if data.compcheckmark:
        chain1 += create_compressor(data)
    img_obj.scan = execute_chain(chain1,img_obj)
    img_obj.save()


    return FileResponse(path='./backend/testimages/test1.png', status_code=200)
