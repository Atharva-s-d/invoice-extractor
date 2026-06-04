# Invoice AI

Invoice AI is a robust Python-based command-line utility for extracting structured data from PDF invoices. It uses a three-step pipeline: converting PDF pages to images, extracting text via OCR, and structuring the extracted text into JSON using a Large Language Model.

## Features

- **PDF to Image Conversion**: Efficiently converts single or multi-page PDF invoices into images using PyMuPDF.
- **Optical Character Recognition (OCR)**: Extracts raw text from images using the highly accurate PaddleOCR.
- **LLM-Powered Data Extraction**: Processes the raw text with Llama 3.3 70B (via the Groq API) to accurately extract key fields like vendor details, tax amounts, bank information, and individual line items.
- **Structured JSON Output**: Returns a highly structured JSON file representing the invoice data, formatted cleanly and ready for database insertion or further integration.

## Project Structure

```
invoice-ai/
├── main.py                  # The main entry point of the application
├── environment.yml          # Conda environment configuration
├── requirements.txt         # pip dependencies
├── src/
│   ├── pdf_to_img.py        # PDF to image conversion module
│   ├── img_to_txt.py        # OCR text extraction module
│   └── extractor_llm.py     # LLM structured extraction module
├── input/                   # Directory for placing input PDFs
└── output/                  # Directory where processed text and JSON are saved
```

## Prerequisites

- Python 3.8+
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) and its core dependencies.

## Installation

You can install the dependencies using either `pip` or `conda`:

**Using pip:**

```bash
pip install -r requirements.txt
```

**Using Conda:**

```bash
conda env create -f environment.yml
conda activate invoice-ai # or the name specified in environment.yml
```

## Configuration

The application uses the Groq API to access the LLM for data extraction. You should set your API key as an environment variable before running the application:

```bash
export GROQ_API_KEY="your_groq_api_key_here"
```

## Usage

You can run the script and provide the path to your PDF invoice either as a command-line argument or via an interactive prompt.

**Via Command Line Argument:**

```bash
python main.py "input/sample_invoice.pdf"
```

**Interactive Mode:**

```bash
python main.py
# The script will prompt you:
# Enter PDF path: input/sample_invoice.pdf
```

### Process & Output

When you run the tool, it executes the following steps:

1. Converts the PDF to images and saves them in memory.
2. Runs PaddleOCR on each page to extract raw text.
3. Passes the combined text to the LLM to extract fields based on a strict JSON schema.

The pipeline will automatically create an `output/` directory (if it doesn't exist) and save the following files:

- `<invoice_name>_page<N>.txt`: The raw text extracted from each page via OCR.
- `<invoice_name>_all_pages.txt`: Combined text (if the invoice has multiple pages).
- `<invoice_name>.json`: The final extracted structured data containing vendor details, bank info, tax breakdown, and line items.

## Troubleshooting

- **PaddleOCR Errors**: Ensure you have installed PaddleOCR correctly. The first run might take a while as it downloads the default OCR models.
- **No Text Detected**: Check if your PDF is empty or purely an unreadable image. The script requires valid image data for OCR.
- **LLM Extraction Errors**: Ensure your Groq API key is valid and has sufficient quota.
