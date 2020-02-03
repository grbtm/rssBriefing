import newspaper
from gensim.summarization import summarize


COOKIE_RESPONSE = 'Cookies help us deliver our Services.'
SEARCH_RESPONSE = 'What term do you want to search?'


def get_summary(url):
    article = newspaper.Article(url)

    try:

        article.download()
        article.parse()

        text = article.text
        summary = summarize(text, word_count=150)

    except newspaper.article.ArticleException as a_err:

        print(f"Article exception: {a_err}")
        summary = None

    return summary


def enrich_with_summary(briefing_items):

    for item in briefing_items:

        summary = get_summary(item.link)

        if not summary or summary.startswith((COOKIE_RESPONSE, SEARCH_RESPONSE)):
            item.summary = item.description
        else:
            item.summary = summary

    return briefing_items
