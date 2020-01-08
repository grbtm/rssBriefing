INSERT INTO user (username, email, password_hash)
VALUES
  ('test',
   'test@testdomain.com',
   'pbkdf2:sha256:150000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
  ('other',
   'other_email@domain.net',
   'pbkdf2:sha256:150000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');

--INSERT INTO feed (title, description, link, href)
--VALUES
--  ('Unique News Website', 'We are an unique website', 'www.news-website.com', 'www.news-website.com/feed.xml');
