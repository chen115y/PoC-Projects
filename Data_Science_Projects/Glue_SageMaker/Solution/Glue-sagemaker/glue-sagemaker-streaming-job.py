import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import DataFrame, Row
from pyspark.sql.functions import col, udf, struct
from pyspark.sql.types import *
import datetime
from awsglue import DynamicFrame
import numpy as np
import boto3

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

## The main process start here ##
endpoint_name = "sagemaker-glue-blog-xgboost-churn"

## Define the One-hot encoding method
def OneHot_Encoding(column_name, tmp):
    categories = tmp.select(column_name).distinct().rdd.flatMap(lambda x : x).collect()
    categories.sort()
    for category in categories:
        function = udf(lambda item: 1 if item == category else 0, IntegerType())
        new_column_name = column_name + '_' + str(category)
        tmp = tmp.withColumn(new_column_name, function(col(column_name)))
    tmp = tmp.drop(column_name)
    return tmp

## Define inference/prediction method via invoking sagemaker endpoint
def get_prediction(row):
    infer_data = ','.join([str(elem) for elem in list(row)])
    sagemaker_client = boto3.client('runtime.sagemaker', 'us-east-1')
    response = sagemaker_client.invoke_endpoint(EndpointName=endpoint_name, ContentType="text/csv", Body=infer_data)
    result = response["Body"].read()
    result = result.decode("utf-8")
    return int(float(result) > 0.5)
pred_udf = udf(lambda x: get_prediction(x) if x is not None else None, IntegerType())

## @type: DataSource
## @args: [stream_type = kinesis, stream_batch_time = "100 seconds", database = "default", additionalOptions = {"startingPosition": "TRIM_HORIZON", "inferSchema": "false"}, stream_checkpoint_location = "s3://sagemaker-us-east-1-684423739646/sagemaker/DEMO-xgboost-churn/result-stream/checkpoint/", table_name = "kinesis_customer_churn"]
## @return: datasource0
## @inputs: []
data_frame_datasource0 = glueContext.create_data_frame.from_catalog(database = "default", table_name = "kinesis_customer_churn", transformation_ctx = "datasource0", additional_options = {"startingPosition": "TRIM_HORIZON", "inferSchema": "true"})
def processBatch(data_frame, batchId):
    if (data_frame.count() > 0):
        datasource0 = DynamicFrame.fromDF(data_frame, glueContext, "from_data_frame")
        # ML transformation to prepare the data for inference/prediction
        df = datasource0.toDF()
        df = df.drop('Phone','Day Charge', 'Eve Charge', 'Night Charge', 'Intl Charge', 'Churn?').select('State','Account Length','Area Code',"Int'l Plan","VMail Plan","VMail Message","Day Mins","Day Calls","Eve Mins","Eve Calls","Night Mins","Night Calls","Intl Mins","Intl Calls","CustServ Calls")
        df = OneHot_Encoding("State", df)
        df = OneHot_Encoding("Int'l Plan", df)
        df = OneHot_Encoding("VMail Plan", df)
        # Invoke SageMaker endpoint to do ML prediction
        df_pred = df.withColumn("prediction", pred_udf(struct([df[x] for x in df.columns])))
        datasource1 = DynamicFrame.fromDF(df_pred, glueContext, "datasource1")
        # Save the final results into s3 bucket
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        day = now.day
        hour = now.hour
        minute = now.minute
        path_datasink1 = "s3://sagemaker-us-east-1-<<AWS Account Number>>/sagemaker/DEMO-xgboost-churn/result-stream" + "/ingest_year=" + "{:0>4}".format(str(year)) + "/ingest_month=" + "{:0>2}".format(str(month)) + "/ingest_day=" + "{:0>2}".format(str(day)) + "/ingest_hour=" + "{:0>2}".format(str(hour)) + "/"
        datasink1 = glueContext.write_dynamic_frame.from_options(frame = datasource1, connection_type = "s3", connection_options = {"path": path_datasink1}, format = "csv", transformation_ctx = "datasink1")
glueContext.forEachBatch(frame = data_frame_datasource0, batch_function = processBatch, options = {"windowSize": "100 seconds", "checkpointLocation": "s3://sagemaker-us-east-1-<<AWS Account Number>>/sagemaker/DEMO-xgboost-churn/result-stream/checkpoint/"})
job.commit()