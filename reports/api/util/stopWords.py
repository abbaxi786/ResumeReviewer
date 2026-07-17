from t1 import CleanTokens
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

stop_words = set(stopwords.words("english"))

def RemoveStopWord(text):
    lists = CleanTokens(text)
    filter_words_list = [word for word in lists if word.lower() not in stop_words]
    return filter_words_list

def WordLemmatizer(filterWordArray):
    lematizer = WordNetLemmatizer()
    lists =RemoveStopWord(filterWordArray)
    lemmas = [lematizer.lemmatize(word, pos="v") for word in lists]
    return lemmas

