from rssbriefing.models import Users, Feed


seed_feeds = [
    {"title": "BBC News - Home", "href": "http://feeds.bbci.co.uk/news/rss.xml"},
    {"title": "NYT > Top Stories", "href": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"},
    {"title": "NYT > World News", "href": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"},
    {"title": "NYT > Business > Economy", "href": "https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml"},
    {"title": "Reuters: Top News", "href": "http://feeds.reuters.com/reuters/topNews"},
    {"title": "Reuters: Business News", "href": "http://feeds.reuters.com/reuters/businessNews"},
    {"title": "International homepage", "href": "https://www.ft.com/?format=rss"},
    {"title": "Fortune", "href": "https://fortune.com/feed"},
    {"title": "Top News and Analysis (pro)", "href": "http://www.cnbc.com/id/19746125/device/rss/rss.xml"},
    {"title": "U.S. News", "href": "https://www.cnbc.com/id/15837362/device/rss/rss.html"},
    {"title": "WSJ.com: World News", "href": "https://feeds.a.dj.com/rss/RSSWorldNews.xml"},
    {"title": "Economy", "href": "https://rss.politico.com/economy.xml"},
    {"title": "Al Jazeera English", "href": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"title": "CNN.com - RSS Channel - Politics", "href": "http://rss.cnn.com/rss/cnn_allpolitics.rss"},
    {"title": "International", "href": "https://www.economist.com/international/rss.xml"},
    {"title": "Business", "href": "https://www.economist.com/business/rss.xml"},
    {"title": "Bloomberg Politics", "href": "https://feeds.bloomberg.com/politics/news.rss"},
    {"title": "Bloomberg.com", "href": "https://feeds.bloomberg.com/business/news.rss"},
    {"title": "World & Nation", "href": "https://www.latimes.com/world-nation/rss2.0.xml"},
    {"title": "World", "href": "http://feeds.washingtonpost.com/rss/world"},
    {"title": "DER SPIEGEL - International", "href": "https://www.spiegel.de/international/index.rss"},
    {"title": "CBC | World News", "href": "https://rss.cbc.ca/lineup/world.xml"},
    {"title": "The Independent - World", "href": "https://www.independent.co.uk/news/world/rss"},
    {"title": "World News - Breaking News, Top Stories", "href": "https://www.huffpost.com/section/world-news/feed"},
    {"title": "Deutsche Welle", "href": "https://rss.dw.com/atom/rss-en-all"},
    {"title": "The Globe and Mail - World", "href": "https://theglobeandmail.com/rss/section/world/"}

]


def get_user_by_id(user_id):
    return Users.query.get(user_id)


def get_user_by_username(username):
    found = Users.query.filter_by(username=username).first()

    return found


def get_feedlist_for_dropdown(user_id):
    feeds = Feed.query.filter(Feed.users.any(Users.id == user_id)).all()

    return feeds


def get_all_users():
    return Users.query.all()


def get_user_by_email(email):
    return Users.query.filter_by(email=email).first()
