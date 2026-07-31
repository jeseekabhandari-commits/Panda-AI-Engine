import io
from pypdf import PdfReader
from fastapi import HTTPException, status


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Reads binary PDF bytes and extracts all text content."""
    try:
        # Load PDF from bytes stream in memory
        pdf_file = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_file)
        
        extracted_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"

        cleaned_text = extracted_text.strip()
        
        if not cleaned_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract any readable text from the uploaded PDF."
            )
            
        return cleaned_text

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Corrupted or invalid PDF file: {str(e)}"
        )