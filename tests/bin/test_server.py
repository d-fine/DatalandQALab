from dataland_qa_lab.bin import server


def test_server_launch() -> None:
    server.main(single_pass_e2e=True)
