import logging
import time

from dataland_qa_lab.dataland import scheduled_processor
from dataland_qa_lab.utils import console_logger

logger = logging.getLogger("dataland_qa_lab.bin.server")


def main(single_pass_e2e: bool = False) -> None:
    """Launch the QA Lab server."""
    console_logger.configure_console_logger()
    logger.info("Launching the Dataland QA Lab server")

    scheduled_processor.run_scheduled_processing()

    while True:
        logger.info("Still running")
        if single_pass_e2e:
            break
        time.sleep(10)


if __name__ == "__main__":
    main()
