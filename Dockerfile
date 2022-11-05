#FROM python:3.9

#WORKDIR /nixreens
#COPY requirements.txt requirements.txt

#RUN pip3 install -r requirements.txt
#COPY . .

#RUN apt-get update && apt-get -y install cron && apt-get -y install #pip && touch /var/log/cron.log

#RUN python manage.py crontab add
#ENTRYPOINT ["./docker-entrypoint.sh"] 

#CMD ["python","manage.py","runserver","0.0.0.0:8080"]
#EXPOSE 8080

FROM ubuntu:latest
# Install cron
RUN apt-get update && apt-get -y install cron && apt-get -y install pip
# Create the log file to be able to run tail
RUN touch /var/log/cron.log
# Setup cron job
RUN (crontab -l ; echo "* * * * * echo "Hello world" >> /var/log/cron.log") | crontab
# Run the command on container startup
CMD cron && tail -f /var/log/cron.log 

WORKDIR /nixreens

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /nixreens/requirements.txt
RUN pip install -r requirements.txt