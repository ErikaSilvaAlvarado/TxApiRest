
import os
from flask import Flask, jsonify, g,abort, render_template, request, redirect, url_for, send_from_directory
# from app import app
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from os.path import join, dirname, realpath
import numpy as np
import pandas as pd
import glob
import csv
import MyFunctions as fu
import json
import plotly
pd.options.plotting.backend = "plotly"
import plotly.express as px
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy import create_engine, inspect
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
#from sqlalchemy import create_engine
# instancia del objeto Flask

app = Flask(__name__, static_folder='/static')
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://b07b4484224a54:edf76401@us-cdbr-east-06.cleardb.net/heroku_daac59f6173f49a'
#app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://esilva:Cr1st0_R3y@localhost/MZI_SCF_fatt'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =False

# Carpeta de subida
app.config['UPLOAD_FOLDER'] = 'Uploads'

@app.route('/downloads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    basedir = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    # Returning file from appended path
    return send_from_directory(directory=filepath, path=filename)

@app.route('/callback', methods=['POST', 'GET'])
def cb():
    paramStr = request.form.getlist('selectValues')
    xmin = float(request.form['xmin'])
    xmax = float(request.form['xmax'])
    dx = int(request.form['dx'])
    varControl = request.form['varControl']
    xRange = [xmin, xmax]
    if request.form.get('Leyenda'):
        flagLgd = True
    else:
        flagLgd = False
    csvFile = request.form['csvFile']
    dataJSON, layoutJSON,nameFig = gm(paramStr, xRange, dx, flagLgd, varControl,csvFile)
    #return render_template('customPlot.html', graphJSON=graphJSON)
    #return render_template('customPlot.html', graphJSON=graphJSON, dataJSON = dataJSON)
    return render_template('customPlot.html', dataJSON=dataJSON, layoutJSON=layoutJSON,nameFig=nameFig)
    
@app.route("/")
def listingTables():
    engine = create_engine("mysql+pymysql://b07b4484224a54:edf76401@us-cdbr-east-06.cleardb.net/heroku_daac59f6173f49a")
    #engine = create_engine("mysql+pymysql://esilva:Cr1st0_R3y@localhost/MZI_SCF_fatt")
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    # renderizamos la plantilla "index.html"
    return render_template('index.html',table_names=table_names)

@app.route("/loaded_database", methods=['POST', 'GET'])
def uploadDB():
    #csvFile = request.form['']
    engine = create_engine("mysql+pymysql://b07b4484224a54:edf76401@us-cdbr-east-06.cleardb.net/heroku_daac59f6173f49a")
    table_name = request.form['selectdb']
    basedir = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    os.chdir(filepath)
    #df1 = pd.read_csv(csvFile+".csv")
    table_df1 = pd.read_sql_table(table_name,con=engine)
    col_names = df1.columns.values[1:]
    xmin = df1["Wavelength"].min()
    xmax = df1["Wavelength"].max()
    xRange = [xmin, xmax]
    dx = ''
    paramStr = col_names.tolist()
    flagLgd=True
    #if csvFile=='curv_dec' or csvFile=='curv_dec':
    varControl=''
    dataJSON, layoutJSON, nameFig = gm(paramStr,xRange,dx,flagLgd,varControl,csvFile)
    return render_template('generalPlot.html', paramStr=paramStr, dataJSON=dataJSON, layoutJSON=layoutJSON, csvFile=csvFile)



@app.route("/upload", methods=['POST', 'GET'])
def uploader():
    #if request.method == 'POST':
        uploaded_files = request.files.getlist('archivo')
        isCurv= request.form.get('isCurv')
        basedir = os.path.abspath(os.path.dirname(__file__))
        filepath = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
        for file in uploaded_files:
            # obtenemos el archivo del input "archivo"
            filename = secure_filename(file.filename)
            # Guardamos el archivo en el directorio "Uploads"
            file.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))
        os.chdir(filepath)
        filesCSV = glob.glob('*.CSV')
        for i in filesCSV:
            if i=='EDFA.CSV':
                dfEDFA = pd.read_csv('EDFA.CSV', header=22, names=["xEDFA", "yEDFA"])
            elif i=='CAR.CSV' or i=='car.csv' or i=='CAR.csv' or i=='car.CSV':
                dfParam = pd.read_csv(i, skiprows=1, header=None, names=["fileName", "param"])
        #dfEDFA = pd.read_csv('EDFA.CSV', header=22, names=["xEDFA", "yEDFA"])
        #dfEDFA = pd.read_csv('./Uploads/' +'EDFA.csv', header=22, names=["xEDFA", "yEDFA"])
        #dfEDFA = pd.read_csv(filepath + '/EDFA.CSV', header=22, names=["xEDFA", "yEDFA"])
        xmin = dfEDFA["xEDFA"].min()
        xmax = dfEDFA["xEDFA"].max()
        xRange = [xmin, xmax]
        dx = ''
        #dfParam = pd.read_csv('./Uploads/'+'car.csv', skiprows=1, header=None, names=["fileName", "param"])
        #dfParam = pd.read_csv(filepath + '/CAR.CSV', skiprows=1, header=None, names=["fileName", "param"])
        param = dfParam["param"].tolist()
        if isCurv:
            curv = fu.Dist2Curv(param)
            dfParam["param"]=curv
        df = fu.CreateTxDataFrame(filepath, dfEDFA, dfParam)  # require EDFA and fileName
        csvfile="dataAll"
        df.to_csv("dataAll.csv", index=False)
        param = dfParam["param"].values
        paramStr = [str(x) for x in param]
        """
        if isCurv:
            paramStr = ["%.6f" % x for x in param]
        else:
            paramStr = ["%.1f" % x for x in param]
        """
        flagLgd = True
        varControl=''
        #graphJSON = gm(paramStr, xRange, dx, flagLgd, varControl)
        dataJSON, layoutJSON, nameFig = gm(paramStr,xRange,dx, flagLgd,varControl,csvfile)
        return render_template('generalPlot.html', paramStr=paramStr, dataJSON=dataJSON, layoutJSON=layoutJSON)
#        return render_template('generalPlot.html', paramStr=paramStr, graphJSON=graphJSON)

def gm(paramStr,xRange,dx, flagLgd,varControl,csvFile):
    basedir = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    os.chdir(filepath)
    df1 = pd.read_csv(csvFile+".csv")
    x = df1["Wavelength"]
    df2 = fu.RefreshDataFrame(df1,xRange, paramStr)
    fig = fu.PlotParamIntLgd(df2,flagLgd)
    dataJSON = json.dumps(fig.data, cls=plotly.utils.PlotlyJSONEncoder)
    #graphJSON = json.dumps(fig.data, cls=plotly.utils.PlotlyJSONEncoder)
    layoutJSON = json.dumps(fig.layout, cls=plotly.utils.PlotlyJSONEncoder)
    nameFig = fu.PlotTxParam(df2, varControl, dx, 'Inc')
    return dataJSON, layoutJSON, nameFig
    #return graphJSON


if __name__ == '__main__':
    # Iniciamos la aplicación
    app.run(debug=True)
