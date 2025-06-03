from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

import shutil
import os
import io

from src.pipeline.bg_prediction_pipeline import process_remove_bg, process_add_bg, process_inpaint
from src.exceptions import CustomException

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local dev or frontend access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static and template directories
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/remove-background/")
async def remove_background(file: UploadFile = File(...)):
    try:
        temp_input_path = f"temp_{file.filename}"
        with open(temp_input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        output_path = process_remove_bg(temp_input_path)

        with open(output_path, "rb") as image_file:
            image_bytes = image_file.read()

        os.remove(temp_input_path)
        return StreamingResponse(io.BytesIO(image_bytes), media_type="image/png")

    except CustomException as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@app.post("/add-background/")
async def add_background(
    foreground: UploadFile = File(...),
    background: UploadFile = File(...)
):
    try:
        temp_foreground_path = f"temp_foreground_{foreground.filename}"
        with open(temp_foreground_path, "wb") as buffer:
            shutil.copyfileobj(foreground.file, buffer)

        temp_background_path = f"temp_background_{background.filename}"
        with open(temp_background_path, "wb") as buffer:
            shutil.copyfileobj(background.file, buffer)

        output_path = process_add_bg(temp_foreground_path, temp_background_path)

        with open(output_path, "rb") as image_file:
            image_bytes = image_file.read()

        os.remove(temp_foreground_path)
        os.remove(temp_background_path)

        return StreamingResponse(io.BytesIO(image_bytes), media_type="image/png")

    except CustomException as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@app.post("/inpaint/")
async def inpaint_image(
    input_image: UploadFile = File(...),
    mask_image: UploadFile = File(...)
):
    try:
        temp_input_path = f"temp_input_{input_image.filename}"
        with open(temp_input_path, "wb") as buffer:
            shutil.copyfileobj(input_image.file, buffer)

        temp_mask_path = f"temp_mask_{mask_image.filename}"
        with open(temp_mask_path, "wb") as buffer:
            shutil.copyfileobj(mask_image.file, buffer)

        output_path = process_inpaint(mask_img_path=temp_mask_path, input_img_path=temp_input_path)

        with open(output_path, "rb") as image_file:
            image_bytes = image_file.read()

        os.remove(temp_input_path)
        os.remove(temp_mask_path)

        return StreamingResponse(io.BytesIO(image_bytes), media_type="image/png")

    except CustomException as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
