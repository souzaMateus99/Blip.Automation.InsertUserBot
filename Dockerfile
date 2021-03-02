FROM joyzoursky/python-chromedriver:3.8-selenium

COPY content/packages/requirements.txt packages/requirements.txt
RUN pip install -r packages/requirements.txt
RUN pip install --user --upgrade selenium

COPY content/src/ script/src/
COPY content/configuration/config.json script/configuration/config.json

WORKDIR /script

ENTRYPOINT [ "python", "src/add_user_script.py" ]