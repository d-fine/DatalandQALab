ARG PYTHON_BASE=3.12
FROM python:$PYTHON_BASE AS builder

RUN pip install -U pdm
ENV PDM_CHECK_UPDATE=false

RUN apt-get update && apt-get install -y default-jre

WORKDIR /project
COPY pyproject.toml pdm.lock README.md /project/
COPY src/ /project/src
COPY bin/ /project/bin

RUN mkdir .git && ./bin/generate_dataland_api_clients.sh \
    && pdm install --check --prod --no-editable

FROM python:$PYTHON_BASE

RUN useradd --create-home --uid 10001 appuser

WORKDIR /project

COPY --from=builder /project/.venv /project/.venv
COPY --from=builder /project/src /project/src
COPY --from=builder /project/bin /project/bin

RUN chown -R appuser:appuser /project

USER appuser

ENV PATH="/project/.venv/bin:$PATH"

EXPOSE 81

CMD ["uvicorn", "dataland_qa_lab.bin.server:dataland_qa_lab", "--host", "0.0.0.0", "--port", "81"]
