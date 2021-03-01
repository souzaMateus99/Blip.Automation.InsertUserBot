FROM joyzoursky/python-chromedriver:3.8-alpine3.10-selenium

RUN mkdir packages

ADD content/packages/requirements.txt packages
RUN pip install -r packages/requirements.txt

RUN pip install chromedriver_installer

COPY content/configuration .
COPY content/src/services .
COPY content/src .

ENTRYPOINT [ "python3", "add_user_script.py" ]