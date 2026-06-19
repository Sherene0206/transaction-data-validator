Build a complete production-ready MVP web application called "Transaction Data Validator & Processor" using the following architecture and requirements.

## Objective

Create a web-based platform that allows users to upload transaction CSV files, validate the data, generate cleaned output files, generate error reports, split large CSV files into smaller chunks, and download all generated files.

The application should be simple, modern, responsive, and suitable for deployment on Render.

---

## Tech Stack

Backend:

* Python 3.11+
* FastAPI
* Pandas
* Uvicorn

Frontend:

* HTML5
* CSS3
* Bootstrap 5
* Vanilla JavaScript

File Handling:

* CSV processing using Pandas

Deployment:

* Render-compatible
* requirements.txt included

Do NOT use:

* Database
* Authentication
* User accounts
* Machine learning
* External paid APIs

---

## Project Structure

transaction-data-validator/

backend/

main.py

validator.py

chunker.py

country_rules.json

requirements.txt

uploads/

outputs/

frontend/

index.html

style.css

script.js

README.md

---

## User Flow

1. User opens the application.
2. User uploads a CSV file.
3. User clicks "Validate & Process".
4. Backend validates all rows.
5. Backend generates:

   * cleaned_transactions.csv
   * validation_errors.csv
   * chunked CSV files if needed
6. UI displays:

   * Total Rows
   * Valid Rows
   * Invalid Rows
7. User can download:

   * Cleaned CSV
   * Error Report CSV
   * Chunk Files ZIP

---

## CSV Input Format

Assume uploaded transaction CSV contains fields like:

order_id
customer_name
phone_number
country
order_date
order_time
product_name
quantity
amount
payment_mode

The application should work even if there are additional columns.

---

## Validation Rules

### Order Validation

order_id:

* Required
* Cannot be empty
* Must be unique

### Customer Validation

customer_name:

* Cannot be empty

### Phone Validation

Phone number validation should be configurable using a JSON configuration file.

Create country_rules.json:

{
"India": 10,
"Singapore": 8,
"USA": 10,
"Malaysia": 9
}

Validation logic:

* Remove spaces
* Remove dashes
* Validate digit count according to country
* Reject invalid phone numbers

Examples:

India:
9876543210 -> valid
98765 -> invalid

Singapore:
12345678 -> valid
12345 -> invalid

### Date Validation

Allowed format:

YYYY-MM-DD

Examples:

2025-05-20 -> valid
20/05/2025 -> invalid
abc -> invalid

### Time Validation

Allowed format:

HH:MM:SS

Examples:

14:30:00 -> valid
25:99:00 -> invalid

### Product Validation

product_name:

* Required
* Cannot be empty

### Quantity Validation

quantity:

* Must be positive integer

### Amount Validation

amount:

* Must be positive numeric value
* Cannot be negative

### Payment Mode Validation

Allowed values:

UPI
Card
Cash
NetBanking
Wallet

Any other value should be marked invalid.

---

## Error Reporting

Create validation_errors.csv.

For every invalid row include:

row_number
order_id
error_reason

Examples:

Invalid Phone Number
Invalid Date Format
Duplicate Order ID
Missing Product Name
Invalid Payment Mode
Negative Amount

Multiple validation failures should be concatenated in one error field.

Example:

Invalid Phone Number; Invalid Date

---

## Clean Output File

Create cleaned_transactions.csv.

Only valid rows should be included.

No invalid rows should appear.

---

## CSV Chunking

If cleaned_transactions.csv contains more than 5000 rows:

Split into:

chunk_1.csv
chunk_2.csv
chunk_3.csv

Each chunk should contain maximum 5000 rows.

Store chunks inside outputs/chunks/

Create downloadable ZIP file automatically containing all chunks.

---

## Backend Endpoints

Create FastAPI endpoints.

POST /upload

Responsibilities:

* Receive CSV file
* Validate data
* Generate output files
* Generate chunks if needed
* Return statistics

Response Example:

{
"total_rows": 10000,
"valid_rows": 9700,
"invalid_rows": 300,
"clean_file": "/download/cleaned_transactions.csv",
"error_file": "/download/validation_errors.csv",
"chunk_zip": "/download/chunks.zip"
}

GET /download/{filename}

Download generated files.

---

## Frontend Requirements

Create a professional dashboard.

Header:
Transaction Data Validator & Processor

Upload Section:

* File input
* Upload button

Processing State:

* Loading spinner

Results Section:
Cards displaying:

* Total Rows
* Valid Rows
* Invalid Rows

Downloads Section:
Buttons:

* Download Clean File
* Download Error Report
* Download Chunk ZIP

Use Bootstrap cards and responsive layout.

Support desktop and mobile.

---

## Backend Implementation Details

validator.py

Create reusable functions:

validate_phone()
validate_date()
validate_time()
validate_order()
validate_amount()
validate_payment_mode()

Return detailed error messages.

chunker.py

Create reusable chunk generation function.

main.py

Create FastAPI application.
Register all endpoints.
Handle file uploads.
Call validator functions.
Generate output files.

---

## Additional Requirements

1. Include comments throughout the code.
2. Follow clean architecture principles.
3. Use modular design.
4. Add exception handling.
5. Validate file type before processing.
6. Accept only CSV files.
7. Create uploads and outputs folders automatically if missing.
8. Generate files with unique timestamps.
9. Include requirements.txt.
10. Include README.md with setup instructions.

---

## UI Design

Modern SaaS style.

Colors:

* White background
* Blue primary buttons
* Clean card design
* Rounded corners
* Professional internship-project appearance

Do not overcomplicate the design.

Focus on functionality and clean user experience.

Generate all files and complete implementation from scratch.
