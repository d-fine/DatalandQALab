import os

from src.dataland_qa_lab.dataland.dataset_provider import get_dataset_by_id
from monitor.qalab_api import run_report_on_qalab
from monitor.utils import load_config


def monitor_documents(documents: list[str], ai_model: str) -> None:
    """Monitor documents by comparing source of truth with QALab responses."""
    for document in documents:
        print("\nProcessing document:", document)
        try:
            res = get_dataset_by_id(document)
            source_of_truth = res.model_dump_json()

            qalab_response = run_report_on_qalab(data_id=document, ai_model=ai_model, use_ocr=False)
        except Exception as e:
            print(f"Couldn't retrieve dataset for data_id {document}")


def main():
    # todo: change this!!!
    print("======= Starting Monitoring =======")
    print("======= Please note this script currently only works for nuclear and gas datasets =======")

    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    config = load_config(config_path)

    # setting defaults, not sure if this is ideal or exiting would be better
    documents = config.get("documents", [])
    ai_model = config.get("ai_model", "gpt-4")

    if not documents:
        print("No documents specified in config. Please add document IDs to monitor.")
        exit(1)

    print("Using AI Model:", ai_model)
    print(f"Monitoring the following documents:\n{', '.join(documents)}")

    monitor_documents(documents=documents, ai_model=ai_model)


if __name__ == "__main__":
    main()
