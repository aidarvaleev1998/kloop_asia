import re
import sys

from bs4 import BeautifulSoup
from datetime import timedelta, datetime
from urllib.request import urlopen, Request

from Levenshtein.StringMatcher import StringMatcher


class PageIterator(object):
    def __init__(self, curr_date, link, n=1, articles=False):
        self.curr_page = n
        self.curr_date = curr_date
        self.link = link
        self.articles = articles
        self.cache = []
        self.cache = self.get_blocks()

    def get_blocks(self):
        user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46'
        url = self.link + str(self.curr_page)

        page = None
        while page is None:
            print(f"Curr_page: {url}")
            page = urlopen(Request(url, data=None, headers={'User-Agent': user_agent}))

        soup = BeautifulSoup(page, "html.parser")
        if self.articles:
            blocks = soup.find_all("article")
        else:
            blocks = soup.find_all("div", {"class": "td_module_1"})
        return blocks

    def tuple2date(self, tuple):
        _, page_link = tuple
        date = page_link[22:32].split('/')
        date = datetime(int(date[0]), int(date[1]), int(date[2]))
        return date

    def block2tuple(self, block):
        try:
            if self.articles:
                img_link = block.contents[1].contents[1].contents[0]["src"]
                page_link = block.contents[1]['href']
            else:
                img_link = block.contents[1].contents[1].contents[0].contents[0]['src']
                page_link = block.contents[1].contents[1].contents[0]['href']
            return img_link, page_link
        except:
            return None

    def get_next(self):
        if not self.cache:
            return []

        pages = list(filter(lambda p: p is not None, map(self.block2tuple, self.cache)))

        while pages and self.tuple2date(pages[-1]) >= self.curr_date:
            self.curr_page += 1
            self.cache = self.get_blocks()
            if not self.cache:
                break
            pages += list(filter(lambda p: p is not None, map(self.block2tuple, self.cache)))

        pages = [p for p in pages if self.tuple2date(p) == self.curr_date]

        self.curr_date -= timedelta(1)
        return pages


def get_match_score(phrase, words, min_distance=2):
    score = 0
    phrase_len = len(''.join(phrase))
    for p in phrase:
        matcher = StringMatcher(seq1=p)
        for w in words:
            matcher.set_seq2(w)
            match_distance = matcher.distance()
            if match_distance <= min_distance:
                score += max(0, len(p) - match_distance) / phrase_len
    return score


def tuple2matching_list(page):
    result = " " + page[0] + " "
    result = re.sub("[/.\\-_:]+", " ", result)
    result = re.sub("https|uz|kg|kloop|asia|wp|blog|content|uploads|sites", " ", result)
    result = re.sub("20[0-9]{2} [0-9]+ ", " ", result)
    result = re.sub(" [0-9]+x[0-9]+ ", " ", result)
    result = re.sub(" [0-9]+x[0-9]+ ", " ", result)
    result = re.sub(" [0-9] ", " ", result)
    result = re.sub("[ ]+", " ", result)
    result = re.split(" ", result.strip())
    return result


def find(ru_page, uz_pages):
    scores = []
    phrase = tuple2matching_list(ru_page)
    for uz_page in uz_pages:
        words = tuple2matching_list(uz_page)
        scores.append((get_match_score(phrase, words), uz_page))

    scores = sorted(scores, reverse=True)[:2]
    if (scores and scores[0][0] > 0.8) or \
            (len(scores) == 1 and scores[0][0] >= 0.5) or \
            (len(scores) == 2 and scores[0][0] >= 0.5 and scores[0][0] - scores[1][0] > 0.15):
        return scores[0][1]
    return None


def preprocess(ru, uz):
    ru_text, uz_text = ru[1], uz[1]
    return ru_text, uz_text


def main():
    n = 0

    line = sys.argv[1].split()
    print(line)

    curr_date = datetime.strptime(line[0], '%Y-%m-%d')
    ru_n = int(line[1]) + 1
    uz_n = int(line[2])

    ru_iterator = PageIterator(curr_date, "http://kloop.kg/news/", n=ru_n, articles=True)
    uz_iterator = PageIterator(curr_date, "http://uz.kloop.asia/category/habarlar/page/", n=uz_n)

    uz_prev = []
    uz_curr = uz_iterator.get_next()

    end_date = datetime(2014, 12, 24)
    while curr_date > end_date:
        ru_curr = ru_iterator.get_next()
        uz_next = uz_iterator.get_next()

        for ru_page in ru_curr:
            uz_page = find(ru_page, uz_prev + uz_curr + uz_next)
            if uz_page is not None:
                n += 1
                ru_page, uz_page = preprocess(ru_page, uz_page)
                with open("kloop.ru.txt", "a", encoding="utf-8") as f:
                    f.write(ru_page + "\n")
                with open("kloop.uz.txt", "a", encoding="utf-8") as f:
                    f.write(uz_page + "\n")

        uz_prev = uz_curr
        uz_curr = uz_next
        with open("log.txt", "w", encoding="utf-8") as f:
            f.write(f'{curr_date.date()} {ru_iterator.curr_page} {uz_iterator.curr_page - 3}\n')
        print(curr_date, f'n={n}')
        curr_date -= timedelta(1)

    with open("log.txt", "w", encoding="utf-8") as f:
        f.write('finish\n')


# main()


# with open("kloop.ru.txt", "r", encoding="utf-8") as f:
#     ru_lines = f.readlines()
#
# with open("kloop.uz.txt", "r", encoding="utf-8") as f:
#     uz_lines = f.readlines()
#
#
# data = set(zip(ru_lines, uz_lines))
# ru_lines, uz_lines = map(list, zip(*data))
#
# with open("kloop.ru.deduped.txt", "w", encoding="utf-8") as f:
#     for l in ru_lines:
#         f.write(l)
#
# with open("kloop.uz.deduped.txt", "w", encoding="utf-8") as f:
#     for l in uz_lines:
#         f.write(l)
