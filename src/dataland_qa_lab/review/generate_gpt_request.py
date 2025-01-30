import ast
import logging

from openai import AzureOpenAI

from dataland_qa_lab.utils import config

logger = logging.getLogger(__name__)


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

        Raises:
            ValueError: For any issues encountered during the process.
        """
        try:
            try:
                conf = config.get_config()
            except Exception as e:
                msg = f"Error loading configuration in Gpt_request generator: {e}"
                raise ValueError(msg) from e

            # Initialize Azure OpenAI client
            try:
                client = AzureOpenAI(
                    api_key=conf.azure_openai_api_key,
                    api_version="2024-07-01-preview",
                    azure_endpoint=conf.azure_openai_endpoint,
                )
            except Exception as e:
                msg = f"Error initializing AzureOpenAI client: {e}"
                raise ValueError(msg) from e

            # Create GPT request
            try:
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
            except Exception as e:
                msg = f"Error during GPT request creation: {e}"
                raise ValueError(msg) from e

            # Extract tool calls from GPT response
            try:
                if updated_openai_response.choices[0].message.tool_calls:
                    tool_call = updated_openai_response.choices[0].message.tool_calls[0].function
                else:
                    msg = "No tool calls found in the GPT response."
                    raise ValueError(msg)  # noqa: TRY301
            except Exception as e:  # noqa: BLE001
                msg = f"Error extracting tool calls: {e}"
                raise ValueError(e)  # noqa: B904

            # Parse tool call arguments
            try:
                data_dict = ast.literal_eval(tool_call.arguments)
            except Exception as e:  # noqa: BLE001
                msg = f"Error parsing tool call arguments: {e}"
                raise ValueError(msg)  # noqa: B904

            # Convert to list and return
            try:
                return list(data_dict.values())
            except Exception as e:  # noqa: BLE001
                msg = f"Error converting parsed data to list: {e}"
                raise ValueError(msg)  # noqa: B904

        except Exception as general_error:  # noqa: BLE001
            # General error handling
            msg = f"An unexpected error occurred: {general_error}"
            raise ValueError(msg)  # noqa: B904
