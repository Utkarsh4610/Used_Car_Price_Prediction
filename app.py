# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 03:26:03 2019
@author: Utkarsh Kumar
"""

from flask import Flask,render_template,request
import joblib
import pandas as pd
import pickle
import pandas as pd
import numpy as np
import logging
logging.basicConfig(level=logging.DEBUG)
from python_utils import get_rec, call_model
app = Flask(__name__)

@app.route('/')
def home():
	return render_template('index.html',template_folder='templates')

@app.route('/predict',methods=['POST'])

def predict():
    if request.method == 'POST':
        logging.info("Got POST request.")
        try:
            logging.info("Calling function to get prediction and Recommendation.")
            prediction, recommend_arr, msg = call_model(request.form)

            return render_template('output.html',template_folder='templates',prediction=prediction,rec_arr_dir=recommend_arr, \
                                    pr=msg)
        except Exception as e:
            logging.exception(f"Error occured: {e}")
            return render_template('lost.html',template_folder='templates')

@app.route('/recommend',methods=['POST'])
def recommend():   
    if request.method == 'POST':
        logging.info("Got Post method for Recommendation.")
        try:
            Rec = request.form['Knpr']
            Rec = float(Rec)
            Loc = request.form['Locc']
            Loc = int(Loc)
            logging.info("Creating the result.")
            recommend_arr = get_rec(Rec,Loc)
            return render_template('recommend.html',template_folder='templates',rec_arr_dir = recommend_arr)
        except Exception as e:
            logging.exception(f"Error: {e}")
            return render_template('lost.html',template_folder='templates')

            
if __name__ == '__main__':
    app.run(debug=True, port=5005)
