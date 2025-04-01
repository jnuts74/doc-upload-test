from PyPDF2 import PdfReader
from pathlib import Path
import re
from utils.logger import logger

class DocumentProcessor:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract_text(self, file_path: Path) -> str:
        """Extract text from a document."""
        try:
            if file_path.suffix.lower() == '.pdf':
                return self._extract_from_pdf(file_path)
            elif file_path.suffix.lower() in ['.txt']:
                return self._extract_from_text(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_path.suffix}")
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            raise

    def _extract_from_pdf(self, file_path: Path) -> str:
        """Extract text from a PDF file."""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return self._clean_text(text)
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {e}")
            raise

    def _extract_from_text(self, file_path: Path) -> str:
        """Extract text from a text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return self._clean_text(f.read())
        except Exception as e:
            logger.error(f"Error extracting text from text file {file_path}: {e}")
            raise

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text.strip()

    def create_chunks(self, text: str) -> list[str]:
        """Split text into overlapping chunks."""
        try:
            chunks = []
            if not text:
                return chunks

            start = 0
            while start < len(text):
                # Get chunk of size chunk_size
                end = start + self.chunk_size
                chunk = text[start:end]

                # If this is not the last chunk, try to break at a sentence boundary
                if end < len(text):
                    # Look for last sentence boundary in chunk
                    last_period = chunk.rfind('.')
                    if last_period != -1:
                        end = start + last_period + 1
                        chunk = text[start:end]

                chunks.append(chunk.strip())
                # Move start position, accounting for overlap
                start = end - self.chunk_overlap

            logger.info(f"Created {len(chunks)} chunks from text")
            return chunks
        except Exception as e:
            logger.error(f"Error creating chunks: {e}")
            raise

# Create a singleton instance
document_processor = DocumentProcessor() 