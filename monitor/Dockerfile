ARG PYTHON_BASE=3.12

FROM python:${PYTHON_BASE} AS builder

RUN pip install -U pdm
ENV PDM_CHECK_UPDATE=false

RUN apt-get update && apt-get install -y --no-install-recommends default-jre

WORKDIR /project

COPY pyproject.toml pdm.lock README.md /project/
COPY monitor/ /project/monitor
COPY bin/ /project/bin

RUN mkdir .git \
 && ./bin/generate_dataland_api_clients.sh \
 && pdm install --check --prod --no-editable


FROM python:${PYTHON_BASE}

RUN useradd --create-home --uid 10001 appuser

WORKDIR /project

COPY --from=builder /project/.venv /project/.venv
COPY --from=builder /project/monitor /project/monitor
COPY --from=builder /project/bin /project/bin

# ✅ CURL FÜR HEALTHCHECKS INSTALLIEREN
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

RUN chown -R appuser:appuser /project

USER appuser

ENV PATH="/project/.venv/bin:$PATH"

EXPOSE 8501

# ✅ HEALTHCHECK FÜR STREAMLIT
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["python", "-m", "monitor.monitor"]
