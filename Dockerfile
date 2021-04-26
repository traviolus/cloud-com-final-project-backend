FROM python:3.9-buster

WORKDIR /app

RUN apt-get update && \
    apt-get install supervisor gcc libffi-dev

COPY ./requirements.txt /app/requirements.txt
RUN python3 -m pip install --upgrade pip && python3 -m pip install -r requirements.txt

COPY ./project /app/

RUN mkdir /var/log/app/
RUN touch /var/log/app/app.log
RUN chown -R www-data /var/log/app && \
    chgrp -R www-data /var/log/app

EXPOSE 8000

CMD ["/usr/local/bin/gunicorn", "project.wsgi:application", "-w", "4", "-b", "0.0.0.0:8000", "--reload"]
