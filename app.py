from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import shutil
import os
import io

from src.pipeline.bg_prediction_pipeline import process_remove_bg, process_add_bg
from src.exceptions import CustomException

app = FastAPI()

# Mount static files directory for CSS, JS, images etc.
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates directory for HTML
templates = Jinja2Templates(directory="templates")


# Render the main HTML page
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Endpoint to remove background
@app.post("/remove-background/")
async def remove_background(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        temp_input_path = f"temp_{file.filename}"
        with open(temp_input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Call your processing function
        output_path = process_remove_bg(temp_input_path)

        # Read output file and send as response
        with open(output_path, "rb") as image_file:
            image_bytes = image_file.read()

        # Clean up temp input file
        os.remove(temp_input_path)

        return StreamingResponse(io.BytesIO(image_bytes), media_type="image/png")

    except CustomException as e:
        return {"error": str(e)}

    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


# Endpoint to add background
@app.post("/add-background/")
async def add_background(
    foreground: UploadFile = File(...),
    background: UploadFile = File(...)
):
    try:
        # Save uploaded foreground temporarily
        temp_foreground_path = f"temp_foreground_{foreground.filename}"
        with open(temp_foreground_path, "wb") as buffer:
            shutil.copyfileobj(foreground.file, buffer)

        # Save uploaded background temporarily
        temp_background_path = f"temp_background_{background.filename}"
        with open(temp_background_path, "wb") as buffer:
            shutil.copyfileobj(background.file, buffer)

        # Call your processing function
        output_path = process_add_bg(temp_foreground_path, temp_background_path)

        # Read output file and send as response
        with open(output_path, "rb") as image_file:
            image_bytes = image_file.read()

        # Cleanup temp files
        os.remove(temp_foreground_path)
        os.remove(temp_background_path)

        return StreamingResponse(io.BytesIO(image_bytes), media_type="image/png")

    except CustomException as e:
        return {"error": str(e)}

    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
