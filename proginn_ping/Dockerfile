FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /var/www/webapp
WORKDIR /var/www/webapp
ADD requirements.txt /var/www/webapp/
ADD geckodriver /usr/bin
RUN pip install --upgrade pip
RUN pip install -i https://pypi.douban.com/simple -r requirements.txt
ADD . /var/www/webapp/
