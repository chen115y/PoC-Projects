from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators import HttpSensor, S3KeySensor
from airflow.contrib.operators.aws_athena_operator import AWSAthenaOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
from io import StringIO
from io import BytesIO
from time import sleep
import csv
import requests
import json
import boto3
import zipfile
import io
s3_bucket_name = 'my-bucket'
s3_key='files/'
redshift_cluster='my-redshift-cluster'
redshift_db='dev'
redshift_dbuser='awsuser'
redshift_table_name='movie_demo'
test_http='https://grouplens.org/datasets/movielens/latest/'
download_http='http://files.grouplens.org/datasets/movielens/ml-latest-small.zip'
athena_db='demo_athena_db'
athena_results='athena-results/'
create_athena_movie_table_query="""
CREATE EXTERNAL TABLE IF NOT EXISTS Demo_Athena_DB.ML_Latest_Small_Movies (
  `movieId` int,
  `title` string,
  `genres` string 
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES (
  'serialization.format' = ',',
  'field.delim' = ','
) LOCATION 's3://my-bucket/files/ml-latest-small/movies.csv/ml-latest-small/'
TBLPROPERTIES (
  'has_encrypted_data'='false',
  'skip.header.line.count'='1'
); 
"""
create_athena_ratings_table_query="""
CREATE EXTERNAL TABLE IF NOT EXISTS Demo_Athena_DB.ML_Latest_Small_Ratings (
  `userId` int,
  `movieId` int,
  `rating` int,
  `timestamp` bigint 
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES (
  'serialization.format' = ',',
  'field.delim' = ','
) LOCATION 's3://my-bucket/files/ml-latest-small/ratings.csv/ml-latest-small/'
TBLPROPERTIES (
  'has_encrypted_data'='false',
  'skip.header.line.count'='1'
); 
"""
create_athena_tags_table_query="""
CREATE EXTERNAL TABLE IF NOT EXISTS Demo_Athena_DB.ML_Latest_Small_Tags (
  `userId` int,
  `movieId` int,
  `tag` int,
  `timestamp` bigint 
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES (
  'serialization.format' = ',',
  'field.delim' = ','
) LOCATION 's3://my-bucket/files/ml-latest-small/tags.csv/ml-latest-small/'
TBLPROPERTIES (
  'has_encrypted_data'='false',
  'skip.header.line.count'='1'
); 
"""
join_tables_athena_query="""
SELECT REPLACE ( m.title , '"' , '' ) as title, r.rating
FROM demo_athena_db.ML_Latest_Small_Movies m
INNER JOIN (SELECT rating, movieId FROM demo_athena_db.ML_Latest_Small_Ratings WHERE rating > 4) r on m.movieId = r.movieId
"""
def download_zip():
    s3c = boto3.client('s3')
    indata = requests.get(download_http)
    n=0
    with zipfile.ZipFile(io.BytesIO(indata.content)) as z:       
        zList=z.namelist()
        print(zList)
        for i in zList: 
            print(i) 
            zfiledata = BytesIO(z.read(i))
            n += 1
            s3c.put_object(Bucket=s3_bucket_name, Key=s3_key+i+'/'+i, Body=zfiledata)
def clean_up_csv_fn(**kwargs):    
    ti = kwargs['task_instance']
    queryId = ti.xcom_pull(key='return_value', task_ids='join_athena_tables' )
    print(queryId)
    athenaKey=athena_results+"join_athena_tables/"+queryId+".csv"
    print(athenaKey)
    cleanKey=athena_results+"join_athena_tables/"+queryId+"_clean.csv"
    s3c = boto3.client('s3')
    obj = s3c.get_object(Bucket=s3_bucket_name, Key=athenaKey)
    infileStr=obj['Body'].read().decode('utf-8')
    outfileStr=infileStr.replace('"e"', '') 
    outfile = StringIO(outfileStr)
    s3c.put_object(Bucket=s3_bucket_name, Key=cleanKey, Body=outfile.getvalue())
def s3_to_redshift(**kwargs):    
    ti = kwargs['task_instance']
    queryId = ti.xcom_pull(key='return_value', task_ids='join_athena_tables' )
    print(queryId)
    athenaKey='s3://'+s3_bucket_name+"/"+athena_results+"join_athena_tables/"+queryId+"_clean.csv"
    print(athenaKey)
    sqlQuery="copy "+redshift_table_name+" from '"+athenaKey+"' iam_role 'arn:aws:iam::163919838948:role/myRedshiftRole' CSV IGNOREHEADER 1;"
    print(sqlQuery)
    rsd = boto3.client('redshift-data')
    resp = rsd.execute_statement(
        ClusterIdentifier=redshift_cluster,
        Database=redshift_db,
        DbUser=redshift_dbuser,
        Sql=sqlQuery
    )
    print(resp)
    return "OK"
def create_redshift_table():
    rsd = boto3.client('redshift-data')
    resp = rsd.execute_statement(
        ClusterIdentifier=redshift_cluster,
        Database=redshift_db,
        DbUser=redshift_dbuser,
        Sql="CREATE TABLE IF NOT EXISTS "+redshift_table_name+" (title	character varying, rating	int);"
    )
    print(resp)
    return "OK"
DEFAULT_ARGS = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False 
}
with DAG(
    dag_id='movie-list-dag',
    default_args=DEFAULT_ARGS,
    dagrun_timeout=timedelta(hours=2),
    start_date=days_ago(2),
    schedule_interval='*/10 * * * *',
    tags=['athena','redshift'],
) as dag:
    check_s3_for_key = S3KeySensor(
        task_id='check_s3_for_key',
        bucket_key=s3_key,
        wildcard_match=True,
        bucket_name=s3_bucket_name,
        s3_conn_id='aws_default',
        timeout=20,
        poke_interval=5,
        dag=dag
    )
    files_to_s3 = PythonOperator(
        task_id="files_to_s3",
        python_callable=download_zip
    )
    create_athena_movie_table = AWSAthenaOperator(task_id="create_athena_movie_table",query=create_athena_movie_table_query, database=athena_db, output_location='s3://'+s3_bucket_name+"/"+athena_results+'create_athena_movie_table')
    create_athena_ratings_table = AWSAthenaOperator(task_id="create_athena_ratings_table",query=create_athena_ratings_table_query, database=athena_db, output_location='s3://'+s3_bucket_name+"/"+athena_results+'create_athena_ratings_table')
    create_athena_tags_table = AWSAthenaOperator(task_id="create_athena_tags_table",query=create_athena_tags_table_query, database=athena_db, output_location='s3://'+s3_bucket_name+"/"+athena_results+'create_athena_tags_table')
    join_athena_tables = AWSAthenaOperator(task_id="join_athena_tables",query=join_tables_athena_query, database=athena_db, output_location='s3://'+s3_bucket_name+"/"+athena_results+'join_athena_tables')
    create_redshift_table_if_not_exists = PythonOperator(
        task_id="create_redshift_table_if_not_exists",
        python_callable=create_redshift_table
    )
    clean_up_csv = PythonOperator(
        task_id="clean_up_csv",
        python_callable=clean_up_csv_fn,
        provide_context=True     
    )
    transfer_to_redshift = PythonOperator(
        task_id="transfer_to_redshift",
        python_callable=s3_to_redshift,
        provide_context=True     
    )
    check_s3_for_key >> files_to_s3 >> create_athena_movie_table >> join_athena_tables >> clean_up_csv >> transfer_to_redshift
    files_to_s3 >> create_athena_ratings_table >> join_athena_tables
    files_to_s3 >> create_athena_tags_table >> join_athena_tables
    files_to_s3 >> create_redshift_table_if_not_exists >> transfer_to_redshift