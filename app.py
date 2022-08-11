import os
import pymysql
from flask import Flask, jsonify, g,abort, render_template, request, redirect, url_for, send_from_directory
# from app import app
from numpy import ndarray
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

# instancia del objeto Flask

app = Flask(__name__, static_folder='/static')
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://b9b5c80ea73822:f09bb1f5@us-cdbr-east-06.cleardb.net/heroku_a5313fa6d44ab5f'
#app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://esilva:Cr1st0_R3y@localhost/MZI_SCF_fatt'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =False

# Carpeta de subida
app.config['UPLOAD_FOLDER'] = 'Uploads'

@app.route('/downloadCSV/<path:filename>', methods=['GET', 'POST'])
def downloadCSV(filename):
    basedir = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    os.chdir(filepath)
    # Returning file from appended path
    return send_from_directory(directory=filepath, path=filename)

@app.route('/downloads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    basedir = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    os.chdir(filepath)
    # Returning file from appended path
    return send_from_directory(directory=filepath, path=filename)

@app.route('/callback', methods=['POST', 'GET'])
def cb():
    paramStr = request.form.getlist('selectValues')
    xmin = float(request.form['xmin'])
    xmax = float(request.form['xmax'])
    ymin = float(request.form['ymin'])
    ymax = float(request.form['ymax'])
    dx = int(request.form['dx'])
    xRange = [xmin, xmax]
    yRange = [ymin, ymax]
    if request.form.get('Leyenda'):
        flagLgd = True
    else:
        flagLgd = False
    table_name = request.form['table_name']
    graphJSON,nameFig = gm(paramStr, xRange, dx,yRange, flagLgd, table_name)
    return render_template('customPlot.html',graphJSON=graphJSON ,nameFig=nameFig)
    
@app.route("/")
def listingTables():
    engine = create_engine("mysql+pymysql://b9b5c80ea73822:f09bb1f5@us-cdbr-east-06.cleardb.net/heroku_a5313fa6d44ab5f")
    #engine = create_engine("mysql+pymysql://esilva:Cr1st0_R3y@localhost/MZI_SCF_fatt")
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    # renderizamos la plantilla "index.html"
    return render_template('index.html',table_names=table_names)

@app.route("/loaded_database", methods=['POST', 'GET'])
def uploadDB():
    #csvFile = request.form['']
    engine = create_engine("mysql+pymysql://b9b5c80ea73822:f09bb1f5@us-cdbr-east-06.cleardb.net/heroku_a5313fa6d44ab5f")
    #engine = create_engine("mysql+pymysql://esilva:Cr1st0_R3y@localhost/MZI_SCF_fatt")
    table_name = request.form['selectdb']
    #df1 = pd.read_csv(csvFile+".csv")
    df = pd.read_sql_table(table_name,con=engine)
    lambdaMax= fu.PointsLinearity(df, 'max')
    col_names = df.columns.values[1:]
    paramStr = col_names.tolist()
    flagLgd=True
    fig = fu.PlotParamIntLgd(df,flagLgd,table_name)
    #fig =fu.PlotSignalInt(paramStr,lambdaMax)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    #if csvFile=='curv_dec' or csvFile=='curv_dec':
    varControl=''
    return render_template('generalPlot.html', paramStr=paramStr, graphJSON=graphJSON, table_name=table_name)


@app.route("/csvtables2db", methods=['POST', 'GET'])
def loadDB():
    basedir = os.path.abspath(os.path.dirname(__file__))
    engine = create_engine("mysql+pymysql://b9b5c80ea73822:f09bb1f5@us-cdbr-east-06.cleardb.net/heroku_a5313fa6d44ab5f")
    #engine = create_engine("mysql+pymysql://esilva:Cr1st0_R3y@localhost/MZI_SCF_fatt")
    #metadata = MetaData()
    #metadata.reflect(engine)
    basedir = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    os.chdir(filepath)
    #procedimiento para crear las tablas
    df1 = pd.read_csv("curv_dec.csv")   
    df2 = pd.read_csv("curv_inc.csv")
    df3 = pd.read_csv("temp_dec.csv")
    df4 = pd.read_csv("temp_inc.csv")
    df1.to_sql('tx_curv_dec', engine, index=False)
    df2.to_sql('tx_curv_inc', engine, index=False)
    df3.to_sql('tx_temp_dec', engine, index=False)
    df4.to_sql('tx_temp_inc', engine, index=False)
    
    """
    #para borar tablas
    engine = create_engine("mysql+pymysql://b9b5c80ea73822:f09bb1f5@us-cdbr-east-06.cleardb.net/heroku_a5313fa6d44ab5f")
    #engine = create_engine("mysql+pymysql://esilva:Cr1st0_R3y@localhost/MZI_SCF_fatt")
    engine.execute("DROP table IF EXISTS Tx_curv_inc2")
    engine.execute("DROP table IF EXISTS Tx_curv_dec2")
    engine.execute("DROP table IF EXISTS Tx_temp_inc2")
    engine.execute("DROP table IF EXISTS Tx_temp_dec2")
    """
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    #for table_name in table_names:
    #    print(f"Table:{table_name}")
    # renderizamos la plantilla "index.html"
    return render_template('index.html',table_names=table_names)
    """    
    #para borar en localhost pero en cleardb no creo haya funcionado
    engine=drop_table('tx_temp_inc2', engine)
    engine=drop_table('tx_temp_dec2', engine)
    engine=drop_table('tx_curv_inc2', engine)
    engine=drop_table('tx_curv_dec2', engine)
    
    #print(table_df1)
    """
    """
    #esto vacía a tabla, pero no la borra
    with engine.connect() as conn, conn.begin():
        df = pd.read_sql('select * from Tx_curv_dec2 limit 1', con=conn)
        print (df.head())
        df.to_sql('tx_curv_dec2', con=conn, schema='MZI_SCF_fatt', if_exists='replace')
        conn.close()
    """

@app.route("/upload", methods=['POST', 'GET'])
def uploader():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('archivo')
        varControl = request.form['varControl'] #temp, bend, tors,curr
        prefix = request.form['type'] #po, tx, ld or as
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
            if i=='CAR.CSV':
                dfParam = pd.read_csv('CAR.CSV', skiprows=1, header=None, names=["fileName", "param"])
                param = dfParam["param"].tolist()
                if varControl=='curv':
                    curv = fu.Dist2Curv(param)
                    dfParam["param"]=curv
                param = dfParam["param"].tolist()
                paramStr = [str(x) for x in param]
                if param[0]<param[1]:
                    direction='inc'
                else:
                    direction='dec'
            elif i=='EDFA.CSV':
                #prefix='tx'
                dfEDFA = pd.read_csv('EDFA.CSV', header=22, names=["xEDFA", "yEDFA"])
        if prefix=='tx':
            df = fu.CreateTxDataFrame(filepath, dfEDFA, dfParam)  # require EDFA and fileName  
        elif prefix=='po' or prefix=='ld' or prefix=='as':
            df = fu.CreatePoutDataFrame(filepath, dfParam)
        xmin = df["Wavelength"].min()
        xmax = df["Wavelength"].max()
        xRange = [xmin, xmax]
        yRange = [-100, 0]
        dx = ''
        table_name =prefix+'_'+varControl+'_'+direction
        #df.to_csv("dataAll.csv", index=False)
        engine = create_engine("mysql+pymysql://b9b5c80ea73822:f09bb1f5@us-cdbr-east-06.cleardb.net/heroku_a5313fa6d44ab5f")
        #engine = create_engine("mysql+pymysql://esilva:Cr1st0_R3y@localhost/MZI_SCF_fatt")
        df1=df
        df1.to_sql(table_name, engine, index=False)
        flagLgd = True
        #graphJSON = gm(paramStr, xRange, dx, flagLgd, varControl)
        graphJSON, nameFig = gm(paramStr,xRange,dx,yRange, flagLgd,table_name)
        return render_template('generalPlot.html', paramStr=paramStr, graphJSON=graphJSON, table_name=table_name)
     
def gm(paramStr,xRange,dx, yRange, flagLgd,table_name):
    engine = create_engine("mysql+pymysql://b9b5c80ea73822:f09bb1f5@us-cdbr-east-06.cleardb.net/heroku_a5313fa6d44ab5f")
    #engine = create_engine("mysql+pymysql://esilva:Cr1st0_R3y@localhost/MZI_SCF_fatt")
    df1 = pd.read_sql_table(table_name,con=engine)
    basedir = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    os.chdir(filepath)
    #df1 = pd.read_csv(csvFile+".csv")
    xmin = df1["Wavelength"].min()
    xmax = df1["Wavelength"].max()
    ymin = -80
    ymax = 0
    #xRange = [xmin, xmax]
    df2 = fu.RefreshDataFrame(df1,xRange, paramStr)
    df2.to_csv("dataAll.csv", index=False)
    fig = fu.PlotParamIntLgd(df2,flagLgd,table_name)
    #dataJSON = json.dumps(fig.data, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    #layoutJSON = json.dumps(fig.layout, cls=plotly.utils.PlotlyJSONEncoder)
    nameFig = fu.PlotTxParam(df2, xRange,dx, yRange,table_name)
    #return dataJSON, layoutJSON, nameFig
    return graphJSON,nameFig

@app.route("/erase_table", methods=['POST', 'GET'])
def eraseTable():
    table_name = request.form['erase_db']
    # para borrar tabla
    engine = create_engine("mysql+pymysql://b9b5c80ea73822:f09bb1f5@us-cdbr-east-06.cleardb.net/heroku_a5313fa6d44ab5f")
    #engine = create_engine("mysql+pymysql://esilva:Cr1st0_R3y@localhost/MZI_SCF_fatt")
    engine.execute("DROP table IF EXISTS "+table_name)
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    #for table_name in table_names:
    #    print(f"Table:{table_name}")
    # renderizamos la plantilla "index.html"
    return render_template('index.html',table_names=table_names)

if __name__ == '__main__':
    # Iniciamos la aplicación
    app.run(debug=True)
