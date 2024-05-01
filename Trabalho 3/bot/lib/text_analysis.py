from errors import AnalysisError

def get_search_term(terms : list):
    raise AnalysisError("get_search_term")

def get_search_things(terms : list):
    raise AnalysisError("get_search_things")

def get_sentiment_analysis(sentences : list):
    raise AnalysisError("get_sentiment_analysis")

avaiable_analysis_functions = {
    "get_search_term": get_search_term,
    "get_search_things": get_search_things,
    "get_sentiment_analysis": get_sentiment_analysis,    
}