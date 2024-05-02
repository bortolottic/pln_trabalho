from .errors import AnalysisError

def get_search_term(terms : list):
    return f"get_search_term = {','.join(terms)}"

def get_search_things(things : list):
    return f"get_search_things = {','.join(things)}"

def get_sentiment_analysis(sentences : list):
    return f"get_sentiment_analysis = {','.join(sentences)}"

avaiable_analysis_functions = {
    "get_search_term": get_search_term,
    "get_search_things": get_search_things,
    "get_sentiment_analysis": get_sentiment_analysis,    
}