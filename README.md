# Document Ingestion & Text Extraction

A Python pipeline for ingesting documents from various sources and extracting text content. Supports PDFs, Word documents, images, and plain text files.

## Features

- Download documents from URLs with retry logic
- Discover PDF links from web pages
- Optional PDF search via Google Custom Search API
- Text extraction with OCR fallback for scanned documents
- Export results to JSON and CSV
- REST API for programmatic access
- Web UI for interactive use

## Supported Formats

| Format | Extensions | Method |
|--------|------------|--------|
| PDF | .pdf | pdfminer (text) / OCR (scanned) |
| Word | .docx | python-docx |
| Images | .png, .jpg, .jpeg, .tiff, .bmp | Tesseract OCR |
| Plain text | .txt | Direct read |

## Requirements

- Python 3.11+
- Tesseract OCR (for scanned PDFs and images)
- Poppler (for PDF to image conversion)

### System Dependencies

**macOS:**
```bash
brew install tesseract poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr poppler-utils
```

## Installation

```bash
git clone https://github.com/BekOsu/document-ingestion-text-extraction.git
cd document-ingestion-text-extraction

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
```

## Configuration

Edit `.env` to set options:

```
DOWNLOAD_TIMEOUT=30
MAX_RETRIES=3
LOG_LEVEL=INFO

# Optional: for PDF search
GOOGLE_API_KEY=your-key
GOOGLE_CSE_ID=your-cse-id
```

## Usage

### Process local files

```bash
python -m app.main --files document.pdf report.docx image.png
```

### Download and process from URLs

```bash
python -m app.main --urls https://example.com/doc.pdf https://example.com/report.pdf
```

### Load URLs from file

```bash
python -m app.main --url-file urls.txt
```

### Scan web pages for PDF links

```bash
python -m app.main --pages https://example.com/publications
```

### Search for PDFs (requires Google API)

```bash
python -m app.main --search "annual report 2024 filetype:pdf"
```

### Output options

```bash
python -m app.main --files doc.pdf --output json   # JSON only
python -m app.main --files doc.pdf --output csv    # CSV only
python -m app.main --files doc.pdf --output both   # Both (default)
```

## Output Format

Results are saved to `data/processed/` with fields:

| Field | Description |
|-------|-------------|
| source_type | local, url, or web_page |
| source_url | Origin URL or page |
| pdf_url | Direct document URL |
| file_name | Local filename |
| page_count | Number of pages (PDF only) |
| extraction_method | pdfminer, ocr, python-docx, plaintext |
| extracted_text | Full text content |

## Project Structure

```
├── app/
│   ├── config.py              # Environment and paths
│   ├── main.py                # CLI entry point
│   ├── ingestion/
│   │   ├── url_sources.py     # URL loading and search
│   │   ├── pdf_discovery.py   # Web page link extraction
│   │   └── downloader.py      # File download with retries
│   ├── extraction/
│   │   ├── extractor.py       # Unified extraction router
│   │   ├── text_extractor.py  # PDF text extraction
│   │   ├── ocr.py             # OCR for scanned PDFs
│   │   ├── docx_extractor.py  # Word document extraction
│   │   ├── txt_extractor.py   # Plain text reader
│   │   └── image_extractor.py # Image OCR
│   └── export/
│       └── exporter.py        # JSON/CSV output
├── api/
│   └── main.py                # FastAPI server
├── frontend/                  # Next.js web UI
├── data/
│   ├── raw/                   # Downloaded files
│   └── processed/             # Extraction results
└── logs/                      # Application logs
```

## Web UI

A Next.js frontend for interactive document processing.

### Setup

```bash
cd frontend
npm install
```

### Run

Start both the API server and frontend:

```bash
# Terminal 1: API server
uvicorn api.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

- API: http://localhost:8000
- Frontend: http://localhost:3000

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/supported-formats` | List supported extensions |
| POST | `/extract/file` | Extract from uploaded file |
| POST | `/extract/url` | Extract from URL |
| POST | `/extract/batch` | Extract from multiple files |
| POST | `/export/json` | Process files and download JSON |
| POST | `/export/csv` | Process files and download CSV |

## Rate Limiting

When using URL sources, the downloader respects rate limits with exponential backoff. Configure `MAX_RETRIES` and `DOWNLOAD_TIMEOUT` in `.env` as needed.

For Google Custom Search API, free tier allows 100 queries/day.

## License

MIT