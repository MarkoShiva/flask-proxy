import re

from bs4 import Tag, NavigableString, BeautifulSoup
def replace_words(soup):
    phrase = "WARP!"
    exp = re.compile(r"\b\w{5}\b")
    if soup.find('body'):
        page = soup.body.find_all(text = exp)
        for i, line in enumerate(page):
            if not re.match(r"^(?![http+|href])[[a-zA-Z0-9'\"]+", line):
                continue
            elif not isinstance(line, NavigableString):
                continue
            words = re.findall(exp, line)



            print("="*25)
            print(line)
            print()
            print(words)
            print()
            words = re.sub(exp, phrase, line)
            # for word in words:
                # replaced_word = line.replace(word, "WARP!")
            # line.replace_with(replaced_word)
            line.replace_with(words)
        print(soup.text.count(phrase))
    return soup

