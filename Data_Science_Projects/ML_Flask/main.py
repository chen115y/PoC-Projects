from flask import Flask, jsonify, abort, make_response, request
# This module depends on the occupation and level classifier modules.
# Adjust the following two lines of codes if needed to import the occupation and level modules correctly
from model.occupationclassifier import OccupationModel
from model.joblevelclassifier import LevelModel
import nltk
import pandas as pd
import snowflake.connector
from snowflake.connector import ProgrammingError
import os

app = Flask(__name__)

nltk.download("stopwords")
nltk.download('wordnet')
nltk.download('omw')
nltk.download('punkt')
hcs_model = OccupationModel()
level_model = LevelModel()

country_code_map = pd.read_csv('country_code_map.csv', header="infer")

# ---Configure this environment variable via app.yaml---
SF_USERNAME = os.environ['SF_USERNAME']
SF_PASSWORD = os.environ['SF_PASSWORD']
SF_ACCOUNT = os.environ['SF_ACCOUNT']
SF_WAREHOUSE = os.environ['SF_WAREHOUSE']
SF_DATABASE = os.environ['SF_DATABASE']
SF_SCHEMA = os.environ['SF_SCHEMA']
SF_ROLE = os.environ['SF_ROLE']


# lookup country standard code
def get_country_code(country: str, df: pd.DataFrame) -> str:
    df = df.loc[df.req_worksite_country_c.str.strip().str.lower() == country.strip().lower()]
    if len(df) > 0:
        return df['rvt_country_code'].values[0]
    else:
        return "0"


# Load the lookup data set from Snowflake
def get_rvt_stats() -> pd.DataFrame:
    df = pd.DataFrame()
    sf_con = snowflake.connector.connect(user=SF_USERNAME, password=SF_PASSWORD, account=SF_ACCOUNT, warehouse=SF_WAREHOUSE, database=SF_DATABASE, schema=SF_SCHEMA)
    sf_cursor = sf_con.cursor()
    try:
        rule_string = "USE ROLE " + SF_ROLE + ";"
        sf_cursor.execute(rule_string)
        sf_cursor.execute("select * from rpt_rvt_stats where LOAD_DATE = (select max(LOAD_DATE) from rpt_rvt_stats) and RVT_HISTOGRAM = 'RVT Available';")
        df = sf_cursor.fetch_pandas_all()
        # log the request information for troubleshooting and bug trace
        print("Lookup data set of RPT_RVT_STATS has been successfully loaded")
    except ProgrammingError as e:  # catch all exceptions
        # log the request information for troubleshooting and bug trace
        print("Loading the lookup data set of RPT_RVT_STATS was failed")
    finally:
        sf_cursor.close()
    sf_con.close()
    # for testing
    # df = pd.read_csv("./model/scripts/rpt_rvt_stats.csv", header="infer")
    return df


# Initialize the lookup data set variable
df_rvt_stats = get_rvt_stats()


# Lookup RVT Stats information based on country, metro area, occupation and level
def lookup_rvt_info(occupation: str, level: str, country_code="USA", metro_area="National", lookup_df=df_rvt_stats):
    # find the rvt stat info accordingly
    if len(metro_area.strip()) <= 0:
        metro_area = "National"
    if len(country_code.strip()) <= 0:
        country_code = "USA"
    df = lookup_df[(lookup_df['HCS_CODE'].astype(str) == occupation) & (lookup_df['HCS_LEVEL'].astype(str) == level) & (lookup_df['AG_GEOG_SHORT_NAME'].astype(str) == metro_area) & (lookup_df['COUNTRY_CODE'].astype(str) == country_code)]
    return df


# Prompt the API usage info
@app.route('/')
def index():
    return make_response(jsonify({'method': 'POST', 'path': '/occupationlevel for prediction function or /occupationlevel/rvt_stats for RVT data refresh'}), 200)


# REST API for loading and refreshing rvt_stats data from Snowflake.
@app.route('/occupationlevel/rvt_stats', methods=['GET'])
def refresh_rvt_stats():
    global df_rvt_stats
    df_rvt_stats = get_rvt_stats()
    return make_response(jsonify({'action': 'data load from Snowflake', 'table_name': 'rvt_stats', 'row_count': str(len(df_rvt_stats)), 'status': 'successful'}), 200)


# testing for GET method
@app.route('/occupationlevel/rvt_stats/<int:row_id>', methods=['GET'])
def get_rvt_stats_id(row_id):
    if len(df_rvt_stats) > 0:
        json_data = df_rvt_stats.iloc[row_id].to_json()
        return make_response(jsonify(json_data), 200)
    else:
        return make_response(jsonify({'data': 'No data available'}), 200)


# setup error handling
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# REST API for real-time occupation and level predictions.
# This is first version. The second version would response
# more fields for RVT information, such as median bill rate,
# pay rate, market grade, etc.
@app.route('/occupationlevel', methods=['POST'])
def create_task():
    response = {}
    if not request.json or 'opportunity_id' not in request.json or 'job_title' not in request.json or 'job_description' not in request.json:
        abort(400)
    else:
        req_guid = request.json['opportunity_id']
        title = request.json['job_title']
        description = request.json.get('job_description', "")
        metro_area = request.json.get('metro_area', "National")
        country = request.json.get('country_code', "USA")
        if len(country.strip()) > 0:
            country_code = get_country_code(country.strip(), country_code_map)
        else:
            country_code = 'USA'
        # log the request information for troubleshooting and bug trace
        print('opportunity_id', req_guid, '; job_title:', title, '; job_description:', description, '; metro area:', metro_area, '; country:', country_code)
        hcs, hcs_desc, hcs_prob, hcs_group = hcs_model.predict(opportunity_id=req_guid, job_title=title, job_description=description).split(",")

        # Alyssa Spitzer updated 5/11/2020 to satisfy use case of when hcs is 00-000 all other values should return 0s
        if hcs == "00-000" or not hcs:
            level_description = "0"
            level_prob = "0"
            hcs_desc = "0"
            hcs_prob_desc = "0"
            hcs_group = "0"
        else:
            hcs_prob_desc = str(hcs_prob)
            hcs_desc = hcs + " " + hcs_desc
            # calling level model
            level, level_prob = level_model.predict(job_title=title, job_description=description).split(",")
            if level == "0":
                level_description = "0"
            elif level == "1":
                level_description = "Entry Level"
            elif level == "2":
                level_description = "Intermediate Level"
            elif level == "3":
                level_description = "Expert Level"
            else:
                level_description = "0"

        # Lookup rvt_stats info based on hcs, level, country, metro area
        df = lookup_rvt_info(hcs, level_description, country_code, metro_area, df_rvt_stats)

        if len(df) > 0:
            market_grade = str(df["MARKET_GRADE"].values[0])
            rvt_histogram = str(df["RVT_HISTOGRAM"].values[0])
            req_count = str(df["REQ_COUNT"].values[0])
            total_placements = str(df["TOTAL_PLACEMENTS"].values[0])
            active_count = str(df["ACTIVE_COUNT"].values[0])
            minimum_bill_rate = str(df["MINIMUM_BILL_RATE"].values[0])
            median = str(df["MEDIAN"].values[0])
            average_bill = str(df["AVERAGE_BILL"].values[0])
            stdev_bill = str(df["STDEV_BILL"].values[0])
            maximum_bill_rate = str(df["MAXIMUM_BILL_RATE"].values[0])
            min_pay_rate = str(df["MIN_PAY_RATE"].values[0])
            appx_median_pay_rate = str(df["APPX_MEDIAN_PAY_RATE"].values[0])
            max_pay_rate = str(df["MAX_PAY_RATE"].values[0])
            open_positions = str(df["OPEN_POSITIONS"].values[0])
            bin_size = str(df["BIN_SIZE"].values[0])
            premium_skills_list = str(df["PREMIUM_SKILLS_LIST"].values[0])
            premium_rate_list = str(df["PREMIUM_RATE_LIST"].values[0])
            percentage_markup_list = str(df["PERCENTAGE_MARKUP_LIST"].values[0])
            premium_fields = str(df["PREMIUM_FIELDS"].values[0])
            total_placements_wo_outlier = str(df["TOTAL_PLACEMENTS_WO_OUTLIER"].values[0])
            active_count_without_outlier = str(df["ACTIVE_COUNT_WITHOUT_OUTLIER"].values[0])
            median_wo_outlier = str(df["MEDIAN_WO_OUTLIER"].values[0])
            average_bill_wo_outlier = str(df["AVERAGE_BILL_WO_OUTLIER"].values[0])
            stdev_bill_wo_outlier = str(df["STDEV_BILL_WO_OUTLIER"].values[0])
            maximum_bill_rate_wo_outlier = str(df["MAXIMUM_BILL_RATE_WO_OUTLIER"].values[0])
            ags_exclude_median = str(df["AGS_EXCLUDE_MEDIAN"].values[0])
        else:
            market_grade = ""
            rvt_histogram = ""
            req_count = ""
            total_placements = ""
            active_count = ""
            minimum_bill_rate = ""
            median = ""
            average_bill = ""
            stdev_bill = ""
            maximum_bill_rate = ""
            min_pay_rate = ""
            appx_median_pay_rate = ""
            max_pay_rate = ""
            open_positions = ""
            bin_size = ""
            premium_skills_list = ""
            premium_rate_list = ""
            percentage_markup_list = ""
            premium_fields = ""
            total_placements_wo_outlier = ""
            active_count_without_outlier = ""
            median_wo_outlier = ""
            average_bill_wo_outlier = ""
            stdev_bill_wo_outlier = ""
            maximum_bill_rate_wo_outlier = ""
            ags_exclude_median = ""

        # Organize the response result
        response = {
            "status": "OK",
            "message": "success",
            "opportunity_id": str(req_guid),
            "job_title": title,
            "job_description": description,
            "Occupation_Group": hcs_group,
            "Occupation": hcs_desc,
            "Occupation_confidence_value": hcs_prob_desc,
            "Experience_level": level_description,
            "Experience_level_confidence_value": str(level_prob),
            "metro_area": metro_area,
            "country_code": country,
            "market_grade": market_grade,
            "rvt_histogram": rvt_histogram,
            "req_count": req_count,
            "total_placements": total_placements,
            "active_count": active_count,
            "minimum_bill_rate": minimum_bill_rate,
            "median": median,
            "average_bill": average_bill,
            "stdev_bill": stdev_bill,
            "maximum_bill_rate": maximum_bill_rate,
            "min_pay_rate": min_pay_rate,
            "appx_median_pay_rate": appx_median_pay_rate,
            "max_pay_rate": max_pay_rate,
            "open_positions": open_positions,
            "bin_size": bin_size,
            "premium_skills_list": premium_skills_list,
            "premium_rate_list": premium_rate_list,
            "percentage_markup_list": percentage_markup_list,
            "premium_fields": premium_fields,
            "total_placements_wo_outlier": total_placements_wo_outlier,
            "active_count_without_outlier": active_count_without_outlier,
            "median_wo_outlier": median_wo_outlier,
            "average_bill_wo_outlier": average_bill_wo_outlier,
            "stdev_bill_wo_outlier": stdev_bill_wo_outlier,
            "maximum_bill_rate_wo_outlier": maximum_bill_rate_wo_outlier,
            "ags_exclude_median": ags_exclude_median
        }
    return jsonify(response)


if __name__ == '__main__':
    app.run()
