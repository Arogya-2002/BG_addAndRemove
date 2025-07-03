from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from contextlib import asynccontextmanager
import asyncio
import shutil
import os
import io
import uuid
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Optional

from src.pipeline.bg_prediction_pipeline import process_remove_bg, process_add_bg
from src.exceptions import CustomException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global executors for parallel processing
process_executor = None
thread_executor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown"""
    global process_executor, thread_executor
    
    # Startup - Initialize thread pools
    max_workers = min(4, os.cpu_count() or 1)
    process_executor = ProcessPoolExecutor(max_workers=max_workers)
    thread_executor = ThreadPoolExecutor(max_workers=max_workers * 2)
    
    logger.info(f"Started executors: {max_workers} process workers, {max_workers * 2} thread workers")
    
    yield
    
    # Shutdown
    if process_executor:
        process_executor.shutdown(wait=True)
    if thread_executor:
        thread_executor.shutdown(wait=True)
    logger.info("Executors shut down")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def save_file_async(file: UploadFile, temp_path: str) -> None:
    """Asynchronously save uploaded file"""
    def _save_file():
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    
    await run_in_threadpool(_save_file)

async def cleanup_file_async(file_path: str) -> None:
    """Asynchronously cleanup file"""
    def _cleanup():
        if os.path.exists(file_path):
            os.remove(file_path)
    
    await run_in_threadpool(_cleanup)

def validate_image_file(file: UploadFile) -> None:
    """Validate uploaded file is an image"""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return "<h1>Background Processing API - Performance Optimized</h1>"

@app.post("/remove-background/")
async def remove_background(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Remove background with parallel processing optimization"""
    validate_image_file(file)
    
    temp_input_path = f"temp_{uuid.uuid4().hex}_{file.filename}"
    output_path = None
    
    try:
        # Save file asynchronously in thread pool
        await save_file_async(file, temp_input_path)
        
        # Process image in thread pool (non-blocking)
        output_path = await run_in_threadpool(process_remove_bg, temp_input_path)
        
        # Read processed file asynchronously
        def read_output():
            with open(output_path, "rb") as f:
                return f.read()
        
        file_content = await run_in_threadpool(read_output)
        
        # Schedule cleanup in background (after response sent)
        background_tasks.add_task(cleanup_file_async, temp_input_path)
        if output_path:
            background_tasks.add_task(cleanup_file_async, output_path)
        
        return StreamingResponse(
            io.BytesIO(file_content), 
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename=no_bg_{file.filename}"}
        )

    except CustomException as e:
        logger.error(f"Custom exception: {e}")
        # Immediate cleanup on error
        await cleanup_file_async(temp_input_path)
        if output_path:
            await cleanup_file_async(output_path)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        # Immediate cleanup on error
        await cleanup_file_async(temp_input_path)
        if output_path:
            await cleanup_file_async(output_path)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/add-background/")
async def add_background(
    background_tasks: BackgroundTasks,
    foreground: UploadFile = File(...),
    background: UploadFile = File(...)
):
    """Add background with concurrent file processing"""
    validate_image_file(foreground)
    validate_image_file(background)

    temp_foreground_path = f"temp_foreground_{uuid.uuid4().hex}_{foreground.filename}"
    temp_background_path = f"temp_background_{uuid.uuid4().hex}_{background.filename}"
    output_path = None

    try:
        # Save both files concurrently using asyncio.gather
        await asyncio.gather(
            save_file_async(foreground, temp_foreground_path),
            save_file_async(background, temp_background_path)
        )

        # Process images in thread pool (non-blocking)
        output_path = await run_in_threadpool(
            process_add_bg, 
            temp_foreground_path, 
            temp_background_path
        )
        
        # Read processed file asynchronously
        def read_output():
            with open(output_path, "rb") as f:
                return f.read()
        
        file_content = await run_in_threadpool(read_output)

        # Schedule cleanup in background
        background_tasks.add_task(cleanup_file_async, temp_foreground_path)
        background_tasks.add_task(cleanup_file_async, temp_background_path)
        if output_path:
            background_tasks.add_task(cleanup_file_async, output_path)

        return StreamingResponse(
            io.BytesIO(file_content), 
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename=with_bg_{foreground.filename}"}
        )

    except CustomException as e:
        logger.error(f"Custom exception: {e}")
        # Immediate cleanup on error
        await asyncio.gather(
            cleanup_file_async(temp_foreground_path),
            cleanup_file_async(temp_background_path),
            return_exceptions=True
        )
        if output_path:
            await cleanup_file_async(output_path)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        # Immediate cleanup on error
        await asyncio.gather(
            cleanup_file_async(temp_foreground_path),
            cleanup_file_async(temp_background_path),
            return_exceptions=True
        )
        if output_path:
            await cleanup_file_async(output_path)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "cpu_count": os.cpu_count(),
        "thread_pool_active": bool(thread_executor),
        "process_pool_active": bool(process_executor)
    }

if __name__ == "__main__":
    uvicorn_run("app:app",host="0.0.0.0", port=8001, reload=True)
