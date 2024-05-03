from .errors import AnalysisError
import pickle as pkl
import nltk
import string
import json

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from LeIA import SentimentIntensityAnalyzer

nltk.download('wordnet')
nltk.download('punkt')
nltk.download('stopwords')

def load_dataset():
    with open('./bot/data/dataset.pkl', '+rb') as file:
        r = pkl.load(file)
    return r

dataset = load_dataset()

transcription_sentences = nltk.sent_tokenize(dataset.get("text_formatted"))
wnlemmatizer = nltk.stem.WordNetLemmatizer()
punctuation_removal = dict((ord(punctuation), None) for punctuation in string.punctuation)
stopwords = nltk.corpus.stopwords.words('portuguese')
s = SentimentIntensityAnalyzer()

def perform_lemmatization(tokens):
    return [wnlemmatizer.lemmatize(token) for token in tokens]

def get_processed_text(document):
    return perform_lemmatization(nltk.word_tokenize(document.lower().translate(punctuation_removal)))

def generate_response(user_input):
    robo_response = ''
    transcription_sentences.append(user_input)

    word_vectorizer = TfidfVectorizer(tokenizer=get_processed_text, stop_words=stopwords)
    all_word_vectors = word_vectorizer.fit_transform(transcription_sentences)
    similar_vector_values = cosine_similarity(all_word_vectors[-1], all_word_vectors)
    similar_sentence_number = similar_vector_values.argsort()[0][-2]

    matched_vector = similar_vector_values.flatten()
    matched_vector.sort()
    vector_matched = matched_vector[-2]

    if vector_matched != 0:
        robo_response = transcription_sentences[similar_sentence_number]

    return robo_response

def get_search_term(terms : list):
    sentences = []
    if terms and len(terms) > 0:
        for term in terms:
            sentences.append(generate_response(term))
    if len(sentences) == 0:
        sentences.append("<NOT_FOUND>")
    return '\n'.join(sentences)

def get_sentiment_analysis(sentence : str):
    return json.dumps(s.polarity_scores(sentence))

avaiable_analysis_functions = {
    "get_search_term": get_search_term,
    "get_sentiment_analysis": get_sentiment_analysis,    
}