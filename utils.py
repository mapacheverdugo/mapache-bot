from babel.numbers import format_currency as _format_currency


def format_currency(value):
    text = _format_currency(value, 'CLP', locale='es_CL')
    return text

def escape_markdown_v2(str):
    str = str.replace("!", "\\!")
    str = str.replace("_", "\\_")
    str = str.replace("*", "\\*")
    str = str.replace("[", "\\[")
    str = str.replace("]", "\\]")
    str = str.replace("`", "\\`")
    str = str.replace("(", "\\(")
    str = str.replace(")", "\\)")
    str = str.replace(".", "\\.")
    str = str.replace("-", "\\-")
    str = str.replace(">", "\\>")
    str = str.replace("#", "\\#")
    str = str.replace("+", "\\+")
    str = str.replace("=", "\\=")
    str = str.replace("|", "\\|")
    str = str.replace("{", "\\{")
    str = str.replace("}", "\\}")
    str = str.replace("~", "\\~")
    str = str.replace("$", "\\$")
    str = str.replace(":", "\\:")

    return str;
