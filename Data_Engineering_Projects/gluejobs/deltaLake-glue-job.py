import sys
import os
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.types import *
import datetime
from awsglue import DynamicFrame

os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages io.delta:delta-core_2.11:0.6.1 --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog"'
## @params: [JOB_NAME]

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()

sc.addPyFile("s3://chen115y-jar-deltalake/delta-core_2.11-0.6.1.jar")
glueContext = GlueContext(sc)
spark = glueContext.spark_session

job = Job(glueContext)
job.init(args['JOB_NAME'], args)

conf = spark.sparkContext._conf.setAll([('spark.delta.logStore.class','org.apache.spark.sql.delta.storage.S3SingleDriverLogStore'),('fs.s3a.impl','org.apache.hadoop.fs.s3a.S3AFileSystem'),('fs.s3.impl','org.apache.hadoop.fs.s3a.S3AFileSystem'),('fs.s3n.impl','org.apache.hadoop.fs.s3a.S3AFileSystem'),('fs.AbstractFileSystem.s3.impl','org.apache.hadoop.fs.s3a.S3A'),('fs.AbstractFileSystem.s3n.impl','org.apache.hadoop.fs.s3a.S3A'),('fs.AbstractFileSystem.s3a.impl','org.apache.hadoop.fs.s3a.S3A')])
from delta.tables import *
## Read from catalog
nbindicatorDyF = glueContext.create_dynamic_frame.from_catalog(database="sampledb", table_name="deltalake_testdata")
nbindicatorDF = nbindicatorDyF.toDF()
# nbindicatorDF.printSchema()
## Write to target as delta target
nbindicatorDFInserts = nbindicatorDF.filter("op = 'I'")
nbindicatorDFUpDel = nbindicatorDF.filter("op in ('U','D')")
nbindicatorDFInserts.write.format("delta").save("s3a://chen115y-test/deltalake-target-data/data-extract")
# create manifest file
deltaTable = DeltaTable.forPath(spark,"s3a://chen115y-test/deltalake-target-data/data-extract")
deltaTable.generate("symlink_format_manifest")
# merge data for delta lake for certain columns
# deltaTable.alias("t").merge(
#     nbindicatorDFUpDel.alias("s"),
#     "s.id = t.id") \
#   .whenMatchedDelete(condition = "s.op = 'D'") \
#   .whenMatchedUpdate(set = {"op" : "s.op",
#                             "calculation" : "s.calculation",
#                             "sequence" : "s.sequence",
#                             "lastupdated" : "s.lastupdated"
#                            } ) \
#   .whenNotMatchedInsert(
#         condition = "s.op ='I'",
#         values = {
#         "op" : "s.op",
#         "id" : "s.id",
#         "calculation" : "s.calculation",
#         "sequence" : "s.sequence",
#         "lastupdated" : "s.lastupdated"
#         }
#    ).execute()

# merge data for delta lake for all columns
deltaTable.alias("t").merge(
    nbindicatorDFUpDel.alias("s"),
    "s.id_bb_unique = t.id_bb_unique") \
  .whenMatchedDelete(condition = "s.op = 'D'") \
  .whenMatchedUpdateAll() \
  .whenNotMatchedInsertAll()\
  .execute()

# re-generate mainfest with changed data
# deltaTable = DeltaTable.forPath(spark,"s3a://chen115y-test/deltalake-target-data/data-extract")
deltaTable.generate("symlink_format_manifest")

job.commit()