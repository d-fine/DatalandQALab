import logging
import time

from dataland_qa_lab.utils import console_logger

logger = logging.getLogger("dataland_qa_lab.bin.server")


def main() -> None:
    """Launch the QA Lab server."""
    console_logger.configure_console_logger()
    logger.info("Launching the Dataland QA Lab server")

    while True:
        logger.info("Still running")
        time.sleep(10)


if __name__ == "__main__":
    main()
