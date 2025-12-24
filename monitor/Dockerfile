# Based on Dockerfile from PDM docs (https://pdm-project.org/latest/usage/advanced/#use-pdm-in-a-multi-stage-dockerfile)
ARG PYTHON_BASE=3.12

FROM python:$PYTHON_BASE AS builder

RUN pip install -U pdm
ENV PDM_CHECK_UPDATE=false

RUN apt-get update && apt-get install -y default-jre

COPY pyproject.toml pdm.lock README.md /project/
COPY monitor/ /project/monitor
COPY bin/ /project/bin

WORKDIR /project
RUN mkdir .git && ./bin/generate_dataland_api_clients.sh && pdm install --check --prod --no-editable
    
EXPOSE 8501

COPY monitor /project/monitor
CMD ["pdm", "run","monitor"]
