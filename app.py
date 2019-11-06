import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify, request

# Database setup
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(session, start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()


# Flask

app= Flask(__name__)

@app.route("/")
def welcome():
    return(f'''
    <h1>Available routes:</h1><br>

    <table border="1">
        <thead>
            <tr>
                <th>Data set</th>
                <th>Path</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Precipitation data JSON:<br><br></td>
                <td><a href="../api/v1.0/precipitation">/api/v1.0/precipitation</a></td>
            </tr>
            <tr>
                <td>List of available stations:<br><br></td>
                <td><a href="../api/v1.0/stations">/api/v1.0/stations</a></td>
            </tr>
            <tr>
                <td>Tobs data by date:<br><br></td>
                <td><a href="../api/v1.0/tobs">/api/v1.0/tobs</a></td>
            </tr>
            <tr>
                <td>
                    Min, max and average from start date to last data available:
                    <br>
                    <b>Example:</b> <i>/api/v1.0?start=2015-01-01</i><br><br>
                </td>
                <td>/api/v1.0/&lsaquo;start&rsaquo;</td>
            </tr>
            <tr>
                <td>
                    Min, max and average from start date to end date:
                    <br>
                    <b>Example:</b> <i>/api/v1.0?start=2015-01-01&end=2015-02-01</i><br><br> 
                </td>
                <td>/api/v1.0/&lsaquo;start&rsaquo;&lsaquo;end&rsaquo;</td>
            </tr>
        </tbody>
    </table>

    ''')

@app.route("/api/v1.0/precipitation")
def precipitation():
    session=Session(engine)
    results=session.query(Measurement.station, Measurement.date, Measurement.prcp).all()
    session.close()
    all_prcp=[]
    for station, date, prcp in results:
        prcp_dic={}
        prcp_dic["station"]=station
        prcp_dic["date"]=date
        prcp_dic["prcp"]=prcp
        all_prcp.append(prcp_dic)
    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)
    results=session.query(Station.name).all()
    session.close()
    all_stations=list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)
    lastDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    lastDateDT = dt.datetime.strptime(lastDate[0], "%Y-%m-%d")
    twelveMonthsAgo = lastDateDT - dt.timedelta(days=365)   
    results=session.query(Measurement.station, Measurement.date, Measurement.tobs).filter(Measurement.date >= twelveMonthsAgo).all()
    session.close()
    all_tobs=[]
    for station, date, tobs in results:
        tobs_dic={}
        tobs_dic["station"]=station
        tobs_dic["date"]=date
        tobs_dic["tobs"]=tobs
        all_tobs.append(tobs_dic)
    return jsonify(all_tobs)

@app.route("/api/v1.0/", methods=['GET'])
def by_start():
    args_dict = request.args.to_dict()
    session=Session(engine)
    start_date = args_dict['start']
    print("I get the start")
    if len(args_dict)==1:
        lastDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    else:
        lastDate = args_dict['end']
        print("Get the end date")
    return jsonify(calc_temps(session, start_date, lastDate))

if __name__=="__main__":
    app.run(debug=True)


