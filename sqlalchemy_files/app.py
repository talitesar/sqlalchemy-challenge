import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Connect to the hawaii sqlite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to the tables
measurement = Base.classes.measurement
stations = Base.classes.station

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
        f"/api/v1.0/<start><br/>"
        f"Format: year-month-day<br/>"
        f"/api/v1.0/<start>/<end><br/>"
        f"Format: year-month-day/year-month-day<br/>"
    )

# Define the precipiation app route
@app.route("/api/v1.0/precipitation")
def prcp_year():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a dictionary of all precipitation values and dates"""
    # Find the most recent date in the data set.
    # Use session.query, sort by date in descending order so that the greatest number (most recent) is first, and select the first value.
    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()

    # Calculate the date one year from the last date in data set.
    # One year before this would be 2016-08-23.
    # Set this date equal to a query date variable to be used in filtering.
    date = dt.date(2016, 8, 23)

    # Perform a query to retrieve the date and precipitation scores
    prcp = session.query(measurement.date, measurement.prcp).filter(measurement.date >= date).all()

    # Close the session
    session.close()

    # Use a dictionary comprehesion to convert these results into a dictionary
    prcp_rows = [{'Date': row[0], "Precipitation Score": row[1]} for row in prcp]

    # Return this dictionary in a json object
    return jsonify(prcp_rows)

# Define station app route
@app.route("/api/v1.0/stations")
def station_listing():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    station_list = session.query(stations.station, stations.name, stations.latitude, stations.longitude, stations.elevation).all()

    # Close the session
    session.close()

    # Create a dictionary from the row data and append to a list of stations all station information
    all_stations = []
    for station,name,latitude,longitude,elevation in station_list:
        stations_dict = {}
        stations_dict["station"] = station
        stations_dict["name"] = name
        stations_dict["latitude"] = latitude
        stations_dict["longitutde"] = longitude
        stations_dict["elevation"] = elevation

        all_stations.append(stations_dict)

    # Print this as a json object
    return jsonify(all_stations)

# Define temperature app route
@app.route("/api/v1.0/tobs")
def temp():
    # Create session link to DB
    session = Session(engine)

    """Return list of temperatures from the most active station"""
    ## Find the most active station
    active_station = session.query(measurement.station,func.count(measurement.station))\
        .group_by(measurement.station).order_by(desc(func.count(measurement.station))).first()
    # Isolate the station 
    most_active_station = active_station[0] 
    # Define date for last year using datetime
    date = dt.date(2016, 8, 23)
    # Query the last 12 months of temperature observation data for this station
    temps = session.query(measurement.date, measurement.tobs).filter(measurement.date >= date).filter(measurement.station==most_active_station).all()

    # Close the session
    session.close()

    # Convert results to a dictionary
    temps_rows = [{'Date': row[0], "Temperature": row[1]} for row in temps]

    # Print the dictionary as a json object
    return jsonify(temps_rows)

# Define app route for temps from start
@app.route("/api/v1.0/<start>")
def start(start):
    # Create session link to DB
    session = Session(engine)

    """Return the min, max, and average temperature since a given start date"""
    # Create selection parameter variables for min, max, and average temps
    select_min = [measurement.tobs, func.min(measurement.tobs)]
    select_max = [measurement.tobs, func.max(measurement.tobs)]
    select_mean = [measurement.tobs, func.avg(measurement.tobs)]

    # Use select variables and filter for date greater than selected start date
    active_min = session.query(*select_min).filter(measurement.date >= start).first()
    active_max = session.query(*select_max).filter(measurement.date >= start).first()
    active_mean = session.query(*select_mean).filter(measurement.date >= start).first()

    # Close the session
    session.close()

    # Convert the min, max, avg variables into one dictionary
    temps = {"Temp Minimum": active_min[0], "Temp Maximum": active_max[0], "Temp Average": active_mean[0]}

    # Print this as a json object
    return jsonify(temps)

# Define app route for temps from start to end
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    # Create session link to DB
    session = Session(engine)

    """Return the min, max, and average temperature since a given start date and before a given end date"""

    # Create selection parameter variables for min, max, and average temps
    select_min = [measurement.tobs, func.min(measurement.tobs)]
    select_max = [measurement.tobs, func.max(measurement.tobs)]
    select_mean = [measurement.tobs, func.avg(measurement.tobs)]

    # Use select variables and filter for date greater than selected start date
    active_min = session.query(*select_min).filter(measurement.date >= start).filter(measurement.date <= end).first()
    active_max = session.query(*select_max).filter(measurement.date >= start).filter(measurement.date <= end).first()
    active_mean = session.query(*select_mean).filter(measurement.date >= start).filter(measurement.date <= end).first()

    # Close the session
    session.close()

    # Convert the min, max, avg variables into one dictionary
    temps = {"Temp Minimum": active_min[0], "Temp Maximum": active_max[0], "Temp Average": active_mean[0]}

    # Print this as a json object
    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)
