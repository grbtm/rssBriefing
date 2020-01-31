from newspaper import Article

cookie_message = 'Cookies help us deliver our Services.'


def get_summary(url):
    article = Article(url)

    article.download()
    article.parse()
    article.nlp()

    summary = article.summary

    return summary


def enrich_with_summary(briefing_items):
    for item in briefing_items:

        summary = get_summary(item.link)

        if not summary or summary.startswith(cookie_message):
            item.summary = item.description
        else:
            item.summary = summary

    return briefing_items
