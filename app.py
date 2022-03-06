from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt
import numpy as np
import pandas as pd
from datetime import timedelta

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")

def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"List of prior year rain totals from all stations<br/>"
        f"-  http://127.0.0.1:5000//api/v1.0/precipitation<br/>"
        f"<br/>"
        f"List of Station numbers and names<br/>"
        f"- http://127.0.0.1:5000//api/v1.0/stations<br/>"
        f"<br/>"
        f" List of prior year temperatures from all stations<br/>"
        f"-  http://127.0.0.1:5000//api/v1.0/tobs<br/>"
        f"<br/>"
        f"When given the start date (YYYY-MM-DD), calculates the MIN/AVG/MAX temperature<br/>"        
        f"-  http://127.0.0.1:5000//api/v1.0/<start><br/>"
        f"<br/>"
        f"When given a range of start and the end date (YYYY-MM-DD), calculate the MIN/AVG/MAX temperature<br/>"
        f"-  http://127.0.0.1:5000//api/v1.0/<start>/<end>"
    )

# Precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    ytd = dt.datetime.strptime(recent_date, "%Y-%m-%d")- dt.timedelta(days=366)

    past_temp = (session.query(Measurement.date, Measurement.prcp)
                .filter(Measurement.date <= recent_date)
                .filter(Measurement.date >= ytd)
                .order_by(Measurement.date).all())
    session.close()

    precip = {date: prcp for date, prcp in past_temp}
    
    return jsonify(precip)

# Stations list Station's ID and Station's name
@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    
    stations = session.query(Station.station, Station.name).all()
    stations_list = list(np.ravel(stations))
    
    session.close()
    
    return jsonify(stations_list)

# Tobs
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
        
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    ytd = dt.datetime.strptime(recent_date, "%Y-%m-%d")- dt.timedelta(days=366)
    tobs_max = session.query(Measurement.tobs).filter(Measurement.date >= ytd).\
                filter(Measurement.station == "USC00519281").\
                order_by(Measurement.date).all()

    # Convert list of tuples into normal list
    tobs_list = list(np.ravel(tobs_max))
    # Return a JSON list
    session.close()

    return jsonify(tobs_list)

# given the start only, min/max/avg, /api/v1.0/<start>
@app.route('/api/v1.0/<start>')
def calc_temps_start(start):
    session = Session(engine)

    set_start= dt.datetime.strptime(start, '%Y-%m-%d')
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    results_1 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= set_start).\
                filter(Measurement.date <= recent_date).all()
    trip = list(np.ravel(results_1))
    
    session.close()

    return jsonify(trip)
    


@app.route('/api/v1.0/<start>/<end>') 
def start(start, end ):
    session = Session(engine)
    
    set_start= dt.datetime.strptime(start, '%Y-%m-%d')
    set_end= dt.datetime.strptime(end,'%Y-%m-%d')
    results_2 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= set_start).\
                filter(Measurement.date <= set_end).all()
    trip = list(np.ravel(results_2))
    
    session.close()
    
    return jsonify(trip)


if __name__ == '__main__':
    app.run(debug=True)