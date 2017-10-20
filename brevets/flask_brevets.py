"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import flask
from flask import request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config

import logging

###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration()
app.secret_key = CONFIG.SECRET_KEY

###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] = flask.url_for("index")
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    km = request.args.get('km', 999, type=float)
    app.logger.debug("km={}".format(km))
    app.logger.debug("request.args: {}".format(request.args))
    # FIXME: These probably aren't the right open and close times
    # and brevets may be longer than 200km
    start_time = arrow.get(flask.session['begin_date'] + "" + flask.session['begin_time']).isoformat()
    open_time = acp_times.open_time(km, flask.session['distance'], start_time)
    close_time = acp_times.close_time(km, flask.session['distance'], start_time)
    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)

app.route("/_distance")
def distance():
    dis = request.args.get('distance', 200, type=int)
    flask.session['distance'] = dis
    return flask.jsonify(result="{}")

@app.route("/_begin_date")
def begin_data():
    date = request.args.get('date', 200, type=str)
    flask.session['begin_date'] = date
    return flask.jsonify(result="{}")
@app.route("/_begin_time")
def end_data():
    date = request.args.get('date', 200, type=str)
    flask.session['begin_time'] = date
    return flask.jsonify(result="{}")


#############

app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
