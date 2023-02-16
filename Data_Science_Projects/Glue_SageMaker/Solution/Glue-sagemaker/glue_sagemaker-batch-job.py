import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
import boto3
from pyspark.context import SparkContext
from pyspark.sql.functions import col, udf, struct
from pyspark.sql.types import *

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# get job parameter values
region = 'us-east-1'
s3_target = 's3://sagemaker-us-east-1-<<AWS account number>>/sagemaker/DEMO-xgboost-churn/result/'
s3_source = 's3://sagemaker-us-east-1-<<AWS account number>>/sagemaker/DEMO-xgboost-churn/churndata/churn.txt'
endpoint_name = 'sagemaker-glue-blog-xgboost-churn'

# read data from source
df = spark.read.option("header", True).csv(s3_source)
df = df.drop('Phone','Day Charge', 'Eve Charge', 'Night Charge', 'Intl Charge', 'Churn?') \
       .select('State','Account Length','Area Code',"Int'l Plan","VMail Plan","VMail Message","Day Mins","Day Calls","Eve Mins","Eve Calls","Night Mins","Night Calls","Intl Mins","Intl Calls","CustServ Calls")
# df.printSchema()

def OneHot_Encoding(column_name, tmp):
    categories = tmp.select(column_name).distinct().rdd.flatMap(lambda x : x).collect()
    categories.sort()
    for category in categories:
        function = udf(lambda item: 1 if item == category else 0, IntegerType())
        new_column_name = column_name + '_' + category
        tmp = tmp.withColumn(new_column_name, function(col(column_name)))
    tmp = tmp.drop(column_name)
    return tmp

df = OneHot_Encoding("State", df)
df = OneHot_Encoding("Int'l Plan", df)
df = OneHot_Encoding("VMail Plan", df)

def get_prediction(row):
    infer_data = ','.join([str(elem) for elem in list(row)])
    runtime_client = boto3.client('runtime.sagemaker', region)
    response = runtime_client.invoke_endpoint(EndpointName=endpoint_name, ContentType="text/csv", Body=infer_data)
    result = response["Body"].read()
    result = result.decode("utf-8")
    return int(float(result) > 0.5)

pred_udf = udf(lambda x: get_prediction(x) if x is not None else None, IntegerType())
df_result = df.withColumn("prediction", pred_udf(struct([df[x] for x in df.columns])))

applymapping1 = DynamicFrame.fromDF(df_result, glueContext, 'applymapping1')
datasink2 = glueContext.write_dynamic_frame.from_options(frame = applymapping1, connection_type = "s3", connection_options = {"path": s3_target}, format = "csv", transformation_ctx = "datasink2")

job.commit()
