class CompanyData:
    """A class to represent company data."""

    def __init__(self) -> None:
        """Initializes the class."""

    @staticmethod
    def get_company_pdf() -> list:
        """Gets the company PDFs.

        Returns:
            list: A list of company PDFs.
        """
        return [
            "/Users/jonas/DatalandQALab/data/pdfs/concordia.pdf",
            "/Users/jonas/DatalandQALab/data/pdfs/covestro.pdf",
            "/Users/jonas/DatalandQALab/data/pdfs/deka.pdf",
            "/Users/jonas/DatalandQALab/data/pdfs/enbw.pdf",
            "/Users/jonas/DatalandQALab/data/pdfs/enel.pdf",
            "/Users/jonas/DatalandQALab/data/pdfs/eon.pdf",
            "/Users/jonas/DatalandQALab/data/pdfs/iberdrola.pdf",
            "/Users/jonas/DatalandQALab/data/pdfs/munichre.pdf",
            "/Users/jonas/DatalandQALab/data/pdfs/rwe.pdf",
            "/Users/jonas/DatalandQALab/data/pdfs/total.pdf",
        ]

    @staticmethod
    def get_company_pages() -> list:
        """Gets the company pages.

        Returns:
            list: A list of company pages.
        """
        return [
            [57, 57, 58, 58, 59],
            [200, 201, 202, 203, 204],
            [116, 117, 117, 118, 119],
            [152, 152, 153, 153, 154],
            [232, None, None, 233, 234],
            [300, 300, 301, 302, 302],
            [295, None, None, 296, 297],
            [65, 66, 66, 67, 67],
            [104, 105, 108, 111, 114],
            [317, 317, 319, 320, 322],
        ]
