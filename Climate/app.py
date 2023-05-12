# Import the dependencies.
from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import numpy as np
import datetime as dt


#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
#session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Homepage

@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/(start_date) ex. YYYY-MM-DD<br/>"
        f"/api/v1.0/(start_date)/(end_date)  ex. YYYY-MM-DD<br/>"
    )

# Precipitation data for the last 12 months endpoint

@app.route("/api/v1.0/precipitation")
def precip():
    session = Session(engine)
   
    # Calculate previous year 

    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    end_date = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d')

    start_date = end_date - dt.timedelta(days=365)

    # Set query to get precipitation data for last 12 months

    sel = [Measurement.date,
          Measurement.prcp]
    date_prcp = session.query(*sel).filter((Measurement.date) >= start_date).all()

    # Put date and precipitation data in dictionary

    date_prcp_dict = {}

    for dp in date_prcp:
        date_prcp_dict[dp[0]] = dp[1]

    session.close()

    # Return dictionary as json file

    return jsonify(date_prcp_dict)

# Stations data endpoint

@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    # Query for stations data

    sel = [Station.station,
           Station.name,
           Station.longitude,
           Station.latitude,
           Station.elevation]
    station_list = session.query(*sel).all()

    # Put stations data in dictionary

    result = []
    for station, name, longitude, latitude, elevation in station_list:
        date_prcp_dict = {}
        date_prcp_dict["station"] = station
        date_prcp_dict["name"] = name
        date_prcp_dict["longitude"] = longitude
        date_prcp_dict["latitude"] = latitude
        date_prcp_dict["elevation"] = elevation
        result.append(date_prcp_dict)

    session.close()

    # Return stations data dictionary as json file

    return jsonify(result)

# Temparture Observation (tobs) endpoint

@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    # Find the most recent date in the data set.
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    end_date = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d')

    # Calculate the date one year from the last date in data set.
    start_date = end_date - dt.timedelta(days=365)

    # Query for most active station

    sel_stations = [Measurement.station,
                    func.count(Measurement.station)]

    active_stations = session.query(*sel_stations).group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()
    
    # Query date and tobs for most active station for previous year
    
    sel = [Station.station,
          Station.name,
          Measurement.date,
          Measurement.tobs]
    
    active_tobs = session.query(*sel).filter(Measurement.station == active_stations[0]).\
        filter((Measurement.date) >= start_date).all()
    
    # Put data in dictionary

    result = []
    for station, name, date, tobs in active_tobs:
        tobs_dict = {}
        tobs_dict["station"] = station
        tobs_dict["name"] = name
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        result.append(tobs_dict)

    session.close()

    # Return dictionary

    return jsonify(result)

# Get minimum, average, and maximum tobs from user selected start date

@app.route("/api/v1.0/<start_dates>")
def start(start_dates):
    session = Session(engine)

    # Query for minimum, average, and maximum tobs from user selected start date

    sel = [func.min(Measurement.tobs),
           func.avg(Measurement.tobs),
           func.max(Measurement.tobs)]
    tobs_stats = session.query(*sel).filter(Measurement.date >= start_dates).all()

    session.close()

    # Put data in dictionary

    result = []
    for min, avg, max in tobs_stats:
        tobs_stats_dict = {}
        tobs_stats_dict["min"] = min
        tobs_stats_dict["avg"] = avg
        tobs_stats_dict["max"] = max
        result.append(tobs_stats_dict)

    # Return dictionary

    return jsonify(result)

# Get minimum, average, and maximum tobs from user selected start date and end date

@app.route("/api/v1.0/<start_dates>/<end_dates>")
def start_end(start_dates, end_dates):

    session = Session(engine)

    # Query for minimum, average, and maximum tobs from user selected start date and end date

    sel = [func.min(Measurement.tobs),
           func.avg(Measurement.tobs),
           func.max(Measurement.tobs)]
    tobs_range_stats = session.query(*sel).filter(Measurement.date >= start_dates).\
        filter(Measurement.date <= end_dates).all()

    session.close()

    # Put data in dictionary

    result = []
    for min, avg, max in tobs_range_stats:
        tobs_stats_range_dict = {}
        tobs_stats_range_dict["min"] = min
        tobs_stats_range_dict["avg"] = avg
        tobs_stats_range_dict["max"] = max
        result.append(tobs_stats_range_dict)

    # Return dictionary

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)