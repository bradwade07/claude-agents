FROM claude-agents-base:latest

COPY shared/ /app/shared/

COPY bradbot/ /app/bradbot/

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "bradbot"]
