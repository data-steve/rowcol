from typing import Dict

class OCRAdapter:
    def extract_document(self, file_path: str) -> Dict:
        """
        Extract fields from a document (mocked until PaddleOCR is integrated).
        :param file_path: Path to document (e.g., PDF, image).
        :return: Dictionary of extracted fields.
        """
        # Mock implementation
        return {
            "vendor_name": "Starbucks",
            "amount": 10.50,
            "date": "2025-08-13",
            "invoice_number": "INV123"
        }

class PaddleOCRAdapter(OCRAdapter):
    def extract_document(self, file_path: str) -> Dict:
        # Placeholder for PaddleOCR integration
        # Install: pip install paddleocr
        # from paddleocr import PaddleOCR
        # ocr = PaddleOCR(use_angle_cls=True, lang='en')
        # result = ocr.ocr(file_path, cls=True)
        return super().extract_document(file_path)  # Use mock for now

def get_ocr_adapter() -> OCRAdapter:
    return PaddleOCRAdapter()  # Swap with VeryfiAdapter or others later