FROM claude-agents-base:latest

COPY shared/ /app/shared/

COPY agents/bradbot/ /app/bradbot/

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "bradbot"]
