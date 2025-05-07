import io
import base64
import pdfplumber
import pytesseract
from PIL import Image
from fastapi import UploadFile, HTTPException

async def extract_text_from_pdf(file: UploadFile) -> str:
    """
    Extracts text content from a PDF file.
    """
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty PDF file")
    
    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        return text
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Error processing PDF: {str(e)}"
        )

async def extract_text_from_image(file: UploadFile) -> str:
    """
    Extracts text content from an image using OCR.
    """
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty image file")
    
    try:
        image = Image.open(io.BytesIO(content))
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Error processing image: {str(e)}"
        )

async def file_to_base64(file: UploadFile) -> str:
    """
    Converts any UploadFile to a Base64 string (without data URI prefix).
    
    Args:
        file (UploadFile): The file to convert
        
    Returns:
        str: Base64 encoded string of the file content
        
    Raises:
        HTTPException: If the file is empty
    """
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    return base64.b64encode(data).decode("utf-8")

async def process_file_content(file: UploadFile) -> tuple[str, str]:
    """
    Processes a file based on its MIME type and returns extracted content and content type.
    
    Args:
        file (UploadFile): The uploaded file to process
        
    Returns:
        tuple[str, str]: A tuple containing (extracted_content, content_type)
            - For PDFs and images with text: (extracted_text, "text")
            - For images without text: (base64_encoded_image, "image")
    """
    mime_type = file.content_type
    
    # Reset file position to start
    await file.seek(0)
    
    if mime_type == "application/pdf":
        text = await extract_text_from_pdf(file)
        return text, "text"
    
    elif mime_type.startswith("image/"):
        # First try to extract text via OCR
        await file.seek(0)
        try:
            text = await extract_text_from_image(file)
            # If OCR found meaningful text
            if text and len(text.strip()) > 10:
                return text, "text"
            # Otherwise, treat as pure image
            else:
                await file.seek(0)
                base64_image = await file_to_base64(file)
                return f"data:{mime_type};base64,{base64_image}", "image"
        except Exception:
            # If OCR fails, fall back to treating as pure image
            await file.seek(0)
            base64_image = await file_to_base64(file)
            return f"data:{mime_type};base64,{base64_image}", "image"
    
    else:
        # For other file types, just read as text if possible
        try:
            await file.seek(0)
            content = await file.read()
            text = content.decode("utf-8", errors="replace")
            return text, "text"
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {mime_type}. Error: {str(e)}"
            )

async def prepare_file_for_ai(file: UploadFile) -> dict:
    """
    Prepares a file for sending to AI models by extracting its content
    and determining the appropriate format.
    
    Args:
        file (UploadFile): The uploaded file
        
    Returns:
        dict: A dictionary with the following keys:
            - file_name: The original filename
            - mime_type: The MIME type of the file
            - content_type: Either "text" or "image"
            - content: The extracted content (text or base64 data URI)
    """
    # Store original filename and MIME type
    file_name = file.filename
    mime_type = file.content_type
    
    # Reset file position
    await file.seek(0)
    
    # Process file based on MIME type
    try:
        content, content_type = await process_file_content(file)
        
        return {
            "file_name": file_name,
            "mime_type": mime_type,
            "content_type": content_type,
            "content": content
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing file {file_name}: {str(e)}"
        )