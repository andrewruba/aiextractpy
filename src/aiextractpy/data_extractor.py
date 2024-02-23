import tiktoken
from openai import OpenAI


class DataExtractor:
    def __init__(self, input_text: str = "", data_labels: list = []):
        """
        Initializes a DataExtractor object.

        Args:
            input_text (str): Any text corpus from which to extract data.
            data_labels (list): A list of data labels to extract.

        Returns:
            None
        """
        self.input_text = input_text
        self.data_labels = data_labels
        self.output_dict_prompt = self._get_output_dict_prompt(
            self.data_labels
        )
        self.prompt = self._get_prompt(
            self.input_text,
            self.data_labels,
            self.output_dict_prompt
        )

        self.model = None
        self.client = None

    def _get_output_dict_prompt(self, data_labels):
        """
        Generates the output dictionary prompt.

        Args:
            data_labels (list): A list of data labels.

        Returns:
            str: The output dictionary prompt.
        """
        output_dict_str = "{"
        for data_label in data_labels:
            if data_label is not None:
                output_dict_str = output_dict_str + "'"+data_label+"': '"+data_label+" data', "
        output_dict_str += "}"
        return output_dict_str

    def _get_prompt(self, input_text, data_labels, output_dict_prompt):
        """
        Generates the full prompt including input text, data labels, and output format.

        Args:
            input_text (str): The input text extracted from a PDF.
            data_labels (list): A list of data labels to extract.
            output_dict_prompt (str): The output dictionary prompt.

        Returns:
            str: The full prompt.
        """
        prompt = f"""
        Here is the text of a pdf. [START OF PDF TEXT]{input_text}[END OF PDF TEXT].
        The problem is that I programmatically extracted the full text from a pdf so it will have some extraneous text. 
        I want to extract the data for the following data labels only: {', '.join(data_labels)}.
        I want the output in the following format with no other text or commentary from you: {output_dict_prompt}
        """
        return prompt

    def _check_num_tokens(self):
        """
        Checks if the number of tokens in the prompt is roughyl within the limit.

        Returns:
            int: The number of tokens in the prompt.
        """
        assert self.prompt is not None and self.model is not None, "Initialize OpenAI!"
        encoding = tiktoken.encoding_for_model(self.model)
        num_tokens = len(encoding.encode(self.prompt))
        assert num_tokens < 10000, "The prompt is too big for this model!"
        return num_tokens

    def initialize_openai(self, openai_key: str = "", openai_model: str = ""):
        """
        Initializes the OpenAI client.

        Args:
            openai_key (str): The OpenAI API key.
            openai_model (str): The OpenAI model.

        Returns:
            None
        """
        self.model = openai_model
        self.client = OpenAI(api_key=openai_key)

    def extract_data(self):
        """
        Extracts data using the initialized OpenAI client and model.

        Returns:
            tuple: A tuple containing extracted data dictionary and error message (if any).
        """
        assert self.client is not None and self.model is not None, "Initialize OpenAI!"
        num_tokens = self._check_num_tokens()
        chat_completion = self.client.chat.completions.create(
            model = self.model,
            messages = [
                {
                    "role": "user",
                    "content": self.prompt
                }
            ],
            temperature = 0.0,
            max_tokens = 16385-int(num_tokens/0.9)
        )

        chat_dict_text = chat_completion.choices[0].message.content

        try:
            chat_dict = eval(chat_dict_text)
            extracted_data = {}
            for data_label in self.data_labels:
                if data_label in chat_dict:
                    extracted_data[data_label] = chat_dict[data_label]
                else:
                    extracted_data[data_label] = None
            return chat_dict, None

        except Exception as e:
            return (chat_dict_text, e)
