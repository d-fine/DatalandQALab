import logging
import sys

application_logger = logging.getLogger("dataland_qa_lab")


def configure_console_logger() -> None:
    """Configures logging to the console."""
    application_logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    application_logger.addHandler(console_handler)
