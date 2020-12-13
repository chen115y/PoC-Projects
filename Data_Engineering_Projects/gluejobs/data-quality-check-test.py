import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *
import boto3
from cerberus import Validator

# @params: [JOB_NAME] and s3_file
args = getResolvedOptions(sys.argv, ['JOB_NAME', 's3_schema_file'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# s3_file = "s3://chen115y-test/schema-defined-cerberus.txt"
s3_file = args['s3_schema_file']

# One way to check schema is to use open source library of cerberus and load comprehensive schema file from s3
s3 = boto3.resource('s3')
content_object = s3.Object('chen115y-test', s3_file)
file_content = content_object.get()['Body'].read().decode('utf-8')
valid_entry = [{'id': 20, 'amount': 30.97, 'user': "ivan@amazon.com", 'items': ["1", "2"], 'extr': 100}]
df = spark.createDataFrame(valid_entry)
dq_schema = eval(file_content)

results = []

V = Validator()
# schema_validator = Validator(schema)
for row in list(df.collect()):
    V.validate(row.asDict(), dq_schema)
    results.append({'id': row['id'], '': str(V.errors)})
# Save the final dataframe into s3 bucket
df_result = spark.createDataFrame(results)
df_result.write.parquet("s3a://chen115y-test/dq-results",mode="overwrite")
# dyDF_final = DynamicFrame.fromDF(df_result, glueContext, "nested")
# glueContext.write_dynamic_frame.from_options(
#                   frame = dyDF_final,
#                   connection_type = "s3",  
#                   connection_options = {"path": 's3://chen115y-test/dq-results'},
#                   format = "parquet"
#)

# Another way to check schema is to use native pyspark function of "StructType.fromJson" to load and parse schema json file from s3
s3 = boto3.client('s3')
file = s3.get_object(Bucket='chen115y-test', Key='schema-defined-pyspark.json')
saved_schema = StructType.fromJson(json.loads(file['Body'].read().decode('utf-8')))
# apply schema check to whole data set
try:
    df_with_schema = spark.createDataFrame(collection, schema=saved_schema)
except:
    print("Data doesn't follow the enforced schema!")