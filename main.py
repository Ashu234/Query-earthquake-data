from flask import Flask, render_template, request, redirect, url_for, session
from azure.storage.blob import BlockBlobService
from azure.storage.blob import PublicAccess
from azure.storage.blob import ContentSettings
import mysql.connector
from mysql.connector import errorcode
import os
import csv
import random
from datetime import datetime

app = Flask(__name__)
#clone successfull
config = {
  'host':'myserver-mysql-ashu.mysql.database.azure.com',
  'user':'root123@myserver-mysql-ashu',
  'password':'Superman123',
  'database':'mysqlashudb',
  'ssl_ca':'BaltimoreCyberTrustRoot.crt.pem'
}

#block_blob_service = BlockBlobService(account_name='ashuazurestorage', account_key='HGvsHgPPFOp64gztvR6B9g+RNUUqzwhl+aNid8wpwca1uwejBMEhyVkP3oev1SKEnI5eeq4EIXWfcvzWjxAjuQ==')
#block_blob_service.set_container_acl('ashu-blob-container', public_access=PublicAccess.Container)

@app.route('/')
def index():
  return redirect(url_for('login'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['logged_in'] = True
        session['username'] = username
        time_start = datetime.now()
        session['time'] = time_start
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/randomQueries')
def randomQueries():
  return render_template('randomQueries.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/random1000queries')
def random1000queries():
    try:
             conn = mysql.connector.connect(**config)
             print("Connection established")
    except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
              print("Something is wrong with the user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
              print("Database does not exist")
            else:
              print(err)
    else:
            cursor = conn.cursor()
            time_start = datetime.now()
            for i in range(0,500):
                randomnum = random.uniform(0,1)
                randomnum = round(randomnum, 2)
                #print("random number %s" %(randomnum))
                #result = cursor.execute("SELECT mag FROM earthquake_table WHERE mag >= %s AND mag <= %s ;", (randomnum,randomnum+1.0))
                result = cursor.execute("SELECT mag FROM earthquake_table WHERE mag = %s ;", [randomnum])
                articles = cursor.fetchall()
            cursor.close()
            conn.close()
            time_end = datetime.now()
    time_diff = time_end - time_start
    return render_template('complete.html', time_diff=time_diff)

@app.route('/restrictedQueries')
def restrictedQueries():
    return render_template('restrictedQueries.html')

@app.route('/searchWithinDistance', methods=['GET','POST'])
def searchWithinDistance():
    if request.method == 'POST':
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        distance = request.form['distance']
        #print("latitude %s " % (latitude))
        time_start = datetime.now()
        try:
                 conn = mysql.connector.connect(**config)
                 print("Connection established")
        except mysql.connector.Error as err:
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                  print("Something is wrong with the user name or password")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                  print("Database does not exist")
                else:
                  print(err)
        else:
                cursor = conn.cursor()
                cursor.execute("SELECT latitude, longitude, place, SQRT(POW(69.1 * (latitude - %s), 2) + POW(69.1 * (%s - longitude) * COS(latitude / 57.3), 2)) AS distance FROM earthquake_table HAVING distance < %s ORDER BY distance ;", (latitude, longitude, distance))
                result = cursor.fetchall()
                #print(result)
                cursor.close()
                conn.close()
        time_end = datetime.now()
        time_diff = time_end - time_start
        return render_template('complete.html',time_diff=time_diff)
    return render_template('searchWithinDistance.html')

@app.route('/searchInCalifornia', methods=['GET','POST'])
def searchInCalifornia():
    if request.method == 'POST':
        state = request.form['state']
        print("state %s " % (state))
        time_start = datetime.now()
        try:
                 conn = mysql.connector.connect(**config)
                 print("Connection established")
        except mysql.connector.Error as err:
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                  print("Something is wrong with the user name or password")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                  print("Database does not exist")
                else:
                  print(err)
        else:
                cursor = conn.cursor()
                # "{0} LIKE '%{1}'".format(field, value_suffix)
                query = "SELECT latitude, longitude, place FROM earthquake_table WHERE place LIKE '%{0}'".format(state)
                cursor.execute(query)
                results = cursor.fetchall()
                #print(results[0])
                cursor.close()
                conn.close()
                time_end = datetime.now()
                time_diff = time_end - time_start
                print("time_diff %s" % (time_diff))
                timediff = str(time_diff)
                print("time_diff in string %s" % (timediff))
                session['time_diff'] = timediff
                return render_template('californiaresult.html', results=results)
    return render_template('searchInCalifornia.html')

@app.route('/createDB')
def createDB():
  fileread = open('all_month.csv','rt')
  file_reader = csv.reader(fileread)
  dataMonth = []
  try:
           conn = mysql.connector.connect(**config)
           print("Connection established")
  except mysql.connector.Error as err:
          if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
          elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
          else:
            print(err)
  else:
          cursor = conn.cursor()
          time_start = datetime.now()
          cursor.execute("DROP TABLE IF EXISTS earthquake_table;")
          cursor.execute("CREATE TABLE earthquake_table(time INT(11), latitude DECIMAL(10,8), longitude DECIMAL(11,8), depth DECIMAL(5,2), mag DECIMAL(5,2), magType VARCHAR(10), nst INT, gap DECIMAL(5,4), dmin DECIMAL(10,10), rms DECIMAL(7,7), net VARCHAR(10), id VARCHAR(25), updated INT(11), place VARCHAR(50), type VARCHAR(15), horizontalError DECIMAL(5,5), depthError DECIMAL(5,5), magError DECIMAL(5,5), magNst INT, status VARCHAR(15), locationSource VARCHAR(10), magSource VARCHAR(10));")
          line = 0;
          for attr in file_reader:
              if line == 0:
                  line = 1
              else:
                  s1 = str(attr[0])
                  s2 = str(attr[12])
                  dt_obj1 = datetime.strptime(s1, '%Y-%m-%dT%H:%M:%S.%fZ')
                  dt_obj2 = datetime.strptime(s2, '%Y-%m-%dT%H:%M:%S.%fZ')
                  millisec1 = dt_obj1.timestamp() * 1000
                  millisec2 = dt_obj2.timestamp() * 1000
                  data = []
                  data.extend((millisec1, attr[1], attr[2],attr[3], attr[4], attr[5], attr[6], attr[7], attr[8], attr[9], attr[10], attr[11], millisec2, attr[13], attr[14], attr[15], attr[16], attr[17], attr[18], attr[19], attr[20], attr[21]))
                  dataMonth.append(data)
          #cursor.executemany("""INSERT INTO earthquake_table (time, latitude, longitude, depth, mag, magType, nst, gap, dmin, rms, net, id, updated, place, type, horizontalError, depthError, magError, magNst, status, locationSource, magSource) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""", [(millisec1, attr[1], attr[2],attr[3], attr[4], attr[5], attr[6], attr[7], attr[8], attr[9], attr[10], attr[11], millisec2, attr[13], attr[14], attr[15], attr[16], attr[17], attr[18], attr[19], attr[20], attr[21])])
          stmt = """INSERT INTO earthquake_table (time, latitude, longitude, depth, mag, magType, nst, gap, dmin, rms, net, id, updated, place, type, horizontalError, depthError, magError, magNst, status, locationSource, magSource) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
          cursor.executemany(stmt, dataMonth)
          conn.commit()
          cursor.close()
          conn.close()
          time_end = datetime.now()
          time_diff = time_end - time_start
  return render_template('complete.html', time_diff=time_diff)


if __name__ == '__main__':
    app.secret_key = 'mysecretkey'
    app.run(debug=True)
app.secret_key = 'secretkey'
