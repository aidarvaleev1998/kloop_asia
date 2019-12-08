import glob
from nltk.tokenize import sent_tokenize

for file in glob.glob('data/*'):
    with open('embed/' + file[5:], 'a', encoding="utf-8") as g:
        with open(file, 'r', encoding="utf-8") as f:
            text = "".join(f.readlines())
            sentences = sent_tokenize(text)
            if len(sentences) > 1:
                i = 0
                while i < len(sentences) - 1:
                    if len(sentences[i]) < 25 or len(sentences[i + 1]) < 25:
                        sentences[i] += sentences[i + 1]
                        sentences.pop(i + 1)
                        i -= 1
                    i += 1
            for i, s in enumerate(sentences):
                if len(s) > 10:
                    g.write(s.strip() + "\n")
