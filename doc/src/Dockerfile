FROM public.ecr.aws/lambda/python:3.7

COPY app.py doc_log.py logging.yml requirements.txt ./

RUN python3.7 -m pip install -r requirements.txt -t .

# Command can be overwritten by providing a different command in the template directly.
CMD ["app.app"]