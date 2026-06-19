import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from validator import TransactionValidator
from chunker import CSVChunker

# Initialize FastAPI app
app = FastAPI(title="Transaction Data Validator & Processor")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static assets from frontend/static
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.parent / "frontend" / "static"),
    name="static"
)

# Create necessary directories
BACKEND_DIR = Path(__file__).parent
UPLOADS_DIR = BACKEND_DIR / "uploads"
OUTPUTS_DIR = BACKEND_DIR / "outputs"
HISTORY_FILE = UPLOADS_DIR / "history.json"
UPLOADS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

# Initialize validator
validator = TransactionValidator()

# Initialize upload history storage
if not HISTORY_FILE.exists():
    HISTORY_FILE.write_text(json.dumps([], indent=2))


def load_history():
    try:
        return json.loads(HISTORY_FILE.read_text())
    except Exception:
        return []


def save_history(history):
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


def add_history_item(item):
    history = load_history()
    history.insert(0, item)
    save_history(history)


def find_history_item(upload_id):
    history = load_history()
    for item in history:
        if item.get('upload_id') == upload_id:
            return item
    return None


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Handle CSV file upload, validation, and processing.
    
    Returns:
        - Statistics: total_rows, valid_rows, invalid_rows
        - Links to generated files: clean_file, error_file, chunk_zip
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        
        # Save uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        upload_path = UPLOADS_DIR / f"upload_{timestamp}.csv"
        
        contents = await file.read()
        with open(upload_path, 'wb') as f:
            f.write(contents)
        
        # Read CSV with pandas
        try:
            df = pd.read_csv(upload_path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid CSV file: {str(e)}")
        
        if len(df) == 0:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        
        # Process each row
        valid_rows = []
        invalid_rows = []
        seen_order_ids = set()
        
        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            is_valid, error_msg, order_id = validator.validate_row(
                row_dict, 
                seen_order_ids
            )
            
            if is_valid:
                valid_rows.append(row_dict)
            else:
                invalid_rows.append({
                    'row_number': idx + 2,  # +2 because CSV starts at row 1 + header
                    'order_id': order_id,
                    'error_reason': error_msg
                })
        
        # Generate output files
        clean_csv_path = OUTPUTS_DIR / f"cleaned_transactions_{timestamp}.csv"
        error_csv_path = OUTPUTS_DIR / f"validation_errors_{timestamp}.csv"
        
        # Write cleaned transactions
        if valid_rows:
            clean_df = pd.DataFrame(valid_rows)
            clean_df.to_csv(clean_csv_path, index=False)
        else:
            # Create empty file with headers
            clean_df = pd.DataFrame(columns=df.columns)
            clean_df.to_csv(clean_csv_path, index=False)
        
        # Write error report
        if invalid_rows:
            error_df = pd.DataFrame(invalid_rows)
            error_df.to_csv(error_csv_path, index=False)
        else:
            # Create file with headers only
            error_df = pd.DataFrame(
                columns=['row_number', 'order_id', 'error_reason']
            )
            error_df.to_csv(error_csv_path, index=False)

        # Build validation summary counts from invalid rows
        summary_counts = {}
        for invalid in invalid_rows:
            if invalid.get('error_reason'):
                for part in str(invalid['error_reason']).split(';'):
                    key = part.strip()
                    if not key:
                        continue
                    summary_counts[key] = summary_counts.get(key, 0) + 1

        validation_summary = [
            {"type": key, "count": summary_counts[key]}
            for key in sorted(summary_counts, key=lambda k: (-summary_counts[k], k))
        ]

        # Handle chunking if needed
        chunk_zip_path = None
        chunk_files, chunks_created = CSVChunker.create_chunks(
            clean_csv_path,
            OUTPUTS_DIR
        )

        if chunks_created:
            chunk_zip_path = CSVChunker.create_zip(
                chunk_files,
                OUTPUTS_DIR,
                timestamp
            )

        upload_id = f"upload_{timestamp}_{uuid.uuid4().hex[:8]}"
        history_item = {
            "upload_id": upload_id,
            "timestamp": timestamp,
            "total_rows": len(df),
            "valid_rows": len(valid_rows),
            "invalid_rows": len(invalid_rows),
            "clean_file": f"/download/cleaned_transactions_{timestamp}.csv",
            "error_file": f"/download/validation_errors_{timestamp}.csv",
            "chunk_zip": f"/download/chunks_{timestamp}.zip" if chunks_created else None,
            "validation_summary": validation_summary,
            "error_preview": invalid_rows[:10]
        }
        add_history_item(history_item)

        response = {
            "upload_id": upload_id,
            "total_rows": len(df),
            "valid_rows": len(valid_rows),
            "invalid_rows": len(invalid_rows),
            "validation_summary": validation_summary,
            "error_preview": invalid_rows[:10],
            "clean_file": history_item["clean_file"],
            "error_file": history_item["error_file"],
            "chunk_zip": history_item["chunk_zip"]
        }

        return response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download generated output files."""
    try:
        # Security: validate filename to prevent directory traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        file_path = OUTPUTS_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            file_path,
            media_type='application/octet-stream',
            filename=filename
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")


@app.get("/api/history")
async def get_history():
    """Return upload history metadata."""
    return load_history()


@app.get("/api/results/{upload_id}")
async def get_results(upload_id: str):
    """Return stored results for a given upload id."""
    item = find_history_item(upload_id)
    if not item:
        raise HTTPException(status_code=404, detail="Upload not found")
    return item


@app.get("/")
async def root():
    """Serve the frontend."""
    return FileResponse(Path(__file__).parent.parent / "frontend" / "index.html")


@app.get("/{full_path:path}")
async def spa_router(full_path: str):
    """Serve the frontend for SPA routes."""
    if full_path.startswith('api') or full_path.startswith('download') or full_path.startswith('static'):
        raise HTTPException(status_code=404, detail="Not Found")
    return FileResponse(Path(__file__).parent.parent / "frontend" / "index.html")


# Mount static files (CSS, JS)
frontend_dir = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
