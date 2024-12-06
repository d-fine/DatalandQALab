from azure.ai.documentintelligence.models import AnalyzeResult


class Prompts:
    """Generates the prompt for every template."""

    def __init__(self) -> None:
        """Initializes the Prompts class."""

    @staticmethod
    def generate_prompt_for_template1(analyze_result: AnalyzeResult) -> str:
        """Generates the prompt for template 1.

        Returns:
            str: The prompt for template 1.
        """
        return f"""
        Given the information from the [relevant documents],
        provide the answers of all 6 questions in template 1.
        Only answer with 'Yes' or 'No'. You need to provide 6 answers.
        # Relevant Documents
        {analyze_result.content}
        """

    @staticmethod
    def generate_prompt_for_template2(analyze_result: AnalyzeResult) -> str:
        """Generates the prompt for template 2.

        Returns:
            str: The prompt for template 2.
        """
        return f"""
        For each row 1-8 of template 2 (revenue) it's called
        "Taxonomy-aligned economic activities (denominator)",
        give me the percentage of "CCM+CCA", "CCM" and "CCA" for all rows.
        Focus on the row numbers on the left side of the table.
        If you can't find the percentage value, write "0".
        Consider translating for this given task like Meldebogen instead of template.
        Make sure to provide the % sign.
        # Relevant Documents
        {analyze_result.content}
        """

    @staticmethod
    def generate_prompt_for_template3(analyze_result: AnalyzeResult) -> str:
        """Generates the prompt for template 3.

        Returns:
            str: The prompt for template 3.
        """
        return f"""
        For each row 1-8 of template 3 (revenue) it's called
        "Taxonomy-aligned economic activities (numerator)",
        give me the percentage of "CCM+CCA", "CCM" and "CCA" for all rows.
        Focus on the row numbers on the left side of the table.
        If you can't find the percentage value, write "0".
        Consider translating for this given task like Meldebogen instead of template.
        Make sure to provide the % sign.
        # Relevant Documents
        {analyze_result.content}
        """

    @staticmethod
    def generate_prompt_for_template4(analyze_result: AnalyzeResult) -> str:
        """Generates the prompt for template 4.

        Returns:
            str: The prompt for template 4.
        """
        return f"""
        For each row 1-8 of template 4 (revenue) it's called
        "Taxonomy-eligible but not taxonomy-aligned economic activities",
        give me the percentage of "CCM+CCA", "CCM" and "CCA" for all rows.
        Focus on the row numbers on the left side of the table.
        If you can't find the percentage value, write "0".
        Consider translating for this given task like Meldebogen instead of template.
        Make sure to provide the % sign.
        # Relevant Documents
        {analyze_result.content}
        """

    @staticmethod
    def generate_prompt_for_template5(analyze_result: AnalyzeResult) -> str:
        """Generates the prompt for template 5.

        Returns:
            str: The prompt for template 5.
        """
        return f"""
        For each row 1-8 of template 5 (revenue) it's called
        "Taxonomy non-eligible economic activities",
        give me the percentage for all rows.
        Focus on the row numbers on the left side of the table.
        If you can't find the percentage value, write "0".
        Consider translating for this given task like Meldebogen instead of template.
        Make sure to provide the % sign.
        # Relevant Documents
        {analyze_result.content}
        """
