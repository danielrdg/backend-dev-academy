import io
import base64
import pdfplumber
import pytesseract
from fastapi import UploadFile, HTTPException

async def extract_text_from_pdf(file: UploadFile) -> str:
    #Extrai o texto de um arquivo PDF
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Arquivo vazio")
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    return text

async def extract_text_from_image(file: UploadFile) -> str:
    #Extrai o texto de uma imagem
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Arquivo vazio")
    image = io.BytesIO(content)
    text = pytesseract.image_to_string(image)
    return text

async def extract_text_from_file(file: UploadFile) -> str:
    #Extrai o texto de um arquivo PDF ou imagem
    if file.content_type == "application/pdf":
        return await extract_text_from_pdf(file)
    elif file.content_type.startswith("image/"):
        return await extract_text_from_image(file)
    else:
        raise HTTPException(status_code=400, detail="Tipo de arquivo não suportado")
    
async def file_to_base64(file: UploadFile) -> str:
    """
    Converte qualquer UploadFile em string Base64 (sem prefixo data URI).
    """
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Arquivo vazio")
    return base64.b64encode(data).decode("utf-8")
