import os
import re
from typing import List, Dict, Any
from pypdf import PdfReader

class PDFParserService:
    """
    Extracts text from PDF documents page-by-page and segments into
    structured chunks preserving metadata (sector, item_id, source_file, page).
    """

    @staticmethod
    def parse_pdf(file_path: str, default_sector: str = None) -> List[Dict[str, Any]]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found at: {file_path}")

        reader = PdfReader(file_path)
        source_file = os.path.basename(file_path)
        chunks = []

        current_sector = default_sector or "general"

        # Regex patterns for structured items e.g., [CRS-0001], [TCH-0001], [POL-0001]
        item_pattern = re.compile(r"\[([A-Z]{3}-\d{4})\]\s*(.*?)(?=\n|\|)")
        sector_header_pattern = re.compile(r"SECTOR:\s*([A-Z_ ]+)", re.IGNORECASE)

        for page_idx, page in enumerate(reader.pages):
            page_num = page_idx + 1
            raw_text = page.extract_text() or ""
            lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

            if not lines:
                continue

            # Check if this page introduces a new sector banner
            for line in lines:
                sec_match = sector_header_pattern.search(line)
                if sec_match:
                    sec_name = sec_match.group(1).strip().lower().replace(" ", "_")
                    if "course" in sec_name:
                        current_sector = "courses_curriculum"
                    elif "teacher" in sec_name:
                        current_sector = "teachers_centers"
                    elif "policy" in sec_name or "support" in sec_name:
                        current_sector = "policies_support"
                    else:
                        current_sector = sec_name

            # Group lines into item blocks
            page_text = "\n".join(lines)
            
            # If the PDF contains structured item tags like [CRS-XXXX]
            item_matches = list(re.finditer(r"\[([A-Z]{3}-\d{4})\]", page_text))
            
            if item_matches:
                for idx, match in enumerate(item_matches):
                    item_id = match.group(1)
                    start_pos = match.start()
                    end_pos = item_matches[idx + 1].start() if idx + 1 < len(item_matches) else len(page_text)
                    item_block = page_text[start_pos:end_pos].strip()

                    # Deduce sector from item_id prefix if available
                    item_sector = current_sector
                    if item_id.startswith("CRS"):
                        item_sector = "courses_curriculum"
                    elif item_id.startswith("TCH"):
                        item_sector = "teachers_centers"
                    elif item_id.startswith("POL"):
                        item_sector = "policies_support"

                    # Clean content
                    clean_content = " ".join(item_block.split())

                    chunks.append({
                        "item_id": item_id,
                        "sector": item_sector,
                        "source_file": source_file,
                        "page": page_num,
                        "content": clean_content
                    })
            else:
                # Generic fallback chunking for arbitrary PDFs (split into ~500-char paragraphs)
                paragraphs = page_text.split("\n\n")
                chunk_counter = 1
                for para in paragraphs:
                    cleaned_para = " ".join(para.split())
                    if len(cleaned_para) > 40:
                        chunks.append({
                            "item_id": f"CHUNK-P{page_num}-{chunk_counter}",
                            "sector": current_sector,
                            "source_file": source_file,
                            "page": page_num,
                            "content": cleaned_para
                        })
                        chunk_counter += 1

        return chunks
