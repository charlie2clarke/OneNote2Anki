from bs4 import BeautifulSoup
from typing import List


class Definition:
    def __init__(self, subject: str, definition: str):
        self.subject = subject
        self.definition = definition


class OneNoteParser:
    def __init__(self, html: str) -> None:
        self.html_doc = html
        self.soup = BeautifulSoup(html, "html.parser")

    def get_title(self) -> str:
        return self.soup.title.string

    # returns a dict with the word as the key and the definition as value.
    def get_definitions_by_bold_text(self) -> List[Definition]:
        definitions = []
        # get all span elements with a style = "font-weight:bold"
        for bold_text in self.soup.find_all("span", style="font-weight:bold"):
            # make each bold text the key to definitions and the rest of the text the value
            definitions.append(Definition(subject=bold_text.string, definition=bold_text.next_sibling.string))
        return definitions
