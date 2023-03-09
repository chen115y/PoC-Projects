# This module depends on the occupation and level classifier modules.
# Adjust the following two lines of codes if needed to import the occupation and level modules correctly
from model.occupationclassifier import OccupationModel
from model.joblevelclassifier import LevelModel
import pandas as pd
import numpy as np
import pyarrow
import nltk
import sys
from os import path
import multiprocessing as mp
import datetime

# this sounds like a good number of data for each CPU to handle :)
BLOCK_SIZE = 20000
start_time = datetime.datetime.now()


def df_split(df: pd.DataFrame, block_size: int) -> list:
    """
    This function is to split the data frame equally
    df: input data frame
    block_size: the size of data block after splitting
    return: a list of small data frames after splitting
    """
    result = []
    if len(df) > 0:
        counter = (len(df) // block_size) + 1
        if counter > 0:
            result = np.array_split(df, counter)
        else:
            result.append(df)
    else:
        print("The input data frame doesn't exist!")
        result = []
    return result


def level_model_predict(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function is a wrapper of level model prediction with a given small data frame
    df: the input small data frame
    return: the prediction data frame
    """
    if len(df) > 0:
        level_model = LevelModel()
        predicted = level_model.predict_df("", df)
        # print("The prediction on data block of", len(predicted), "has been processed!")
        return predicted
    else:
        return pd.DataFrame()


def occupation_model_predict(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function is a wrapper of level model prediction with a given small data frame
    df: the input small data frame
    return: the prediction data frame
    """
    if len(df) > 0:
        hcs_model = OccupationModel()
        predicted = hcs_model.predict_df("", df)
        # print("The prediction on data block of", len(predicted), "has been processed!")
        return predicted
    else:
        return pd.DataFrame()


def main_process(input_data: str, output_data: str, flag: str = None):
    global start_time
    if input_data and path.exists(input_data):
        if flag == '--all' or flag is None or flag == '--occupation':
            print('Starting Occupation Prediction ... ')
            nltk.download("stopwords")
            nltk.download('wordnet')
            nltk.download('omw')
            nltk.download('punkt')
            start_time = datetime.datetime.now()
            first_df = pd.read_parquet(input_data, engine='pyarrow')
            tmp = df_split(first_df, BLOCK_SIZE)
            pool = mp.Pool(mp.cpu_count())
            df_results = pool.map(occupation_model_predict, tmp)
            result_final = pd.concat(df_results)
            pool.close()
            pool.join()
        else:
            result_final = pd.DataFrame()
        if flag == '--all' or flag is None or flag == '--level':
            print('Starting Level Prediction ... ')
            start_time = datetime.datetime.now()
            if len(result_final) == 0:
                result_final = pd.read_parquet(input_data, engine='pyarrow')
            tmp = df_split(result_final, BLOCK_SIZE)
            pool = mp.Pool(mp.cpu_count())
            df_results = pool.map(level_model_predict, tmp)
            result_final = pd.concat(df_results)
            pool.close()
            pool.join()
        if result_final is not None and len(result_final) > 0:
            result_final.to_parquet(output_data, index=False, engine='pyarrow')
            print("Total", len(result_final), "data records have been successfully saved into file of", output_data)
        else:
            print("Something Wrong! Nothing to save!")
        print('Time Taken:', (datetime.datetime.now() - start_time))
    else:
        print("The input data file doesn't exist!")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        input_datafile = sys.argv[1]
        output_datafile = sys.argv[2]
        main_process(input_datafile, output_datafile)
    elif len(sys.argv) == 4:
        input_datafile = sys.argv[1]
        output_datafile = sys.argv[2]
        indicator = sys.argv[3]
        main_process(input_datafile, output_datafile, indicator)
    else:
        print("The wrong arguments!")
