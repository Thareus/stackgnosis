import re

def format_entry(text: str) -> str:
    """
    Cleans and formats the given text to conform to the Entry model
    """
    # Links
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2" _blank>\1</a>', text)
    # Bold
    text = re.sub(r"((- )?\*{2})(.*?)(\*{2})", r"<strong>\3</strong>", text)
    # Condense
    text = re.sub("\n\n", "\n", text)
    # Beginning
    text = text.strip()
    text = re.sub("(.*?)(<h3>)", r"\2", text, 1)
    # Headers
    text = re.sub("(^|\s+)##\s*(\d+\.)?\s*(.*?)\n", r"<h3>\3</h3>", text)
    # Body
    text = re.sub("(</h3>)(.*?)(<h3>)", r"\1<p>\2</p>\3", text)
    text = re.sub("\n+(- )?", r"<br>", text) # duplicate newlines
    text = re.sub("(>)\s*-\s*(<)", r"\1\2", text) # exposed dashes
    text = re.sub("(<br>){2,}", r"<br>", text) # duplicate line breaks
    text = re.sub("<p>(<br>)?</p>", r"", text) # empty paragraphs
    return text