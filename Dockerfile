FROM python:3.15-slim
WORKDIR /opt/spliceledger
COPY spliceledger/ ./spliceledger/
COPY LICENSE .
ENV PYTHONDONTWRITEBYTECODE=1
USER 65532:65532
ENTRYPOINT ["python", "-m", "spliceledger"]
