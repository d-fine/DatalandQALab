import ast

from openai import AzureOpenAI

from dataland_qa_lab.utils import config


class GenerateGptRequest:
    """Generates the actual GPT request."""

    @staticmethod
    def generate_gpt_request(mainprompt: str, subprompt: str) -> list:
        """Generates the actual GPT request.

        Args:
            mainprompt (str): The main system prompt for the template.
            subprompt (str): Additional context or parameters for the tool function.

        Returns:
            List[str]: A list of extracted values from the GPT response.
        """
        conf = config.get_config()

        client = AzureOpenAI(
            api_key=conf.azure_openai_api_key,
            api_version="2024-07-01-preview",
            azure_endpoint=conf.azure_openai_endpoint,
        )

        updated_openai_response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            messages=[
                {"role": "system", "content": mainprompt},
            ],
            tool_choice="required",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "requested_information_precisely_found_in_relevant_documents",
                        "description": "Submit the requested information. "
                        "Use this function when the information is precisely stated in the relevant documents.",
                        "parameters": subprompt,
                    },
                }
            ],
        )
        tool_call = updated_openai_response.choices[0].message.tool_calls[0].function
        data_dict = ast.literal_eval(tool_call.arguments)
        return list(data_dict.values())
