from pathlib import Path

from src.dataland_qa_lab.dataland.upload_test_data import upload_test_data


def test_upload_test_data() -> None:
    project_root = Path(__file__).resolve().parent.parent.parent
    pdf_path = project_root / "data" / "pdfs"
    json_path = project_root / "data" / "jsons"
    test_data = upload_test_data(pdf_path=pdf_path, json_path=json_path)
    assert len(test_data) == 10
