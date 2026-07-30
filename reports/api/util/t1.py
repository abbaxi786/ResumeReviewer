import os 
import pdfplumber
from docx import Document
from striprtf.striprtf import rtf_to_text
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import spacy
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


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

ROLE_KEYWORDS = {

    "python developer":[
        "python",
        "django",
        "flask",
        "fastapi",
        "sql",
        "postgresql",
        "mysql",
        "git",
        "docker",
        "aws",
        "linux",
        "rest api",
        "unit testing",
        "oop"
    ],

    "frontend developer":[
        "html",
        "css",
        "javascript",
        "typescript",
        "react",
        "nextjs",
        "redux",
        "tailwind",
        "git",
        "responsive design"
    ],

    "full stack developer":[
        "html",
        "css",
        "javascript",
        "react",
        "nextjs",
        "node",
        "express",
        "mongodb",
        "sql",
        "docker",
        "git",
        "aws",
        "rest api"
    ]
}

KEYWORDS = [
    "api",
    "rest",
    "agile",
    "testing",
    "deployment",
    "backend",
    "frontend",
    "database",
    "authentication",
    "authorization",
    "microservices",
    "cloud",
    "linux",
    "debugging",
    "oop",
    "design",
    "development",
    "web",
    "software",
    "team"
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

def RemoveExtraSpaceAndGiveNumberOfWordsAndChr(txt,requiredExperience,role,description):

    cleaned_text = re.sub(r'\s+', ' ', txt).strip()
    words = re.findall(r'\S+', cleaned_text)
    numberOfWords = len(words)
    without_spaces_text = re.sub(r'\s+', '', cleaned_text)
    NoOfChr = len(without_spaces_text)
    lematizedWords = WordLemmatizer(txt)
    GivenSkills = CheckSkills(lematizedWords)
    keywordMatch = CheckKeywords(lematizedWords)
    entityData = ExtractEntity(cleaned_text)
    experience = ExtractExperience(cleaned_text)
    ResumeScoresOverall = ScoringMatrics(GivenSkills,tech_skills,experience,requiredExperience,KEYWORDS,keywordMatch,description,cleaned_text)
    requiredSkills = ROLE_KEYWORDS.get(role)
    if requiredSkills is None:
        raise ValueError(f"Unknown role: {role}")

    skillScores = ScoringSkillMetrics(
        GivenSkills,
        requiredSkills
    )    

    return {"Text": cleaned_text, "Words": numberOfWords, "Characters": NoOfChr,"LematizedWords":lematizedWords,
            "PersonSkills":GivenSkills,"PersonData":entityData,"ResumeScores":ResumeScoresOverall,"SkillsRequiredScores": skillScores}

# this function uses the file and return output according to it extension 

def AssignAccordingToExt(file,requiredExperience,role,description):
     
    ext = GetExt(file)

    if ext == '.docx':
          return RemoveExtraSpaceAndGiveNumberOfWordsAndChr(FromDoc(file),requiredExperience,role,description)
    elif ext == ".pdf":
          return RemoveExtraSpaceAndGiveNumberOfWordsAndChr(FromPdf(file),requiredExperience,role,description)
    elif ext == ".txt":
          return RemoveExtraSpaceAndGiveNumberOfWordsAndChr(FromTxt(file),requiredExperience,role,description)
    elif ext == ".rtf":
          return RemoveExtraSpaceAndGiveNumberOfWordsAndChr(FromRTF(file),requiredExperience,role,description)
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

# this function is used for the keywords 

def CheckKeywords(LemmatizedWordList):
    keywords = KEYWORDS
    checkedValue = [word for word in LemmatizedWordList if word in keywords]
    return set(checkedValue)

# this give text pick out the date locations and name form the text 

def ExtractEntity(text):
    doc = nlp(text)

    extractedData =[]

    for entity in doc.ents:
        extractedData.append(
            {
                "label": entity.label_,
                "text": entity.text
            }
        )
    return extractedData


# ---------------------------The skills based functions --------------------------------------

def ScoringMatrics(
    foundSkills,
    totalSkills,
    candidateExperience,
    requiredExperience,
    totalKeywords,
    foundKeywords,
    description,
    resumeText,
):
    suggestion = None

    # Skills Score (30 Marks)
    skillScore = (
        min(len(foundSkills) / len(totalSkills), 1) * 30
        if totalSkills else 0
    )

    # Experience Score (40 Marks)
    experienceScore = (
        min(candidateExperience / requiredExperience, 1) * 40
        if requiredExperience else 0
    )

    # Keyword Score (30 Marks)
    keywordScore = (
        min(len(foundKeywords) / len(totalKeywords), 1) * 30
        if totalKeywords else 0
    )

    total = skillScore + experienceScore + keywordScore

    # Suggest experience if required
    if candidateExperience < requiredExperience:
        suggestion = {
            "ExperienceSuggestion": f"Required {requiredExperience - candidateExperience} more years of experience."
        }

    descriptionScores = DescriptionSetting(
        description,
        foundSkills,
        foundKeywords,
        resumeText,
    )

    return {
        "SkillScore": round(skillScore, 2),
        "ExperienceScore": round(experienceScore, 2),
        "KeywordScore": round(keywordScore, 2),
        "TotalResumeScore": round(total, 2),
        "Suggestion": suggestion,
        "DescriptionScores": descriptionScores
    }


def ScoringSkillMetrics(foundSkills,RequiredSkills):

     if RequiredSkills is None:
        raise ValueError("Unknown role supplied.")
     matchedSkills = [skill for skill in foundSkills if skill in RequiredSkills]
     NotmatchedSkills = [skill for skill in RequiredSkills if skill not in foundSkills]
     scores = min(len(matchedSkills)/len(RequiredSkills),1)*100 if RequiredSkills else 0
     MistSkillWithSuggestions = LoadingSuggestionAndCheckingMissingTeckSkills(NotmatchedSkills)
     return {"SkillScoresFromRequired": scores,"Match_Skills":matchedSkills,"Not_Matched_Skills":NotmatchedSkills,"MistSkillWithSuggestions":MistSkillWithSuggestions}



def ExtractExperience(text):

    pattern = r'(\d+)\s*\+?\s*(?:years?|yrs?)'
    matches = re.findall(pattern, text.lower())
    if not matches:
        return 0
    years = [int(year) for year in matches]
    return max(years)

def LoadingSuggestionAndCheckingMissingTeckSkills(techSkills):
    jsonValue = None
    skillList = []  # <--- FIX: Changed from {} to [] to make it a list
    
    with open("api/util/suggestion.json", 'r', encoding="utf-8") as file:
        jsonValue = json.load(file)

    for skill in techSkills:
        # Safely get suggestions from the "SUGGESTIONS" dictionary
        # If a skill isn't in your JSON, this returns None instead of crashing
        suggests = jsonValue.get("SUGGESTIONS", {}).get(skill)
        
        skillList.append({
            "Skill": skill,
            "Suggestions": suggests
        })
    
    return skillList


#   the description process functions 

def DescriptionSetting(txt, foundSkills, foundKeywords,resumeText):

    if txt is None or txt.strip() == "":
        return {
            "message": "Job description not provided."
        }

    lemmatizedWords = WordLemmatizer(txt)

    skillsFromDescription = CheckSkills(lemmatizedWords)
    keywordsFromDescription = CheckKeywords(lemmatizedWords)

    matchedSkillsWithDescription = [
        skill for skill in foundSkills
        if skill in skillsFromDescription
    ]

    matchedKeywordsWithDescription = [
        keyword for keyword in foundKeywords
        if keyword in keywordsFromDescription
    ]

    descriptionSkillScore = (
        len(matchedSkillsWithDescription) /
        len(skillsFromDescription) * 100
        if skillsFromDescription else 0
    )

    descriptionKeywordScore = (
        len(matchedKeywordsWithDescription) /
        len(keywordsFromDescription) * 100
        if keywordsFromDescription else 0
    )

    tfidfScore = TFIDFCosineSimilarity(
        resumeText,
        txt
    )

    return {
        "MatchedSkills": matchedSkillsWithDescription,
        "MissingSkills": [
            skill
            for skill in skillsFromDescription
            if skill not in foundSkills
        ],
        "MatchedKeywords": matchedKeywordsWithDescription,
        "skills_scores": round(descriptionSkillScore, 2),
        "keyword_scores": round(descriptionKeywordScore, 2),
        "TFIDF_Cosine_Score": tfidfScore
    }

# ---------------cosine similarity of description and resume--------------------------

def TFIDFCosineSimilarity(resumeText, jobDescription):

    if not resumeText or not jobDescription:
        return 0

    documents = [
        resumeText,
        jobDescription
    ]

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )

    score = float(similarity[0][0]) * 100

    return round(score, 2)




    


        

    





     



    

        


