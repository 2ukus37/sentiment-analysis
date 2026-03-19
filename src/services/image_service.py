"""
Image Service: Extract text from images for cyberbullying detection.
Uses Tesseract (local) with OCR.space (cloud) as fallback.
"""
import logging
import io
import os
import base64
import requests
from typing import Dict
from PIL import Image, ImageFilter, ImageEnhance, ImageOps


class ImageService:

    OCR_SPACE_URL = 'https://api.ocr.space/parse/image'

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pytesseract = None
        self.ocr_available = False
        self.ocr_space_key = os.getenv('OCR_SPACE_API_KEY', '')
        self._init_tesseract()

    def _init_tesseract(self):
        """Initialize Tesseract with path auto-detection."""
        try:
            import pytesseract
            self.pytesseract = pytesseract

            candidates = [
                os.getenv('TESSERACT_PATH', ''),
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                r'C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe'.format(
                    os.getenv('USERNAME', '')),
                '/usr/bin/tesseract',
                '/usr/local/bin/tesseract',
                '/opt/homebrew/bin/tesseract',
            ]

            path_set = False
            for path in candidates:
                if path and os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    self.logger.info(f"Tesseract found at: {path}")
                    path_set = True
                    break

            if not path_set:
                default = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                pytesseract.pytesseract.tesseract_cmd = default
                self.logger.info(f"Forcing Tesseract path to: {default}")

            # Ensure TESSDATA_PREFIX is set
            tessdata_candidates = [
                os.getenv('TESSDATA_PREFIX', ''),
                r'C:\Program Files\Tesseract-OCR\tessdata',
                r'C:\Program Files (x86)\Tesseract-OCR\tessdata',
                os.path.join(os.path.dirname(pytesseract.pytesseract.tesseract_cmd), 'tessdata'),
            ]
            for td in tessdata_candidates:
                if td and os.path.isdir(td):
                    os.environ['TESSDATA_PREFIX'] = td
                    self.logger.info(f"TESSDATA_PREFIX set to: {td}")
                    break

            pytesseract.get_tesseract_version()
            self.ocr_available = True
            self.logger.info("Tesseract OCR is ready")

        except ImportError:
            self.logger.warning("pytesseract not installed — run: pip install pytesseract")
        except Exception as e:
            self.logger.warning(f"Tesseract not accessible: {e}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_text_from_image(self, image_data: bytes) -> Dict:
        """
        Extract text from raw image bytes.
        Tries Tesseract first, falls back to OCR.space if result is empty.
        """
        image = None
        try:
            image = Image.open(io.BytesIO(image_data))
            self.logger.info(f"Image loaded — size: {image.size}, mode: {image.mode}")
        except Exception as e:
            return {'success': False, 'error': f'Cannot open image: {e}', 'text': ''}

        # --- Try Tesseract ---
        if self.ocr_available:
            try:
                text, method = self._extract_best(image)
                if text:
                    self.logger.info(f"Tesseract extracted {len(text)} chars via '{method}'")
                    return {
                        'success': True,
                        'text': text,
                        'length': len(text),
                        'image_size': image.size,
                        'method': f'tesseract:{method}',
                    }
                self.logger.info("Tesseract returned no text, trying OCR.space fallback")
            except Exception as e:
                self.logger.warning(f"Tesseract error: {e}, trying OCR.space fallback")

        # --- Fallback: OCR.space ---
        if self.ocr_space_key:
            result = self._ocr_space(image_data)
            if result.get('success') and result.get('text'):
                return result

        # --- Both failed ---
        if not self.ocr_available and not self.ocr_space_key:
            return {
                'success': False,
                'error': (
                    'No OCR engine available. Install Tesseract or set OCR_SPACE_API_KEY in .env.'
                ),
                'text': '',
            }

        return {
            'success': False,
            'error': (
                'No readable text found in the image.\n'
                'Tips:\n'
                '• Use a clear, high-resolution image\n'
                '• Ensure dark text on a light background\n'
                '• Try a screenshot instead of a photo'
            ),
            'text': '',
            'image_size': image.size if image else None,
        }

    def extract_text_from_base64(self, b64: str) -> Dict:
        """Extract text from a base64-encoded image string."""
        try:
            if ',' in b64:
                b64 = b64.split(',')[1]
            return self.extract_text_from_image(base64.b64decode(b64))
        except Exception as e:
            return {'success': False, 'error': str(e), 'text': ''}

    def is_image_file(self, filename: str) -> bool:
        exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        return os.path.splitext(filename.lower())[1] in exts

    # ------------------------------------------------------------------
    # OCR.space cloud fallback
    # ------------------------------------------------------------------

    def _ocr_space(self, image_data: bytes) -> Dict:
        """Send image to OCR.space API and return extracted text."""
        try:
            self.logger.info("Calling OCR.space API...")
            response = requests.post(
                self.OCR_SPACE_URL,
                files={'file': ('image.png', image_data, 'image/png')},
                data={
                    'apikey': self.ocr_space_key,
                    'language': 'eng',
                    'isOverlayRequired': False,
                    'detectOrientation': True,
                    'scale': True,
                    'OCREngine': 2,  # Engine 2 is better for complex images
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            if data.get('IsErroredOnProcessing'):
                err = data.get('ErrorMessage', ['Unknown OCR.space error'])
                self.logger.warning(f"OCR.space error: {err}")
                return {'success': False, 'error': str(err), 'text': ''}

            parsed = data.get('ParsedResults', [])
            if not parsed:
                return {'success': True, 'text': '', 'method': 'ocr.space'}

            text = self._clean(' '.join(
                r.get('ParsedText', '') for r in parsed
            ))
            self.logger.info(f"OCR.space extracted {len(text)} chars")
            return {
                'success': True,
                'text': text,
                'length': len(text),
                'method': 'ocr.space',
            }

        except Exception as e:
            self.logger.error(f"OCR.space request failed: {e}")
            return {'success': False, 'error': str(e), 'text': ''}

    # ------------------------------------------------------------------
    # Preprocessing helpers
    # ------------------------------------------------------------------

    def _to_rgb(self, image: Image.Image) -> Image.Image:
        if image.mode not in ('RGB', 'L'):
            image = image.convert('RGB')
        return image

    def _preprocess_standard(self, image: Image.Image) -> Image.Image:
        img = self._to_rgb(image).convert('L')
        w, h = img.size
        if w < 800 or h < 800:
            scale = max(800 / w, 800 / h, 2.0)
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        img = ImageEnhance.Contrast(img).enhance(2.0)
        img = ImageEnhance.Sharpness(img).enhance(2.0)
        return img

    def _preprocess_binarize(self, image: Image.Image) -> Image.Image:
        img = self._preprocess_standard(image)
        img = img.point(lambda p: 255 if p > 128 else 0, '1').convert('L')
        return img

    def _preprocess_inverted(self, image: Image.Image) -> Image.Image:
        img = self._preprocess_standard(image)
        return ImageOps.invert(img)

    def _preprocess_denoise(self, image: Image.Image) -> Image.Image:
        img = self._preprocess_standard(image)
        img = img.filter(ImageFilter.MedianFilter(size=3))
        return img

    def _preprocess_large(self, image: Image.Image) -> Image.Image:
        img = self._to_rgb(image).convert('L')
        w, h = img.size
        scale = max(1600 / w, 1600 / h, 3.0)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        img = ImageEnhance.Contrast(img).enhance(2.5)
        img = ImageEnhance.Sharpness(img).enhance(3.0)
        return img

    # ------------------------------------------------------------------
    # OCR runner
    # ------------------------------------------------------------------

    def _run_ocr(self, image: Image.Image, config: str = '') -> str:
        text = self.pytesseract.image_to_string(image, config=config)
        return self._clean(text)

    @staticmethod
    def _clean(text: str) -> str:
        import re
        text = re.sub(r'[^\x20-\x7E\n]', ' ', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def _extract_best(self, image: Image.Image):
        """Try multiple Tesseract strategies, return (best_text, method)."""
        strategies = [
            ('standard',       self._preprocess_standard,  '--oem 3 --psm 6'),
            ('binarize',       self._preprocess_binarize,  '--oem 3 --psm 6'),
            ('inverted',       self._preprocess_inverted,  '--oem 3 --psm 6'),
            ('denoise',        self._preprocess_denoise,   '--oem 3 --psm 6'),
            ('large_scale',    self._preprocess_large,     '--oem 3 --psm 6'),
            ('standard_psm3',  self._preprocess_standard,  '--oem 3 --psm 3'),
            ('standard_psm11', self._preprocess_standard,  '--oem 3 --psm 11'),
            ('binarize_psm4',  self._preprocess_binarize,  '--oem 3 --psm 4'),
        ]

        best_text = ''
        best_method = 'none'

        for label, preprocess, config in strategies:
            try:
                text = self._run_ocr(preprocess(image), config)
                self.logger.debug(f"[{label}] {len(text)} chars")
                if len(text) > len(best_text):
                    best_text = text
                    best_method = label
                if len(best_text) > 100:
                    break
            except Exception as e:
                self.logger.debug(f"[{label}] failed: {e}")

        return best_text, best_method
