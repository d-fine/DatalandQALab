# Based on Dockerfile from PDM docs (https://pdm-project.org/latest/usage/advanced/#use-pdm-in-a-multi-stage-dockerfile)
ARG PYTHON_BASE=3.12

FROM python:$PYTHON_BASE AS builder

RUN pip install -U pdm
ENV PDM_CHECK_UPDATE=false

RUN apt-get update && apt-get install -y default-jre

COPY pyproject.toml pdm.lock README.md /project/
COPY ./ /project/

WORKDIR /project

FROM python:$PYTHON_BASE

COPY --from=builder /project/.venv/ /project/.venv
ENV PATH="/project/.venv/bin:$PATH"

EXPOSE 8501

COPY ./ /project
CMD ["pdm", "run", "monitor"]
    