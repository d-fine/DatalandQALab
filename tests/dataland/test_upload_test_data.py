from src.dataland_qa_lab.dataland import upload_test_data


def test_upload_test_data() -> None:
    uploaded_test_data = upload_test_data()
    assert uploaded_test_data is True
