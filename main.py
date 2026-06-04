import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf_to_img import pdf_to_images
from img_to_txt import image_to_text
from extractor_llm import extract_invoice_llm


OUTPUT_FOLDER = Path("output")


def process_invoice(pdf_path: str) -> None:
    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        print(f"\nError: File not found — {pdf_path}")
        return
    if pdf_file.suffix.lower() != ".pdf":
        print(f"\nError: Expected a .pdf file, got: {pdf_file.suffix}")
        return

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    print(f"\n[1/3] Converting PDF to images: {pdf_file.name}")
    try:
        images = pdf_to_images(str(pdf_file))
    except Exception as exc:
        print(f"Error converting PDF to images: {exc}")
        return
    print(f"      Found {len(images)} page(s)")

    print(f"\n[2/3] Running OCR on {len(images)} page(s)...")
    all_texts = []

    for i, image_np in enumerate(images, start=1):
        txt_filename = (
            f"{pdf_file.stem}.txt"
            if len(images) == 1
            else f"{pdf_file.stem}_page{i}.txt"
        )
        txt_path = OUTPUT_FOLDER / txt_filename
        print(f"      Page {i}/{len(images)} → {txt_path}")

        try:
            text = image_to_text(image_np, str(txt_path))
            all_texts.append(text)
        except Exception as exc:
            print(f"      Warning: OCR failed for page {i}: {exc}")
            all_texts.append("")

    full_text = "\n\n".join(all_texts).strip()

    if not full_text:
        print("\nError: OCR produced no text. Cannot extract invoice data.")
        return

    if len(images) > 1:
        combined_txt_path = OUTPUT_FOLDER / f"{pdf_file.stem}_all_pages.txt"
        combined_txt_path.write_text(full_text, encoding="utf-8")
        print(f"\n      Combined text saved → {combined_txt_path}")

    print(f"\n[3/3] Extracting invoice fields with LLM...")
    try:
        result = extract_invoice_llm(full_text)
    except Exception as exc:
        print(f"Error during LLM extraction: {exc}")
        return

    json_path = OUTPUT_FOLDER / f"{pdf_file.stem}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\nJSON saved → {json_path}")
    print(f"\n--- Preview ---")
    print(f"  Vendor      : {result.get('vendor_name')}")
    print(f"  Invoice No  : {result.get('vendor_invoice_number')}")
    print(f"  Invoice Date: {result.get('vendor_invoice_date')}")
    print(f"  Total Amount: {result.get('total_invoice_amount')}")
    print(f"  Line Items  : {len(result.get('invoiceMaterialLineItems', []))}")


def main() -> None:
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1].strip().strip("'\"")
    else:
        pdf_path = input("\nEnter PDF path: ").strip().strip("'\"")

    process_invoice(pdf_path)


if __name__ == "__main__":
    main()