import re


JAILBREAK_PATTERNS = [
    r'\bcontexto\b', r'\bsystem prompt\b', r'\bprompt\b',
    r'\binstruç(ões|ao)\b', r'\bmostre seu(s)? segredo(s)?\b',
    r'\bmostre (seu|o) (contexto|sistema)\b',
    r'\bsou o criador\b', r'\bdono da aplica[cç][aã]o\b',
    r'\bconte como voc[eê] foi configurado\b',
    r'\bqual( é| e) seu contexto\b'
]

def is_prompt_disclosure_attempt(text: str) -> bool:
    t = text.lower()
    return any(re.search(p, t) for p in JAILBREAK_PATTERNS)