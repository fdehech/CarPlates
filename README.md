# CarPlates

A small **Flask REST API** that returns the latest car plate information using a **Python web scraper
(no WebDriver / no Selenium)**.

## Features
- Simple HTTP endpoints
- Case-insensitive `plate_type`
- No browser automation (no WebDriver)

## Tech Stack
- Python
- Flask
- Web scraping (requests + HTML parsing)

## Installation

### 1) Clone the project
```bash
git clone https://github.com/fdehech/CarPlates.git
cd CarPlates
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Run the API
```bash
python app.py
```
