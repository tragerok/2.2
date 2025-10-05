import json
import os
LOCALES = {}

def load_locales():
    for filename in ['ru.json', 'en.json']:
        filepath = os.path.join(os.path.dirname(__file__), filename)
        if os.path.exists(filepath):
            lang = filename.split('.')[0]
            with open(filepath, 'r', encoding='utf-8') as f:
                LOCALES[lang] = json.load(f)
load_locales()

def L(key, lang='ru'):
    return LOCALES.get(lang, {}).get(key, key)
