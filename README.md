# Transaction Data Validator & Processor

A lightweight, production-ready MVP web application for validating, processing, and managing transaction CSV files.

## Features

✅ **CSV Upload & Validation** - Upload transaction files and validate against business rules  
✅ **Data Cleaning** - Generate cleaned output files with only valid transactions  
✅ **Error Reporting** - Detailed error reports with row numbers and error reasons  
✅ **CSV Chunking** - Automatically split large files (>5000 rows) into manageable chunks  
✅ **Download Results** - Download cleaned files, error reports, and chunked ZIP files  
✅ **Modern UI** - Responsive Bootstrap 5 interface for desktop and mobile  
✅ **Production Ready** - Deployable on Render with minimal configuration  

## Tech Stack

**Backend:**
- Python 3.11+
- FastAPI (modern async web framework)
- Pandas (data processing)
- Uvicorn (ASGI server)

**Frontend:**
- HTML5
- CSS3
- Bootstrap 5
- Vanilla JavaScript

## Project Structure

```
xeno-validator/
├── backend/
│   ├── main.py                    # FastAPI application
│   ├── validator.py               # Validation logic
│   ├── chunker.py                 # CSV chunking logic
│   ├── country_rules.json         # Phone validation rules by country
│   ├── requirements.txt           # Python dependencies
│   ├── uploads/                   # Temporary uploaded files
│   └── outputs/                   # Generated output files
├── frontend/
│   ├── index.html                 # Main HTML file
│   ├── style.css                  # Styling
│   └── script.js                  # Client-side logic
├── README.md                      # This file
└── .gitignore                     # Git ignore rules
```

## Installation

### Prerequisites
- Python 3.11+
- pip or pip3
- Git

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd xeno-validator
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

## Running Locally

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Start the FastAPI server:**
   ```bash
   python main.py
   ```

   The application will be available at: `http://localhost:8000`

## API Endpoints

### POST /upload
Upload and process a CSV file.

**Request:**
- Form data with file field containing CSV file

**Response:**
```json
{
  "total_rows": 10000,
  "valid_rows": 9700,
  "invalid_rows": 300,
  "clean_file": "/download/cleaned_transactions_20250619_120000.csv",
  "error_file": "/download/validation_errors_20250619_120000.csv",
  "chunk_zip": "/download/chunks_20250619_120000.zip"
}
```

### GET /download/{filename}
Download a generated file (CSV or ZIP).

## Validation Rules

### Order ID
- Required field
- Cannot be empty
- Must be unique across file

### Customer Name
- Required field
- Cannot be empty

### Phone Number
- Validated by country using `country_rules.json`
- Spaces and dashes are stripped before validation
- Digit count must match country rules:
  - India: 10 digits
  - Singapore: 8 digits
  - USA: 10 digits
  - Malaysia: 9 digits

### Order Date
- Format: `YYYY-MM-DD`
- Example: `2025-05-20`

### Order Time
- Format: `HH:MM:SS`
- Example: `14:30:00`

### Product Name
- Required field
- Cannot be empty

### Quantity
- Must be a positive integer
- Cannot be zero or negative

### Amount
- Must be a positive numeric value
- Cannot be negative

### Payment Mode
- Must be one of: `UPI`, `Card`, `Cash`, `NetBanking`, `Wallet`
- Case-sensitive

## File Processing

### Cleaned Output
- Contains only valid rows
- All invalid rows excluded
- Same column structure as input

### Error Report
- CSV with columns: `row_number`, `order_id`, `error_reason`
- Multiple validation failures concatenated with `; `
- Example: `Invalid Phone Number; Invalid Date Format`

### CSV Chunking
- If cleaned file exceeds 5000 rows, automatic chunking is triggered
- Creates `chunk_1.csv`, `chunk_2.csv`, etc.
- All chunks packaged in `chunks.zip` for download

## Deployment on Render

### Prerequisites
- Render account (free tier available)
- GitHub account (to push code)

### Steps

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Create Render Web Service:**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Use these settings:
     - **Name:** transaction-validator
     - **Environment:** Python 3.11
     - **Build Command:** `cd backend && pip install -r requirements.txt`
     - **Start Command:** `cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000`
     - **Port:** 8000

3. **Deploy:**
   - Click "Deploy Web Service"
   - Your app will be live at: `https://transaction-validator.onrender.com`

### Environment Variables
No environment variables are required for this MVP.

## Usage Example

1. Open the application in your browser
2. Click "Browse Files" or drag-drop a CSV file
3. Ensure your CSV has these columns:
   - order_id
   - customer_name
   - phone_number
   - country
   - order_date
   - order_time
   - product_name
   - quantity
   - amount
   - payment_mode
4. Click "Process File"
5. View results (Total, Valid, Invalid rows)
6. Download:
   - **Clean File** - validated transactions only
   - **Error Report** - details of invalid rows
   - **Chunks (ZIP)** - if applicable

## Sample CSV Format

```csv
order_id,customer_name,phone_number,country,order_date,order_time,product_name,quantity,amount,payment_mode
1001,John Doe,9876543210,India,2025-05-20,14:30:00,Laptop,1,45000.00,Card
1002,Jane Smith,98765432,Singapore,2025-05-21,10:15:00,Mouse,5,1500.00,UPI
1003,Bob Johnson,5551234567,USA,2025-05-22,16:45:00,Keyboard,2,3000.00,NetBanking
```

## Troubleshooting

### "Only CSV files are allowed"
- Ensure you're uploading a `.csv` file
- Check file extension and MIME type

### "CSV file is empty"
- Your CSV has no data rows (only headers)
- Add transaction records

### Validation errors not showing details
- Check browser console for error logs
- Ensure backend is running and accessible

### Files not downloading
- Browser may have blocked downloads; check settings
- Ensure sufficient disk space on your machine

## Performance

- Supports files with thousands of rows
- Automatic chunking for large datasets (>5000 rows)
- Async processing prevents UI blocking
- Optimized pandas operations for speed

## Security Considerations

- File uploads stored temporarily and cleaned after processing
- No database or user authentication required
- All processing done server-side
- No sensitive data logging
- Path traversal protection on file downloads

## License

This is an internship assignment project. Feel free to modify and extend as needed.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review error messages in browser console
3. Verify CSV format matches requirements
4. Check that all required columns are present

---

**Built with FastAPI + Pandas + Bootstrap** | Ready for Render Deployment ✨
