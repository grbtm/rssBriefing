import en_core_web_sm
from spacy.lang.en.stop_words import STOP_WORDS

from gensim.models import Phrases
from gensim.corpora import Dictionary

from rssbriefing.briefing_model.ranking import get_candidates
from rssbriefing.briefing_model.data_structures import TopicModel
from rssbriefing.briefing_model.configs import reference_feeds, stop_words, common_terms


def collect_posts(app):
    """ Collect RSS and Atom posts from past 24h and store them in rssbriefing.models.Briefing data structure.

    :param app:
    :return: posts: [Lst[rssbriefing.models.Briefing]]
    """
    posts = get_candidates(app, user_id=1)

    posts = [candidate for candidate in posts if candidate.feed_title in reference_feeds]

    # Remove posts with Live updates, since these cover multiple topics and thus deviate from the average post
    posts = [candidate for candidate in posts if 'Live' not in candidate.title]

    # Remove advertising posts for Bloomberg products
    posts = [candidate for candidate in posts if '(Source: Bloomberg)' not in candidate.description]

    app.logger.info(f'Fetched {len(posts)} posts for subsequent topic modeling.')
    return posts


def load_language_model():
    nlp = en_core_web_sm.load()
    nlp.Defaults.stop_words.update(stop_words)

    for word in STOP_WORDS:
        lexeme = nlp.vocab[word]
        lexeme.is_stop = True

    return nlp


def preprocess_document(post, nlp):
    """

    :param post:
    :param nlp:
    :return:
    """

    doc = post.title + ' ' + post.description

    doc = doc.lower()

    doc = nlp(doc)

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
    bigram = Phrases(corpus,
                     min_count=5,   # Ignore all words and bigrams with total collected count lower than this value.
                     common_terms=common_terms) # List of stop words that won’t affect frequency count of expressions containing them.

    for idx in range(len(corpus)):
        for token in bigram[corpus[idx]]:
            if '_' in token:
                # Token is a bigram, add to document.
                corpus[idx].append(token)

    return corpus


def preprocess(posts):
    """

    :param posts: [Lst[rssbriefing.models.Briefing]]
    :return:
    """
    corpus = tokenize_and_lemmatize(posts)

    corpus = compute_bigrams(corpus)

    return corpus


def get_dictionary(corpus):
    """ Construct a mapping between words/tokens and their respective integer ids - with gensim's Dictionary class

    :param corpus:
    :return:
    """
    dictionary = Dictionary(corpus)

    # Filter out words that occur less than 4 documents, or more than 60% of the documents.
    dictionary.filter_extremes(no_below=4, no_above=0.6)

    return dictionary


def get_bow_representation(corpus, dictionary):
    bow_corpus = [dictionary.doc2bow(doc) for doc in corpus]
    return bow_corpus


def compute_topics(app):
    posts = collect_posts(app)

    corpus = preprocess(posts)

    dictionary = get_dictionary(corpus)

    bow_corpus = get_bow_representation(corpus, dictionary)

    model = TopicModel()

    model.save(MODEL_PATH)

    return model
