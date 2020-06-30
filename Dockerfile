FROM python:3.8
WORKDIR /coorseo-api/
COPY application/requirements.txt application/
RUN pip3.8 install -r application/requirements.txt
RUN pip install waitress

COPY . .

ENV FLASK_APP=application
ENV FLASK_ENV=production
ENV FLASK_DEBUG=1
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080

EXPOSE 8080
CMD ["waitress-serve", "--call", "'application:create_app'"]
