import os 
import pdfplumber
from docx import Document
from striprtf.striprtf import rtf_to_text
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import spacy

nlp = spacy.load("en_core_web_sm")
stop_words = set(stopwords.words("english"))
lematizer = WordNetLemmatizer()
tech_skills = [
    "python",
    "java",
    "c",
    "cpp",
    "csharp",
    "javascript",
    "typescript",
    "html",
    "css",
    "bootstrap",
    "tailwind",
    "react",
    "nextjs",
    "nodejs",
    "express",
    "django",
    "flask",
    "fastapi",
    "sql",
    "mysql",
    "postgresql",
    "sqlite",
    "mongodb",
    "redis",
    "git",
    "github",
    "docker",
    "kubernetes",
    "aws",
    "azure"
]

# This function is use for check if the root exists and check if the extension is supported
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
    
# It used to get the extension from the file name
    
def GetExt(rootPath):        
    try:
            base_name = os.path.basename(rootPath)
            _ ,ext =os.path.splitext(base_name)

            return ext.lower()
   
    except Exception as e :
        print(str(e))
        return False
    
# It is used to extract pdf text  from the files 
    
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

# It is used to extract document text  from the files 


def FromDoc(fileExt):
    text = ""
    doc = Document(fileExt)

    for paragraph in doc.paragraphs:
         text+= paragraph.text+ "\n"
    return text

# It is used to extract text  from the files 


def FromTxt(fileExt):
    text = ""
    with open(fileExt, "r", encoding="utf-8") as file:
          text = file.read()
    return text

# It is used to extract  text  from the rtl files
     
def FromRTF(fileExt):
    with open(fileExt, "r", encoding="utf-8") as file:
        return rtf_to_text(file.read())
    
# this function uses the text and make it in order form to give json 

def RemoveExtraSpaceAndGiveNumberOfWordsAndChr(txt):

    cleaned_text = re.sub(r'\s+', ' ', txt).strip()
    words = re.findall(r'\S+', cleaned_text)
    numberOfWords = len(words)
    without_spaces_text = re.sub(r'\s+', '', cleaned_text)
    NoOfChr = len(without_spaces_text)
    lematizedWords = WordLemmatizer(txt)
    GivenSkills = CheckSkills(lematizedWords)
    entityData = ExtractEntity(cleaned_text)
    

    return {"Text": cleaned_text, "Words": numberOfWords, "Characters": NoOfChr,"LematizedWords":lematizedWords,
            "PersonSkills":GivenSkills,"PersonData":entityData}

# this function uses the file and return output according to it extension 

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
    
# this function remove the puntuation marks from the text

def RemovePunctuation(text):
    withoutSymbols = re.sub(r"[^\w\s]", "", text)
    return withoutSymbols

# this function give the text in clean array of text in token form 

def CleanTokens(text):
    data = RemovePunctuation(text)
    result=re.sub(r'\s+', ' ', data).strip()
    lists = result.split(" ")
    return lists

# this function used to remove the stopword from the text 
def RemoveStopWord(text):
    lists = CleanTokens(text)
    filter_words_list = [word for word in lists if word.lower() not in stop_words]
    return filter_words_list

# this function used to lemetized the list of filtered values 

def WordLemmatizer(filterWordArray):
    lists =RemoveStopWord(filterWordArray)
    lemmas = [lematizer.lemmatize(word.lower(), pos="v") for word in lists]
    notRepeatedWords = set(lemmas)
    return notRepeatedWords

# this function check if the given skill is present in the resume

def CheckSkills(LemmatizedWordList):
    requiredSkills = tech_skills
    checkedValue = [word for word in LemmatizedWordList if word in requiredSkills]
    return set(checkedValue)

# this give text pick out the date locations and name form the text 

def ExtractEntity(text):
    doc = nlp(text)

    extractedData =[]

    for entity in doc.ents:
        extractedData.append(
            {
                "label": entity.label,
                "text": entity.text
            }
        )
    return extractedData





     



    

        


