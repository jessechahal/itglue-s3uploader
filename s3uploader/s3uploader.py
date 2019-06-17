import os

from flask import Flask, flash, request, redirect, url_for
import boto3
import coloredlogs, logging
from logging.config import dictConfig
from werkzeug.utils import secure_filename

logging_config = dict(
    version = 1,
    formatters = {
        'f': {'format':
              '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'}
        },
    handlers = {
        'h': {'class': 'logging.StreamHandler',
              'formatter': 'f',
              'level': logging.DEBUG}
        },
    root = {
        'handlers': ['h'],
        'level': logging.DEBUG,
        },
)

dictConfig(logging_config)

logger = logging.getLogger()
coloredlogs.install(level='DEBUG',
                    logger=logger,
                    fmt='%(asctime)s %(levelname)-6s %(message)s')

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        S3_BUCKETNAME='it-glue',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    @app.route("/")
    def root():
        return "Please use the /upload endpoint"


    @app.route("/upload", methods=('POST'))
    def upload():
       # TODO: implement this
       s3 = boto3.resource('s3')
       # check if the post request has the file part
       if 'file' not in request.files:
           flash('No file part')
           return redirect(request.url)
       file = request.files['file']
       # if user does not select file, browser also
       # submit an empty part without filename
       if file.filename == '':
           flash('No selected file')
           return redirect(request.url)
       if file:
        filename = secure_filename(file.filename) #maybe save filename has a hash of date + filename?

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploaded_file', filename=filename))
        return '' #dunno what yet


    @app.route("/healthcheck", methods=('GET'))
    def upload():
        # contact s3 bucket? upload file to s3 bucket?
    return app

if __name__ == "__main__":
    create_app().run(debug=True, host='0.0.0.0')