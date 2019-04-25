import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    """Home page.
    List all routes that are available."""
    return (
        f"Available Routes:<br/>"
        f"<a target='_blank' href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"<a target='_blank' href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"<a target='_blank' href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"/api/v1.0/&lt;start> - Enter the start date of your vacation as YYYY-MM-DD<br/>"
        f"/api/v1.0/&lt;start>/&lt;end> - Enter the start and end dates of your vacation as YYYY-MM-DD"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    """Convert the query results to a Dictionary using date as the key and prcp as the value.
    Return the JSON representation of your dictionary."""
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= dt.date(2017, 8 ,23) - dt.timedelta(days=365)).\
    order_by(Measurement.date).all()
    # results = session.query(Measurement.date, Measurement.prcp).all()    
    prcp_data = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp_data.append(prcp_dict)
    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    results = session.query(Station.station).all()
    return jsonify(results)

@app.route("/api/v1.0/tobs")
def tobs():
    """Query for the dates and temperature observations from a year from the last data point.
    Return a JSON list of Temperature Observations (tobs) for the previous year."""
    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= dt.date(2017, 8 ,23) - dt.timedelta(days=365)).\
    order_by(Measurement.date).all()
    tobs_data = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_data.append(tobs_dict)
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start, end=None):
#     """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#     When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
#     When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""
    intermediate = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start)
    if end is not None:
        intermediate = intermediate.filter(Measurement.date <= end)
    min_avg_max, = intermediate.all()
    min, avg, max = min_avg_max
    return (
            f"Temperature Observations (tobs):<br/>"
            f"Min: {min}<br/>"
            f"Max: {max}<br/>"
            f"Avg: {avg}"
            )

if __name__ == '__main__':
    app.run(debug=True)


    