FROM python:2.7
LABEL maintainer="jesse@jessechahal.com"

COPY . /s3uploader
WORKDIR /s3uploader
RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=s3uploader
#NOTE: need a tmpfs for storing uploaded files before sending them to S3. tmpfs is faster+better then a disk mount for this case
#VOLUME /tmp
HEALTHCHECK --timeout=5s \
    CMD curl localhost:5000/healthcheck || exit 1
EXPOSE 5000

ENTRYPOINT ["waitress-serve"]
CMD ["--port=5000", "--call", "s3uploader.s3uploader:create_app"]
