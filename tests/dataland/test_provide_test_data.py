from pathlib import Path

from dataland_qa_lab.dataland.provide_test_data import provide_test_data
from dataland_qa_lab.utils import config


def test_upload_test_data() -> None:
    dataland_client = config.get_config().dataland_client
    project_root = Path(__file__).resolve().parent.parent.parent
    pdf_path = project_root / "data" / "pdfs"
    json_path = project_root / "data" / "jsons"
    test_data = provide_test_data(pdf_path=pdf_path, json_path=json_path, dataland_client=dataland_client)
    assert len(test_data) == 10
