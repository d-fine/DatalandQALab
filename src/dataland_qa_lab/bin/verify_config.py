import logging
import pprint

from pydantic import ValidationError

from dataland_qa_lab.utils import config, console_logger

logger = logging.getLogger("dataland_qa_lab.bin.verify_config")


def main() -> None:
    """Verify the Dataland QA Lab configuration."""
    console_logger.configure_console_logger()
    logger.info("Verifying the Dataland QA Lab configuration")
    try:
        config.get_config()
    except ValidationError as e:
        logger.error(  # noqa: TRY400
            "Configuration is syntactically invalid. Please ensure your .env file is up-to-date \n %s",
            pprint.pformat(e.errors()),
        )
        return

    logger.info("Configuration is valid")


if __name__ == "__main__":
    main()
