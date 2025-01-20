from babel.numbers import format_currency as _format_currency


def format_currency(value):
    return _format_currency(value, 'CLP', locale='es_CL')

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
