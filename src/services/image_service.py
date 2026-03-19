"""
Image Service: Extract text from images for cyberbullying detection.
Applies image preprocessing to maximize OCR accuracy.
"""
import logging
import io
import os
import base64
from typing import Dict
from PIL import Image, ImageFilter, ImageEnhance, ImageOps


class ImageService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pytesseract = None
        self.ocr_available = False
        self._init_tesseract()

    def _init_tesseract(self):
        """Initialize Tesseract with path auto-detection."""
        try:
            import pytesseract
            self.pytesseract = pytesseract

            # Resolve path: .env → common install locations → system PATH
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

            # If no path found via exists(), force the default Windows path anyway
            # (os.path.exists can fail with spaces in path on some environments)
            if not path_set:
                default = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                pytesseract.pytesseract.tesseract_cmd = default
                self.logger.info(f"Forcing Tesseract path to: {default}")

            # Ensure TESSDATA_PREFIX is set so Tesseract can find language data
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

            # Verify it actually works
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
        Applies multiple preprocessing passes and picks the best result.
        """
        if not self.ocr_available:
            return {
                'success': False,
                'error': (
                    'Tesseract OCR is not installed or not in PATH.\n'
                    'Windows: download from https://github.com/UB-Mannheim/tesseract/wiki\n'
                    'Linux:   sudo apt install tesseract-ocr\n'
                    'Mac:     brew install tesseract\n'
                    'Then set TESSERACT_PATH in your .env file and restart the server.'
                ),
                'text': '',
                'installation_required': True,
            }

        try:
            image = Image.open(io.BytesIO(image_data))
            self.logger.info(f"Image loaded — size: {image.size}, mode: {image.mode}")

            text, method = self._extract_best(image)

            if not text:
                return {
                    'success': True,
                    'text': '',
                    'length': 0,
                    'image_size': image.size,
                    'warning': 'No text detected. Ensure the image has clear, readable text.',
                }

            self.logger.info(f"Extracted {len(text)} chars via '{method}'")
            return {
                'success': True,
                'text': text,
                'length': len(text),
                'image_size': image.size,
                'method': method,
            }

        except Exception as e:
            self.logger.error(f"OCR error: {e}", exc_info=True)
            return {'success': False, 'error': str(e), 'text': ''}

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
    # Preprocessing helpers
    # ------------------------------------------------------------------

    def _to_rgb(self, image: Image.Image) -> Image.Image:
        """Ensure image is in RGB mode."""
        if image.mode not in ('RGB', 'L'):
            image = image.convert('RGB')
        return image

    def _preprocess_standard(self, image: Image.Image) -> Image.Image:
        """
        Standard preprocessing:
        - Convert to grayscale
        - Upscale small images (Tesseract works best at ~300 DPI)
        - Sharpen + increase contrast
        """
        img = self._to_rgb(image).convert('L')  # grayscale

        # Upscale if too small
        w, h = img.size
        if w < 800 or h < 800:
            scale = max(800 / w, 800 / h, 2.0)
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

        img = ImageEnhance.Contrast(img).enhance(2.0)
        img = ImageEnhance.Sharpness(img).enhance(2.0)
        return img

    def _preprocess_binarize(self, image: Image.Image) -> Image.Image:
        """
        Binarization preprocessing:
        - Grayscale → threshold to pure black/white
        - Helps with low-contrast or noisy backgrounds
        """
        img = self._preprocess_standard(image)
        # Simple threshold at midpoint
        img = img.point(lambda p: 255 if p > 128 else 0, '1').convert('L')
        return img

    def _preprocess_inverted(self, image: Image.Image) -> Image.Image:
        """Invert colors — useful for white text on dark backgrounds."""
        img = self._preprocess_standard(image)
        return ImageOps.invert(img)

    def _preprocess_denoise(self, image: Image.Image) -> Image.Image:
        """Apply median filter to reduce noise before OCR."""
        img = self._preprocess_standard(image)
        img = img.filter(ImageFilter.MedianFilter(size=3))
        return img

    def _preprocess_large(self, image: Image.Image) -> Image.Image:
        """Aggressive upscale for very small/thumbnail images."""
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
        """Run Tesseract on a PIL image and return cleaned text."""
        text = self.pytesseract.image_to_string(image, config=config)
        return self._clean(text)

    @staticmethod
    def _clean(text: str) -> str:
        """Remove noise characters and collapse whitespace."""
        import re
        # Keep printable ASCII + common punctuation
        text = re.sub(r'[^\x20-\x7E\n]', ' ', text)
        # Collapse multiple spaces/newlines
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def _extract_best(self, image: Image.Image):
        """
        Try multiple preprocessing + Tesseract config combinations.
        Returns (best_text, method_name).
        """
        # (label, preprocessor, tesseract_config)
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
                processed = preprocess(image)
                text = self._run_ocr(processed, config)
                self.logger.debug(f"[{label}] extracted {len(text)} chars")

                # Prefer the result with the most content
                if len(text) > len(best_text):
                    best_text = text
                    best_method = label

                # Early exit if we already have a solid result
                if len(best_text) > 100:
                    break

            except Exception as e:
                self.logger.debug(f"[{label}] failed: {e}")
                continue

        return best_text, best_method
