import time
import collections

from donkey_package.db import get_db, get_id_feedtitle_lookup_dict
from donkey_package.models.entry import FeedItem


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

    # If multiple candidates with same similarity reference exist, keep only the candidate with highest score
    if multiple_assignments:
        for reference in multiple_assignments:

            same_ref_candidates = [candidate for candidate in candidates if candidate.reference == reference]
            same_ref_candidates = sorted(same_ref_candidates, key=lambda cand:cand.score, reverse=True)

            # Reset the reference for all candidates except for the one with the highest score
            for candidate in same_ref_candidates[1:]:
                candidate.reference = None

        candidates = [candidate for candidate in candidates if candidate.reference is not None]

    # Remove candidates with a similarity score below the threshold
    candidates = [candidate for candidate in candidates if candidate.score > 0.9]

    return candidates


