# import needed dependencies

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/><br/>"
        f"Input dates in this format: YYYY-MM-DD"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # query all dates for precipitation data 
    results = session.query(measurement.date, measurement.prcp).all()

    session.close()
    
    # create a dictionary of precipitation by date 
    total_precip = []

    for date, precip in results:
        precip_dict = {}
        precip_dict['date'] = date
        precip_dict['precip'] = precip
        total_precip.append(precip_dict)
    
    return jsonify(total_precip)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # query all station names
    results = session.query(station.name).all()

    session.close()

    # convert list 

    return jsonify(results)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # query dates and temperature observations for the most active station 
    results = session.query(measurement.date, measurement.tobs).\
                filter(measurement.station == 'USC00519281', measurement.date > "2016-08-23").all()

    # convert the results into a dictionary of temp observed by date 
    temp_obs = []

    for date, temp in results:
        temp_dict = {}
        temp_dict['date'] = date
        temp_dict['temp'] = temp
        temp_obs.append(temp_dict)

    return jsonify(temp_obs)

@app.route("/api/v1.0/<start>")
def start(start):
#     # Create our session (link) from Python to the DB
    session = Session(engine)

    # query for min, avg, and max temperatures over the year
    low_temp = session.query(func.min(measurement.tobs)).\
        filter(measurement.date > start).all()

    high_temp = session.query(func.max(measurement.tobs)).\
        filter(measurement.date > start).all() 

    avg_temp = session.query(func.avg(measurement.tobs)).\
        filter(measurement.date > start).all()

    start_dict = [('high temp', high_temp),
                        ('avg temp', avg_temp),
                        ('low temp', low_temp)]

    return jsonify(start_dict)

@app.route("/api/v1.0/<start>/<end>")
def range(start, end):
#     # Create our session (link) from Python to the DB
    session = Session(engine)

    # query for min, avg, and max temperatures over the specified time range
    low_temp = session.query(func.min(measurement.tobs)).\
        filter(measurement.date > start, measurement.date <= end).all()

    high_temp = session.query(func.max(measurement.tobs)).\
        filter(measurement.date > start, measurement.date <= end).all() 

    avg_temp = session.query(func.avg(measurement.tobs)).\
        filter(measurement.date > start, measurement.date <= end).all()

    range_dict = ([('high temp', high_temp),
                        ('avg temp', avg_temp),
                        ('low temp', low_temp)])

    return jsonify(range_dict)

if __name__ == '__main__':
    app.run(debug=True)