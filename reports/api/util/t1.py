import os 
import pdfplumber
from docx import Document
from striprtf.striprtf import rtf_to_text
import re

def CheckRoot(rootPath):        
    try:
            base_name = os.path.basename(rootPath)
            _ ,ext =os.path.splitext(base_name)

            allowed_ext =(".pdf",".docx",".txt",".rtf")
            
            if ext.lower() in allowed_ext:
                return True
            else:
                raise ValueError("File type not supported")
   
    except Exception as e :
        print(str(e))
        return False
    
def GetExt(rootPath):        
    try:
            base_name = os.path.basename(rootPath)
            _ ,ext =os.path.splitext(base_name)

            return ext.lower()
   
    except Exception as e :
        print(str(e))
        return False
    
def FromPdf(fileExt):
    text = ""
    with pdfplumber.open(fileExt) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    if not text.strip():
        raise ValueError(
            "This PDF contains no extractable text. It may be a scanned document."
        )

    return text

def FromDoc(fileExt):
    text = ""
    doc = Document(fileExt)

    for paragraph in doc.paragraphs:
         text+= paragraph+ "\n"
    return text

def FromTxt(fileExt):
    text = ""
    with open(fileExt, "r", encoding="utf-8") as file:
          text = file.read()
    return text
     
def FromRTF(fileExt):
    with open(fileExt, "r", encoding="utf-8") as file:
        return rtf_to_text(file.read())

def RemoveExtraSpaceAndGiveNumberOfWordsAndChr(txt):

    cleaned_text = re.sub(r'\s+', ' ', txt).strip()
    words = re.findall(r'\S+', cleaned_text)
    numberOfWords = len(words)
    without_spaces_text = re.sub(r'\s+', '', cleaned_text)
    NoOfChr = len(without_spaces_text)

    return {"Text": cleaned_text, "Words": numberOfWords, "Characters": NoOfChr}

def AssignAccordingToExt(file):
     
    ext = GetExt(file)

    if ext == '.docx':
          return RemoveExtraSpaceAndGiveNumberOfWordsAndChr(FromDoc(file))
    elif ext == ".pdf":
          return RemoveExtraSpaceAndGiveNumberOfWordsAndChr(FromPdf(file))
    elif ext == ".txt":
          return RemoveExtraSpaceAndGiveNumberOfWordsAndChr(FromTxt(file))
    elif ext == ".rtf":
          return RemoveExtraSpaceAndGiveNumberOfWordsAndChr(FromRTF(file))
    else:
        raise ValueError("Unsupported file type.")
    

        


