import io
import os
import fitz  # PyMuPDF
from PIL import Image
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# Multi-modal Vision Model Initialization
vision_llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0.1,
    google_api_key=os.getenv("GEMINI_API_KEY")
)

def generate_image_summary(image_bytes: bytes, mime_type: str = "image/png") -> str:
    """Invokes Gemini vision capabilities to extract structured descriptions from document visuals."""
    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": (
                    "Analyze this image extracted from an enterprise document in detail. "
                    "If it is a diagram, chart, or system architecture, explain its components, "
                    "data flow, relationships, numbers, and structural context clearly."
                ),
            },
            {
                "type": "image_url",
                "image_url": f"data:{mime_type};base64,{image_bytes.hex()}" # Base64 payload or raw bytes interface
            },
        ]
    )
    response = vision_llm.invoke([message])
    return response.content

def extract_text_and_visuals_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """Extracts both textual content and embedded images/diagrams from a PDF."""
    doc = fitz.open(pdf_path)
    extracted_chunks: List[Dict[str, Any]] = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # 1. Extract Text
        text_content = page.get_text("text").strip()
        if text_content:
            extracted_chunks.append({
                "content": text_content,
                "type": "text",
                "page": page_num + 1
            })

        # 2. Extract Embedded Images / Diagrams
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            # Summarize extracted image using Gemini Vision
            visual_summary = generate_image_summary(image_bytes, mime_type=f"image/{image_ext}")
            
            extracted_chunks.append({
                "content": f"[Visual Asset - Page {page_num + 1} Diagram/Chart Summary]: {visual_summary}",
                "type": "visual_summary",
                "page": page_num + 1
            })

    return extracted_chunks