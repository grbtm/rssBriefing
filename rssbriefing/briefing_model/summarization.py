import newspaper
from transformers import pipeline

COOKIE_RESPONSE = 'Cookies help us deliver our Services.'
SEARCH_RESPONSE = 'What term do you want to search?'


def get_summary(url, nlp):
    article = newspaper.Article(url)

    try:

        article.download()
        article.parse()

        text = article.text
        text = text.replace("\n", "")

        if len(nlp.tokenizer.tokenize(text)) > 1024:
            text = text[:4000]

        output = nlp(text, max_length=300, min_length=190)
        summary = output[0]['summary_text']

    except newspaper.article.ArticleException as a_err:

        print(f"Article exception: {a_err}")
        summary = None

    except ValueError as v_err:

        print(f"Value error: {v_err}")
        summary = None

    return summary


def enrich_with_summary(briefing_items):
    nlp = pipeline('summarization')

    for item in briefing_items:

        summary = get_summary(item.link, nlp)

        if not summary or summary.startswith((COOKIE_RESPONSE, SEARCH_RESPONSE)):
            item.summary = item.description
        else:
            item.summary = summary

    return briefing_items
