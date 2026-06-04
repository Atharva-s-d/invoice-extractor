from pathlib import Path
from paddleocr import PaddleOCR
# try:
    
# except ImportError as e:
#     raise ImportError("PaddleOCR is required. Install it with: pip install paddleocr") from e

_ocr_instance = None


def _get_ocr():
    global _ocr_instance
    if _ocr_instance is None:
        print("  Loading OCR models (first run only)...")
        _ocr_instance = PaddleOCR(
            det_model_dir=None,
            rec_model_dir=None,
            cls_model_dir=None,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_angle_cls=False,
            use_gpu=False,
            cpu_threads=4,
            enable_mkldnn=False,
            lang="en",
            show_log=False,
        )
    return _ocr_instance


def image_to_text(image_np, output_txt_path: str) -> str:
    ocr = _get_ocr()
    result = ocr.ocr(image_np, cls=False)

    if not result or result[0] is None:
        print("  Warning: No text was detected in the image.")
        ocr_text = ""
    else:
        lines = [line[1][0] for line in result[0]]
        ocr_text = "\n".join(lines)

    output_path = Path(output_txt_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(ocr_text, encoding="utf-8")
    return ocr_text