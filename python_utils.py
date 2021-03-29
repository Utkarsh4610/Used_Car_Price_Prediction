import pickle
import joblib
import pandas as pd
import logging
logging.basicConfig(level=logging.DEBUG)

def get_rec(Rec,Loc):
    df_use = open('models/df_usex.pickle','rb')
    df_fuel = open('models/Fuel_Type_dict.pickle','rb')
    df_location = open('models/Location_dict.pickle','rb')
    df_model = open('models/Model_dict.pickle','rb')
    df_owner = open('models/Owner_Type_dict.pickle','rb')
    
    df_use = pickle.load(df_use)
    df_fuel = pickle.load(df_fuel)
    df_location = pickle.load(df_location)
    df_model = pickle.load(df_model)
    df_owner = pickle.load(df_owner)
    df_trans= {0:'Automatic',1:'Manual'}         
    
    df_new = df_use[df_use['Location']==Loc]
    df_new['Price_new'] = (Rec-df_new.Price).abs()
    df_new.sort_values(by=['Price_new'],inplace=True)
    df_new.drop(['Price_new'],axis=1,inplace=True)
    rec_arr = df_new.head(20)
    rec_arr.reset_index(drop=True,inplace=True)
    rec_arr.replace({"Model": df_model},inplace=True)
    rec_arr.replace({"Location": df_location},inplace=True)
    rec_arr.replace({"Fuel_Type": df_fuel},inplace=True)
    rec_arr.replace({"Transmission": df_trans},inplace=True)
    rec_arr.replace({"Owner_Type": df_owner},inplace=True)
    rec_arr_dict = rec_arr.to_dict(orient='records')
    return rec_arr_dict


def process_without_model(attribute_list):
    print(attribute_list)
    attribute_list = [float(i) for i in attribute_list]
    with open('models/xgboost_without_model_attribute.ml','rb') as f:
        xgmodel = joblib.load(f)
    col_names = xgmodel.get_booster().feature_names
    pred_df = pd.DataFrame([attribute_list], columns=col_names)
    prediction = xgmodel.predict(pred_df)[0]
    logging.info(f"Predicted value is: {prediction}")
    return prediction


def process_with_model(attribute_list):
    print(attribute_list)
    attribute_list = [float(i) for i in attribute_list]
    with open('models/xgboost_with_model_attribute.ml','rb') as f:
        xgmodel = joblib.load(f)
    col_names = xgmodel.get_booster().feature_names
    pred_df = pd.DataFrame([attribute_list], columns=col_names)
    prediction = xgmodel.predict(pred_df)[0]
    logging.info(f"Predicted value is: {prediction}")
    return prediction

def call_model(_data):
    """
    :param: request.form
    -> Mandatory fields: _location, _owner, _brand, _fuel, _year, 
    """
    _data = _data.to_dict()
    logging.info(f"Input dict is:{_data}")
    _location = _data.get('Loc')
    _owner = _data.get('Own')
    _brand = int(_data.get('Brand'))
    _fuel = _data.get('Fuel')
    _year = _data.get('Year')
    _model = _data.get('Model')

    # Read the null info dictionary to fill the values by Brandwise. Let us connect unsolved dots now.
    with open(f"models/null_info_brand_wise.pickle","rb") as f:
        null_info_dict = pickle.load(f)

    # Read the brand dictionary to fill the values by Brandwise.
    with open(f"models/Brand_dict.pickle","rb") as f:
        brand_dict = pickle.load(f)

    _seat = _data.get('Seats')
    if _seat == "":
        _seat = null_info_dict.get(brand_dict.get(_brand)).get('Seats')

    trans_di= {'Automatic': 0 ,'Manual': 1}
    _transmission = _data.get('Trans')
    if _transmission == "":
        _transmission = trans_di[null_info_dict.get(brand_dict.get(_brand)).get('Transmission')]

    _distance = _data.get('Dist')
    if _distance == "":
        _distance = null_info_dict.get(brand_dict.get(_brand)).get('Kilometers_Driven')

    _mileage = _data.get('Mil')
    if _mileage == "":
        _mileage = null_info_dict.get(brand_dict.get(_brand)).get('Mileage')

    _capacity = _data.get('Cap')
    if _capacity == "":
        _capacity = null_info_dict.get(brand_dict.get(_brand)).get('Engine')

    _power = _data.get('Pow')
    if _power == "":
        _power = null_info_dict.get(brand_dict.get(_brand)).get('Power')

    msg = ""
    if _model == "Choose a Model Name":
        # Important Step: Create an array from above data in same sequence as model was created
        # Sequence: ['Location', 'Year', 'Kilometers_Driven', 'Fuel_Type', 'Transmission', 'Owner_Type', 'Mileage', 'Engine', 'Power', 'Seats', 'Brand']
        without_model_arr = [_location, _year, _distance, _fuel, _transmission, _owner, _mileage, _capacity, _power, _seat, _brand]
        logging.info("Model Name is not passed. Calling the model without model attribute.")
        msg = "To get more accurate result try giving Model Name and more precise parameters."
        pred_price = process_without_model(without_model_arr)
    else:
        # Important Step: Create an array from above data in same sequence as model was created
        # Sequence: ['Location', 'Year', 'Kilometers_Driven', 'Fuel_Type', 'Transmission', 'Owner_Type', 'Mileage', 'Engine', 'Power', 'Seats', 'Brand', 'Model']
        print(_model)
        with open(f"models/Model_rev_dict.pickle","rb") as f:
            model_rev_dict = pickle.load(f)
        _model = model_rev_dict.get(_model)
        with_model_arr = [_location, _year, _distance, _fuel, _transmission, _owner, _mileage, _capacity, _power, _seat, _brand, _model]
        logging.info("Model Name is passed. Calling the model with model attribute.")
        msg = "To get more accurate result try giving more precise parameters."
        if _model is None:
            logging.info("Unable to fetch Model Name. Fallback to without model.")
            pred_price = process_without_model(with_model_arr[:-1])
        else:
            pred_price = process_with_model(with_model_arr)
    
    # Get the Recommendation from the predicted price
    rec_arr = get_rec(float(pred_price), int(_location) )
    return pred_price, rec_arr, msg
