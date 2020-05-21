"""
    Module with functions for preprocessing

"""
import en_core_web_sm
from spacy.lang.en.stop_words import STOP_WORDS
from gensim.models import Phrases
from gensim.utils import tokenize
from nltk.corpus import stopwords

from rssbriefing.briefing_model.configs import stop_words, stop_words_to_remove, common_terms


def preprocess(doc, encoding='utf8'):
    """ Prepare a document for either model training or prediction by tokenizing and applying further filters. """

    doc = list(tokenize(doc,
                        lowercase=True,
                        deacc=True,  # Remove accentuation
                        encoding=encoding))

    commonlist = stopwords.words('english')

    doc = [word for word in doc if word not in commonlist]  # remove common words
    doc = [word for word in doc if word.isalpha()]  # remove numbers and special characters

    return doc


def load_language_model():
    nlp = en_core_web_sm.load()

    # Update stop words according to custom use case
    nlp.Defaults.stop_words.update(stop_words)
    for word in stop_words_to_remove:
        nlp.Defaults.stop_words.remove(word)

    for word in STOP_WORDS:
        lexeme = nlp.vocab[word]
        lexeme.is_stop = True

    return nlp


# def entity_recognition(doc):
#     full_string = doc.text
#     for entity in doc.ents:
#
#     return doc

def preprocess_document(post, nlp):
    """ Perform preprocessing on a single document.

    Preprocessing covers:
        - Normalization: lowering all string

        - Tokenization
        - Lemmatization
        - custom filtering

    :param post:
    :param nlp:
    :return:
    """

    doc = post.title + ' ' + post.description

    doc = doc.lower()

    doc = nlp(doc)

    # doc = entity_recognition(doc)

    doc = [word.lemma_ for word in doc
           if word.text != '\n' and
           word.text != '\n ' and
           word.text != '\n\n' and
           word.lemma_ not in STOP_WORDS and  # compare lemmatized string against stopwords list
           not word.is_punct and
           word.lemma_ != '-PRON-' and
           not word.like_num]

    # Custom filter for some RSS posts
    if doc[-2] == 'continue' and doc[-1] == 'reading':
        doc = doc[:-2]

    return doc


def tokenize_and_lemmatize(posts):
    nlp = load_language_model()

    corpus = [preprocess_document(post, nlp) for post in posts]

    return corpus


def compute_bigrams(corpus):
    """ Enrich documents (consisting of list of tokens) with composite tokens of bigrams such as "new_york".

    :param corpus: [Lst[Lst[str]]]
    :return: corpus: [Lst[Lst[str]]]
    """
    bigram = Phrases(corpus,
                     min_count=5,  # Ignore all words and bigrams with total collected count lower than this value.
                     common_terms=common_terms)  # List of stop words that won’t affect frequency count of expressions containing them.

    for idx in range(len(corpus)):
        for token in bigram[corpus[idx]]:
            if '_' in token:
                # Token is a bigram, add to document.
                corpus[idx].append(token)

    return corpus
