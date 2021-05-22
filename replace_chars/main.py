import re

from bs4 import Tag, NavigableString, BeautifulSoup
def replace_words(soup: BeautifulSoup, phrase: str = None, wl: int = 5, regex: re = None ):
    if not phrase:
        phrase = "WARP!"
    if regex:
        exp = regex
    else:
        regex = fr"\b\w{{{wl}}}\b"
    exp = re.compile(regex) # we are replacing any kind of word that is 5 char long. that include numbers.
    if soup.find('body'):       # limit to body
        page = soup.body.find_all(text = exp) # find all text that matches word len.
        for line in page:
            if not re.match(r"^(?!http+)[[a-zA-Z0-9'\"]+", line):
                # refuse renaming links in text and make sure we are not renaming links
                continue
            elif isinstance(line, NavigableString):
                # only rename strings that are in text not sometime inlined script tags.
                # words = re.findall(exp, line)  # this was debugging


                # we are doing a faster replace with re.
                words = re.sub(exp, phrase, line)
                # can be used in case of needed to do nested check replace
                # for word in words:
                    # replaced_word = line.replace(word, "WARP!")
                # line.replace_with(replaced_word)
                line.replace_with(words)
        print(soup.text.count(phrase))
    return soup

