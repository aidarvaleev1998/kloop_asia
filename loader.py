import re
import sys
import urllib.parse
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request


def remove_tags(i, div):
    text = str(div)
    text = re.sub('</p>|</div>|</li>|<br/>|<br>|<hr/>|<hr>', '\n', text)
    text = re.sub('<p>|<p [^>]*>|<div[^>]*>|<li>|<li [^>]*>|<a>|<a [^>]*>|</a>|<span[^>]*>|</span>|<time[^>]*>|</time>|'
                  '<nobr[^>]*>|</nobr>|<img[^>]*>|<em[^>]*>|</em>|<tr[^>]*>|<td[^>]*>|</tr>|</td>|</tbody>|<tbody>|'
                  '<strong[^>]*>|</strong>|<ul[^>]*>|</ul>|<u>|</u>|<ol[^>]*>|</ol>|<h[1-6][^>]*>|</h[1-6]>|'
                  '<blockquote[^>]*>|</blockquote>|<wbr/>|<wbr>|<sub>|</sub>|<sup>|</sup>|<thead>|</thead>|\t|\r|'
                  '<i>|<i [^>]*>|</i>|<del>|<del [^>]*>|</del>|<b>|<b [^>]*>|</b>|<font[^>]*>|</font>|'
                  '<col[^>]*>|<center>|</center>|<colgroup[^>]*>|</colgroup>|<pre>|</pre>|</video>', '', text)
    text = re.sub('<script[^<]*</script>|<table[^<]*</table>|<figure[^<]*</figure>|<figcaption[^<]*</figcaption>|'
                  '<button[^<]*</button>|<noscript[^<]*</noscript>|<video[^>]*>|<source[^>]*>|'
                  '<metricconverter[^<]*</metricconverter>|<u[^>]*>|<style[^<]*</style>|'
                  '<twitterwidget[^<]*</twitterwidget>', '\n', text)
    text = re.sub('<iframe[^<]*</iframe>|<figure[^<]*</figure>|<![^<]*>', '\n', text)
    temp = re.findall('<[^>]*>', text)
    if temp:
        print(i, temp)
    text = re.sub('<[^>]*>', '', text)
    text = re.sub('\n\n+', '\n', text)
    return text.strip()


def remove_comments(div):
    text = [str(d) for d in div.contents if '<div class="fb-comments"' not in str(d)]
    text = '\n'.join(text)
    return text


def download_text(i, link):
    user_agent = 'Google Chrome 53 (Win 10 x64): Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'
    page = urlopen(Request(to_ascii(link), data=None, headers={
        'User-Agent': user_agent,
        "Accept": "text/html",
        "Connection": "keep - alive"
    }))
    soup = BeautifulSoup(page, "html.parser", from_encoding="utf-8")
    div = soup.find(id="wtr-content")
    div = remove_comments(div)
    text = remove_tags(i, div)
    return text


def to_ascii(link):
    link = list(urllib.parse.urlsplit(link.strip()))
    link[2] = urllib.parse.quote(link[2])
    link = urllib.parse.urlunsplit(link)
    return link


def download_all(ext, start):
    with open(f"kloop.{ext}.deduped.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        end = 216
        for i, link in enumerate(lines[start:end]):
            with open("log2.txt", "w", encoding="utf-8") as f:
                f.write(f'{start + i}\n')

            text = download_text(start + i, link)
            with open(f"data/{start + i}.{ext}", "w", encoding="utf-8") as g:
                g.write(text)
    with open("log2.txt", "w", encoding="utf-8") as f:
        f.write(f'10000\n')


# download_all("uz", 0)
n = int(sys.argv[1])
print(n)
download_all("ru", n)
