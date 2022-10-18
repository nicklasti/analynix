FROM python:3.9

WORKDIR /nixreens
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
COPY . .

CMD [ "python","manage.py","runserver","0.0.0.0:8080" ]
EXPOSE 8080