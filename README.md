# aiextractpy
aiextractpy's DataExtractor is a Python class designed to extract specific data from text using OpenAI's GPT-3 model.

## Installation

To use DataExtractor, clone the repository or copy the `DataExtractor.py` file into your project directory.

## Usage

'''python
from src.aiextractpy.data_extractor import DataExtractor
import configparser

config = configparser.ConfigParser()
config.read('secrets/config.ini')
openai_key = config.get('openai', 'key')
openai_model = config.get('openai', 'model')

with open('secrets/test.txt', 'r') as file:
    input_text = file.read()

data_labels = ['sender', 'receiver', 'amount', 'receipt number']

de = DataExtractor(input_text, data_labels)
de.initialize_openai(openai_key, openai_model)
data, error = de.extract_data()

if error:
    print(f"An error occurred: {error}")
else:
    print("Extracted data:")
    print(data)
'''