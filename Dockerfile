FROM python:3.9

WORKDIR /analynix
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
COPY . .

RUN python cron.py

EXPOSE 8080
CMD python manage.py runserver --insecure 0.0.0.0:8080








# FROM python:3.9

# WORKDIR /analynix
# COPY requirements.txt requirements.txt

# RUN pip3 install -r requirements.txt
# COPY . .

# EXPOSE 8080
# CMD python manage.py runserver --insecure 0.0.0.0:8080

































# FROM python:3.9

# WORKDIR /analynix
# COPY requirements.txt requirements.txt

# #RUN apt-get update && apt-get -y install cron

# RUN pip3 install -r requirements.txt
# COPY . .

# #COPY /usr/bin/crontab /etc/cron.d/
 
# # Give execution rights on the cron job
# #RUN chmod 0644 /etc/cron.d/crontab

# # Apply cron job
# #RUN crontab /etc/cron.d/crontab
 
# # Create the log file to be able to run tail
# #RUN touch /var/log/cron.log
 
# # Run the command on container startup
# #CMD cron && tail -f /var/log/cron.log

# # CMD cron -f -l; tail -f /var/log/cron.log; python manage.py crontab add; python manage.py runserver --insecure 0.0.0.0:8080

# # CMD cron; tail -f /var/log/cron.log; sudo python manage.py crontab add; python manage.py runserver --insecure 0.0.0.0:8080

# CMD python manage.py runserver --insecure 0.0.0.0:8080

# #CMD ["python","manage.py","runserver","--insecure","0.0.0.0:8080"]
# EXPOSE 8080

# #FROM ubuntu:latest
# # Install cron
# #RUN apt-get update && apt-get -y install cron && apt-get -y install pip
# # Create the log file to be able to run tail
# #RUN touch /var/log/cron.log
# # Setup cron job
# #RUN (crontab -l ; echo "* * * * * echo "Hello world" >> /var/log/cron.log") | crontab
# # Run the command on container startup
# #CMD cron && tail -f /var/log/cron.log && /bin/sh -c python3 manage.py runserver 0.0.0.0:8080 && /bin/sh -c python3 manage.py crontab add && /bin/sh -c python3 manage.py crontab add && /bin/sh -c python3 manage.py crontab show

# #WORKDIR /nixreens

# #ENV PYTHONDONTWRITEBYTECODE 1
# #ENV PYTHONUNBUFFERED 1

# #COPY ./requirements.txt /nixreens/requirements.txt
# #RUN pip install -r requirements.txt