from openai import OpenAI
import json, uuid, os
from datetime import datetime, timezone

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY", "your_groq_api_key_here"),
    base_url="https://api.groq.com/openai/v1"
)

SYSTEM_PROMPT = """You are an invoice data extraction engine.
Extract ALL fields from the invoice text and return ONLY valid JSON matching this exact schema.
No explanation, no markdown, no extra text — just the raw JSON object.

{
  "vendor_name": "",
  "vendor_taxid": "",
  "vendor_pan": "",
  "vendor_po": "Not Mentioned",
  "vendor_po_date": null,
  "vendor_invoice_number": "",
  "vendor_invoice_date": "",
  "total_tax_cgst_amount": "",
  "total_tax_sgst_amount": "",
  "total_tax_amount": "",
  "total_invoice_amount": "",
  "bank_name": "",
  "bank_account_no": "",
  "bank_ifsc": "",
  "bank_branch": "",
  "invoiceMaterialLineItems": [
    {
      "item_no": "1",
      "material_code": "",
      "material_description": "",
      "quantity": "",
      "rate": "",
      "uom": "",
      "amount": "",
      "hsn_code": "",
      "tax_cgst_amount": "",
      "tax_cgst_rate": "",
      "tax_igst_amount": "0.00",
      "tax_igst_rate": "0.00",
      "tax_sgst_amount": "",
      "tax_sgst_rate": "",
      "line_total_amount": ""
    }
  ]
}

Rules:
- All numeric values must be strings with exactly 2 decimal places e.g. "241.20", "9.00"
- Dates must be in ISO 8601 format: YYYY-MM-DDTHH:mm:ss.sssZ  e.g. "2025-06-09T00:00:00.000Z"
- If a field is not found in the invoice, use "" for strings or null for date fields
- Extract ALL line items found in the invoice, one object per item
- hsn_code must be a string e.g. "3208" or "38140010"
- Do not invent, assume, or guess any data
- vendor_pan is typically 10 characters e.g. "AHZPC8211H"
- vendor_taxid is the GSTIN e.g. "27AHZPC8211H1Z3"
"""


def fmt_decimal(val) -> str:
    if val is None or val == "":
        return "0.00"
    try:
        return f"{float(str(val).replace(',', '')):.2f}"
    except Exception:
        return str(val)


def post_process(data: dict) -> dict:
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    invoice_id = str(uuid.uuid4())
    vendor_invoices_id = str(uuid.uuid4())

    output = {
        "id": invoice_id,
        "vendor_code": "",
        "vendor_invoices_id": vendor_invoices_id,
        "vendor_name": data.get("vendor_name", ""),
        "vendor_taxid": data.get("vendor_taxid", ""),
        "vendor_pan": data.get("vendor_pan", ""),
        "vendor_po": data.get("vendor_po", "Not Mentioned"),
        "vendor_po_date": data.get("vendor_po_date", None),
        "vendor_invoice_number": data.get("vendor_invoice_number", ""),
        "vendor_invoice_date": data.get("vendor_invoice_date", ""),
        "total_tax_cgst_amount": fmt_decimal(data.get("total_tax_cgst_amount")),
        "total_tax_sgst_amount": fmt_decimal(data.get("total_tax_sgst_amount")),
        "total_tax_amount": fmt_decimal(data.get("total_tax_amount")),
        "total_invoice_amount": fmt_decimal(data.get("total_invoice_amount")),
        "bank_name": data.get("bank_name", ""),
        "bank_account_no": data.get("bank_account_no", ""),
        "bank_ifsc": data.get("bank_ifsc", ""),
        "bank_branch": data.get("bank_branch", ""),
        "createdAt": now,
        "updatedAt": now,
        "invoiceMaterialLineItems": []
    }

    for i, item in enumerate(data.get("invoiceMaterialLineItems", []), 1):
        output["invoiceMaterialLineItems"].append({
            "id": str(uuid.uuid4()),
            "vendor_invoices_details_id": invoice_id,
            "item_no": str(item.get("item_no", i)),
            "material_code": item.get("material_code", ""),
            "material_description": item.get("material_description", ""),
            "quantity": fmt_decimal(item.get("quantity")),
            "rate": fmt_decimal(item.get("rate")),
            "uom": item.get("uom", ""),
            "amount": fmt_decimal(item.get("amount")),
            "hsn_code": str(item.get("hsn_code", "")),
            "tax_cgst_amount": fmt_decimal(item.get("tax_cgst_amount")),
            "tax_cgst_rate": fmt_decimal(item.get("tax_cgst_rate")),
            "tax_igst_amount": fmt_decimal(item.get("tax_igst_amount", "0")),
            "tax_igst_rate": fmt_decimal(item.get("tax_igst_rate", "0")),
            "tax_sgst_amount": fmt_decimal(item.get("tax_sgst_amount")),
            "tax_sgst_rate": fmt_decimal(item.get("tax_sgst_rate")),
            "line_total_amount": fmt_decimal(item.get("line_total_amount")),
            "createdAt": now,
            "updatedAt": now
        })

    return output


def extract_invoice_llm(invoice_text: str) -> dict:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"},
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract all fields from this invoice:\n\n{invoice_text}"}
        ]
    )
    raw = response.choices[0].message.content
    extracted = json.loads(raw)
    return post_process(extracted)