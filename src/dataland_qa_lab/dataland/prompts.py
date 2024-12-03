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
        provide the answers of all questions in template 1.
        Only answer with 'Yes' or 'No'.
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
        give me all the values of "CCM+CCA", "CCM" and "CCA" for all rows.
        Focus on the row numbers on the left side of the table.
        If you can't find the value, write "0", but alwasy provide the currency.
        Consider translating for this given task like Meldebogen instead of template.
        Make sure to provides the right units. Like €, Mio €, Mio, € in thousends or %.
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
        give me all the values of "CCM+CCA", "CCM" and "CCA" for all rows.
        Focus on the row numbers on the left side of the table.
        If you can't find the value, write "0", but alwasy provide the currency.
        Consider translating for this given task like Meldebogen instead of template.
        Make sure to provides the right units. Like €, Mio €, Mio, € in thousends or %.
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
        give me all the values of "CCM+CCA", "CCM" and "CCA" for all rows.
        Focus on the row numbers on the left side of the table.
        If you can't find the value, write "0", but alwasy provide the currency.
        Consider translating for this given task like Meldebogen instead of template.
        Make sure to provides the right units. Like €, Mio €, Mio, € in thousends or %.
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
        give me one value and one percentage per row.
        Focus on the row numbers on the left side of the table.
        If you can't find the value, write "0", but alwasy provide the currency.
        Consider translating for this given task like Meldebogen instead of template.
        Make sure to provides the right units. Like €, Mio €, Mio, € in thousends or %.
        # Relevant Documents
        {analyze_result.content}
        """
