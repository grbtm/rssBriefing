"""
Requirements:

Briefing

    reference/corpus collection

    similarity score calculation
        - score is always wrt to a given corpus, which is relevant only for a given time until the next corpus update
            -> therefore score inherent to corpus and not property of feed item to which the score is assigned to
            -> score should be saved with Briefing object -> Briefing db table, not feed items

        many to many:
            ref1               ref2
            / | \              / | \

           /  |  \           /   |  \

        A     B    C        A    B    C
        0.9   0.2  0.9      0.0  0.9  0.8

        -> briefing ranking w threshold e.g. 0.7:
            A
            C
            B
            C

        -> consider multiple posts (A, B, C) covering same topic (ref1, ref2):
            - additional criteria (e.g. highest similarity score) needed to filter:
                A for ref1
                B for ref2

    view/write to db

    assumption now: briefing calculation to be run once per day, but potentially more often

Entry

    similarity score wrt ref

    attributes as given from db


"""
from gensim.corpora import Dictionary
from nltk import word_tokenize
from nltk.corpus import stopwords

from donkey_package.models.ranking import calculate_similarity_index


def preprocess(doc):
    doc = doc.split(' - ', 1)[0]  # remove news source at end of each headline from NEWS API
    doc = doc.lower()
    doc = word_tokenize(doc)

    commonlist = stopwords.words('english')

    doc = [word for word in doc if word not in commonlist]  # remove common words
    doc = [word for word in doc if word.isalpha()]  # remove numbers and special characters
    return doc


def get_reference_documents():
    """ Collect the reference topics for the current Briefing.

    Documents are Strings containing a whole text and represent the gensim objects that make up a corpus.

    :return:
    """

    documents = ''

    return documents


def get_corpus_dictionary(corpus):
    """ Wrapper for gensim Dictionary function.

    From gensim docs: Dictionary encapsulates the mapping between normalized words and their integer ids.

    :return: [gensim.corpora.Dictionary]
    """

    dictionary = Dictionary(corpus)

    return dictionary


def get_reference_corpus(self):
    """ Load the current corpus.

    Since the corpus is relatively small it can be loaded fully into memory.

    :return: [Lst[Str]] List of Strings containing the preprocessed text bodies
    """

    corpus = [preprocess(doc) for doc in get_reference_documents()]
    return corpus


def save_to_db(self):
    """ Save given corpus and respective feed item selection to db.

    :return:
    """


def generate_briefing():

    corpus = get_reference_corpus()

    dictionary = get_corpus_dictionary(corpus)

    docsim = calculate_similarity_index(corpus, dictionary)

    candidates = get_candidates()

    selected = rank_candidates(candidates, docsim, dictionary)

    save_to_db(selected)

