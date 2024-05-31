FROM langchain/langchain

RUN pip install langserve

COPY ./gptmodel.py /gptmodel.py
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

ENV OPENAI_API_KEY=sk-proj-CUdeVPUz9ydF7lmcoMdtT3BlbkFJTg1jD1GS4w2QUKBalNUT \
LANGCHAIN_TRACING_V2=true \
LANGCHAIN_API_KEY=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

CMD ["python", "gptmodel.py"]
