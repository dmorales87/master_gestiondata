
import unidecode
import spacy
import re
import sklearn
import nltk
from nltk.corpus import stopwords
from nltk.tokenize.casual import TweetTokenizer

class TextNormalizer(sklearn.base.BaseEstimator, sklearn.base.TransformerMixin):
    def __init__(self, language='spanish', lemmatize=True, stem=False, reduce_len=True, strip_handles=True, strip_stopwords=True, strip_urls=True, strip_accents=True, token_min_len=-1, preserve_case=True, text_to_sequence=False):
        """Un normalizador de texto pensado para procesamiento de Tweets en español. Este normalizador puede devolver o bien un texto transformado o bien una secuencia de tokens si se
        indica el parametro `text_to_sequence`. Dentro de los procesamientos disponibles son lemmatization, stemming, reducir la longitud de caracteres repetidos, eliminar handles, 
        eliminar URLs, eliminar mayusculas."""
        
        self.tokenizer = TweetTokenizer(strip_handles=strip_handles, 
                                        reduce_len=reduce_len,
                                        preserve_case=preserve_case) # Creamos un tokenizer
        if stem:
            self.stemmer = nltk.stem.SnowballStemmer(language=language) # Creamos un steammer
        else:
            self.stemmer = False
        
        if lemmatize:
            try:
                import es_core_news_sm as spa
            
                self.parser = spa.load() # Cargamos el parser en español
            except ImportError:
                raise ImportError('El modelo en español no está instalado. Ejecute python -m spacy download en_core_web_sm')
            self.lemmatizer = lambda word : " ".join([token.lemma_ for token in self.parser(word)]) # Creamos un lemmatizer
        else:
            self.lemmatizer = False
        
        if strip_stopwords:
            nltk.download("stopwords", quiet=True)
            self.stopwords = set(stopwords.words(language)) # Instanciamos las stopwords en español
        
        self.strip_stopwords = strip_stopwords
        self.strip_accents = strip_accents
        self.strip_urls = strip_urls
        self.urls_regex = re.compile('http\S+') # Usamos una expresion regular para encontrar las URLs
        self.token_min_len = token_min_len
        self._text_to_sequence = text_to_sequence
    
    def process_text(self, text):
        """Procesa una secuencia de texto de acuerdo a la configuración del normalizador. Este método
        devuelve una secuencia de tokens."""
        tokens = self.tokenizer.tokenize(text)

        if self.strip_urls:
            tokens = [token for token in tokens if not re.match(self.urls_regex, token)]
        if self.token_min_len > 1:
            tokens = [token for token in tokens if len(token) > self.token_min_len]
        if self.strip_accents:
            tokens = [unidecode.unidecode(token) for token in tokens]
        if self.strip_stopwords:
            tokens = [token for token in tokens if token not in self.stopwords]
        if self.lemmatizer:
            tokens = [self.lemmatizer(token) for token in tokens]
        if self.stemmer:
            tokens = [self.stemmer.stem(token) for token in tokens]
        return tokens
    
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        if self._text_to_sequence:
            for doc in X:
                yield self.process_text(text=doc)
        else:
            for doc in X:
                yield ' '.join(self.process_text(text=doc))
