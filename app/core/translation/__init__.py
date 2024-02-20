import json

from google.cloud import translate


with open('../iso639-1.json') as f:
    iso_639_1 = json.load(f)


def translate_text(text:str):
    PROJECT_ID = 'studied-flow-385100'
    PARENT = f'projects/{PROJECT_ID}'
    TRANSLATE = translate.TranslationServiceClient()
    data = {
                'contents': [text],
                'parent': PARENT,
                'target_language_code': 'en-US',
            }
    try:
        response = TRANSLATE.translate_text(request=data)
    except TypeError:
        response = TRANSLATE.translate_text(**data)
    
    response['language'] = iso_639_1.get(response.translations[0].detected_language_code)

    return response
