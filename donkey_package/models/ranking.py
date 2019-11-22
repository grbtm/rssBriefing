import time
import collections

from gensim.models import Word2Vec, WordEmbeddingSimilarityIndex
from gensim.similarities import SoftCosineSimilarity, SparseTermSimilarityMatrix

from donkey_package.db import get_db, get_id_feedtitle_lookup_dict

MODEL_PATH = ''


class FeedItem(object):

    def __init__(self, idx_id, feed_id, feed_name, title, description, link, created, guid):
        self.idx_id = idx_id
        self.feed_id = feed_id
        self.feed_name = feed_name
        self.title = title
        self.description = description
        self.link = link
        self.created = created
        self.guid = guid
        self.reference = None
        self.score = 0


def load_model(path):
    model = Word2Vec.load(path)
    return model


def calculate_similarity_index(corpus, dictionary):
    """ Use pre-trained Word2Vec model for word embeddings. Calculate similarities based on Soft Cosine Measure.

    References
        Grigori Sidorov et al.
        Soft Similarity and Soft Cosine Measure: Similarity of Features in Vector Space Model, 2014.

        Delphine Charlet and Geraldine Damnati, SimBow at SemEval-2017 Task 3:
        Soft-Cosine Semantic Similarity between Questions for Community Question Answering, 2017.

        Gensim notebook on: Finding similar documents with Word2Vec and Soft Cosine Measure
        https://github.com/RaRe-Technologies/gensim/blob/develop/docs/notebooks/soft_cosine_tutorial.ipynb

    :return: [numpy.ndarray] similarity index matrix, stored in memory
    """

    # Load pre-trained Word2Vec model
    model = load_model(MODEL_PATH)

    # Construct the WordEmbeddingSimilarityIndex model based on cosine similarities between word embeddings
    similarity_index = WordEmbeddingSimilarityIndex(model.wv)

    # Construct similarity matrix
    similarity_matrix = SparseTermSimilarityMatrix(similarity_index, dictionary)

    # Convert the corpus into the bag-of-words vector representation
    bow_corpus = [dictionary.doc2bow(document) for document in corpus]

    # Build the similarity index for corpus-based queries
    docsim_index = SoftCosineSimilarity(bow_corpus, similarity_matrix, num_best=10)

    return docsim_index


def get_candidates():
    db = get_db()

    timestamp_24h_ago = time.time() - 86400

    candidates = db.execute(f"SELECT * FROM item WHERE created > {timestamp_24h_ago}").fetchall()

    feedtitle_lookup = get_id_feedtitle_lookup_dict()

    candidates = [FeedItem(idx_id=candidate['id'],
                           feed_id=candidate['feed_id'],
                           feed_name=feedtitle_lookup[candidate['feed_id']],
                           title=candidate['title'],
                           description=candidate['description'],
                           link=candidate['link'],
                           created=candidate['created'],
                           guid=candidate['guid']) for candidate in candidates]

    return candidates


def query_most_similar_reference(feeditem, docsim, dictionary):
    query = feeditem.title + ' ' + feeditem.description
    query = dictionary.doc2bow(query)

    similarities = docsim[query]
    similarities = sorted(similarities, key=lambda tupl: tupl[1], reverse=True)

    top_ranked = similarities[0]

    corpus_reference = top_ranked[0]
    feeditem.reference = corpus_reference

    score = top_ranked[1]
    feeditem.score = score


def rank_candidates(candidates, docsim, dictionary):

    # Enrich candidates with most similar reference and respective similarity score
    for candidate in candidates:
        query_most_similar_reference(candidate, docsim, dictionary)

    # Check for candidates with same reference
    references = [candidate.reference for candidate in candidates]
    multiple_assignments = [item for item, count in collections.Counter(references).items() if count > 1]

    # If multiple candidates with same similarity reference only consider the candidate with highest score
    if multiple_assignments:
        for reference in multiple_assignments:

            same_ref_candidates = [candidate for candidate in candidates if candidate.reference == reference]
            same_ref_candidates = sorted(same_ref_candidates, key=lambda cand:cand.score, reverse=True)

            # Reset the reference for all candidates except for the one with the highest score
            for candidate in same_ref_candidates[1:]:
                candidate.reference = None

        candidates = [candidate for candidate in candidates if candidate.reference is not None]

    return candidates


