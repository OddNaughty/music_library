from prompt_toolkit import prompt
from prompt_toolkit.contrib.completers import WordCompleter


def confirm(message):
    keep = prompt(message + " [Y/n] ? : ")
    if keep in ["Y", "y", ""]:
        return True
    return False


def ask(message, choices=None):
    return prompt(message, completer=WordCompleter(choices))


def ask_with_default(message, default, choices=None):
    default_msg = f" [{default}]" if default else ""
    if not choices:
        res = prompt(f"{message}{default_msg} [Y/n] ? : ")
    else:
        res = prompt(f"{message}{default_msg} [Y/n] ? : ", completer=WordCompleter(choices))
    if not res or res in ["Y", "y", ""]:
        return default
    return res
