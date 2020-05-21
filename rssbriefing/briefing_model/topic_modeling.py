import os
import en_core_web_sm
import numpy as np
from gensim.corpora import Dictionary
from gensim.models import Phrases, LdaModel
from spacy.lang.en.stop_words import STOP_WORDS

from rssbriefing import create_app
from rssbriefing.briefing_model.configs import reference_feeds, stop_words, stop_words_to_remove, common_terms, \
    NUM_TOPICS, PASSES
from rssbriefing.briefing_model.ranking import get_candidates


module_path = os.path.abspath(os.path.dirname(__file__))


def collect_posts(app):
    """ Collect RSS and Atom posts from past 24h and store them in rssbriefing.models.Briefing data structure.

    :param app:
    :return: posts: [Lst[rssbriefing.models.Briefing]]
    """
    app.logger.info('Collecting posts from past 24h for topic modeling ... ')
    posts = get_candidates(app, user_id=1)

    posts = [candidate for candidate in posts if candidate.feed_title in reference_feeds]

    # Remove posts with Live updates, since these cover multiple topics and thus deviate from the average post
    posts = [candidate for candidate in posts if 'Live ' not in candidate.title]

    # Remove advertising posts for Bloomberg products
    posts = [candidate for candidate in posts if '(Source: Bloomberg)' not in candidate.description]

    app.logger.info(f'Successfully collected {len(posts)} posts.')
    return posts


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


def preprocess(app, posts):
    """ Preprocess documents and thus create corpus ready for model training.

    :param posts: [Lst[rssbriefing.models.Briefing]]
    :return:
    """
    app.logger.info('Preprocessing the collected posts ....')
    corpus = tokenize_and_lemmatize(posts)

    corpus = compute_bigrams(corpus)
    app.logger.info('Finished preprocessing.')

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


def train_model(app, bow_corpus, dictionary):
    """ Initialize and train LDA model. Since no iteration param supplied, it trains until topics converge.

    :param corpus:
    :param dictionary:
    :return:
    """
    app.logger.info(f'Training LDA model with {NUM_TOPICS} topics ...')
    temp = dictionary[0]  # Load dictionary into memory, necessary due to lazy evaluation

    model = LdaModel(
        corpus=bow_corpus,

        # id2word: mapping of id -> token/word
        id2word=dictionary.id2token,

        # alpha: Can be set to an 1D array of length equal to the number of expected topics
        # that expresses our a-priori belief for the each topics’ probability.
        # We initialize it with uniform distribution.
        alpha=np.full(shape=NUM_TOPICS, fill_value=(1 / NUM_TOPICS), dtype=np.float),

        # A-priori belief on word probability: the string ‘auto’ to learn the asymmetric prior from the data.
        eta='auto',

        num_topics=NUM_TOPICS,
        passes=PASSES
    )

    app.logger.info('Finished training.')
    return model


def show_model_stats(app, model, bow_corpus, corpus, dictionary):
    top_topics = model.top_topics(corpus=bow_corpus, texts=corpus, dictionary=dictionary, coherence='c_v')
    avg_topic_coherence = sum([t[1] for t in top_topics]) / NUM_TOPICS

    app.logger.info(f'Topic model training finished. Average topic coherence: {avg_topic_coherence}')
    app.logger.info(f'Top topics: {top_topics}')


def compute_topics(app):
    posts = collect_posts(app)

    corpus = preprocess(app, posts)

    dictionary = get_dictionary(corpus)

    bow_corpus = get_bow_representation(corpus, dictionary)

    model = train_model(app, bow_corpus, dictionary)

    #model.save(os.path.join(module_path, 'instance', 'LDA_model'))

    show_model_stats(app, model, bow_corpus, corpus, dictionary)

    return model


if __name__ == '__main__':
    # Set up app context to be able to access extensions such as SQLAlchemy when this module is run independently
    app = create_app()
    app.app_context().push()

    compute_topics(app)
