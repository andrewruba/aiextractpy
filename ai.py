import numpy as np
import PyPDF2
import openai
import tiktoken
from src.helper_modules.data_orangutan import initialize_openai
from firebase_admin import firestore
import configparser


def data_extraction(input_file, df):

    output_dict_str = "{"
    data_labels = []
    for label in df["Data label"].to_numpy():
        if label != "Click here and start typing to add data label..." and label is not None:
            output_dict_str = output_dict_str + "'"+label+"': '"+label+" data', "
            data_labels.append(label)
    output_dict_str = output_dict_str + "}"

    if not input_file:
        return (None, "Please upload a pdf!")
    if len(data_labels) == 0:
        return (None, "Please edit at least 1 data label!")

    reader = PyPDF2.PdfReader(input_file)
    num_pages = len(reader.pages)
    full_text = ""
    for i in range(num_pages):
        page = reader.pages[i]
        text = page.extract_text()
        full_text = full_text + text

    _log_prompt(full_text, ', '.join(data_labels))
    key, model = initialize_openai()
    openai.api_key = key

    prompt = f"""
    Here is the text of a pdf. [START OF PDF TEXT]{full_text}[END OF PDF TEXT].
    The problem is that I programmatically extracted the full text from a pdf so it will have some extraneous text. 
    I want to extract the data for the following data labels only: {', '.join(data_labels)}.
    I want the output in the following format with no other text or commentary from you: {output_dict_str}
    """

    encoding = tiktoken.encoding_for_model(model)
    num_tokens = len(encoding.encode(prompt))
    if num_tokens > 10000:
        return (None, "There is too much text in the pdf. Please upload a smaller pdf!")

    chat_completion = openai.ChatCompletion.create(
        model = model,
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature = 0.0,
        max_tokens = 16385-int(num_tokens/0.9)
    )
    chat_dict_text = chat_completion["choices"][0]["message"]["content"]

    try:
        print(chat_dict_text)
        chat_dict = eval(chat_dict_text)
        extracted_data = []
        for data_label in df["Data label"].to_numpy():
            if data_label in chat_dict:
                extracted_data.append(chat_dict[data_label])
            else:
                extracted_data.append(None)
        df["Extracted data"] = extracted_data

        return df, None

    except Exception as e:
        return (None, e)

def _log_prompt(full_text, data_labels):
    try:
        config = configparser.ConfigParser()
        config.read('config/config.ini')
        prompt_collection = config.get('firebase', 'prompt_collection')
        db = firestore.client()

        data = {
            'full_text': full_text,
            'data_labels': data_labels,
        }

        doc_ref = db.collection(prompt_collection).document()
        doc_ref.set(data)

        return None

    except:
        pass
