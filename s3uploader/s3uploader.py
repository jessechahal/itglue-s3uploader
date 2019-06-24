import os
import tempfile

from flask import Flask, flash, request, redirect, url_for, Response
import boto3
import s3transfer
import uuid
import coloredlogs, logging
from logging.config import dictConfig
from werkzeug.utils import secure_filename


DEBUG = os.environ.get("DEBUG", True)
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
S3_BUCKET = os.environ.get("S3_BUCKET", "it-glue-s3uploader")

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if not S3_BUCKET:
        raise ValueError("No S3 bucket provided for uploads")

    logging_config = dict(
        version=1,
        formatters={
            'f': {'format':
                      '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'}
        },
        handlers={
            'h': {'class': 'logging.StreamHandler',
                  'formatter': 'f',
                  'level': logging.DEBUG}
        },
        root={
            'handlers': ['h'],
            'level': logging.DEBUG,
        },
    )

    dictConfig(logging_config)

    logger = logging.getLogger('waitress')
    coloredlogs.install(level=LOG_LEVEL,
                        logger=logger,
                        fmt='%(asctime)s %(levelname)-6s %(message)s')


    s3 = boto3.resource('s3')

    def generate_s3_filename(initial_filename):
        # maybe save filename has a hash of date + filename?
        filename = secure_filename(initial_filename)
        random_file_name = ''.join([str(uuid.uuid4().hex[:12]), filename])
        return random_file_name

    def create_local_temp_file(file_content):
        temp_file = tempfile.mkstemp(prefix="s3uploader_")
        with tempfile.mkstemp(prefix="s3uploader_") as f:
            f.write(file_content)
        return temp_file



    @app.route("/")
    def root():
        return "Please use the 'POST /upload' endpoint or 'GET /healthcheck'"


    @app.route("/upload", methods=['POST'])
    def upload():
        # TODO: implement this
        # check if the post request has the file part
        if request.method != "POST":
            logger.error("Something went horribly wrong, didn't get a POST message")
            logger.debug(request)
            return redirect(request.url)
        if 'file' not in request.files:
            logger.error('No file called "file" in POST message')
            flash('No file part')
            return redirect(request.url)
        uploaded_file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if uploaded_file.filename == '':
            logger.error("Filename is blank, no file was probably selected")
            flash('No selected file')
            return redirect(request.url)

        if uploaded_file:
            logger.info("POST msg looks good")
            unique_filename = generate_s3_filename(uploaded_file.filename)
            logger.debug("generated unique filename {0}".format(unique_filename))
            temp_folder = tempfile.tempdir
            logger.debug("temp file folder {0}".format(temp_folder))
            local_saved_filepath = os.path.join(temp_folder, unique_filename)
            uploaded_file.save(local_saved_filepath)

            s3.meta.client.upload_file(local_saved_filepath, S3_BUCKET, unique_filename)
            object_acl = s3.ObjectAcl(S3_BUCKET,unique_filename)
            object_acl.put(ACL='public-read')

            bucket_location = s3.meta.client.get_bucket_location(Bucket=S3_BUCKET)
            object_url = "https://s3-{0}.amazonaws.com/{1}/{2}".format(
                bucket_location['LocationConstraint'],
                S3_BUCKET,
                unique_filename)
            return Response(object_url, status=200, mimetype='application/text')

        #s3.upload_file(Key, app.config.S3_BUCKETNAME, filename)

        # return redirect(url_for('uploaded_file', filename=filename))


    @app.route("/healthcheck", methods=['GET'])
    def healthcheck():
        bucket_location = s3.meta.client.get_bucket_location(Bucket=S3_BUCKET)
        if bucket_location:
            return Response("", status=200, mimetype='application/json')
        else:
            return Response("Couldn't reach s3 bucket", status=500, mimetype='application/text')


    return app

application = create_app()
if __name__ == "__main__":
    application.run(debug=DEBUG, host='0.0.0.0')
