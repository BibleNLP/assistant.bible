import json

import boto3

# with open('../iso639-1.json') as f:
#     iso_639_1 = json.load(f)


def translate_text(text:str):
    translate = boto3.client(service_name='translate', use_ssl=True)
    try:
        # Call AWS Translate
        response = translate.translate_text(
            Text=text,
            SourceLanguageCode='auto',  # Automatically detect the source language
            TargetLanguageCode='en'     # Target language code is 'en' for English
        )
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}
    
    source_language_code = response.get('SourceLanguageCode', '').split('-')[0]  # Extracting ISO 639-1 code part
    # response['language'] = iso_639_1.get(source_language_code, "Unknown language")

    return response

if __name__ == "__main__":
    # Example text to translate
    test_text = "Hola, mundo"
    # Call the translate_text function
    result = translate_text(test_text)
    # Print the result
    print(result)
