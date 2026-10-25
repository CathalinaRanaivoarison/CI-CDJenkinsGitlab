import logging
import os

from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def hello():
    """Return a friendly HTTP greeting."""
    return "Hello World"


@app.route("/health")
def health():
    """Health check used by the pipeline and Ansible."""
    return jsonify(status="ok", env=os.getenv("APP_ENV", "dev"))


@app.route("/error")
def error_route():
    """Raise an exception to test the error handler."""
    raise Exception("Test Error")


@app.errorhandler(500)
def server_error(e):
    logging.exception("An error occurred during a request.")
    return "An internal error occurred. See logs for full stacktrace.", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
