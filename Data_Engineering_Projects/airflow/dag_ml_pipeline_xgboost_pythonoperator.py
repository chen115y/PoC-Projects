import boto3
import sagemaker
# from sagemaker.workflow.airflow import training_config, transform_config_from_estimator
import airflow
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from sagemaker.inputs import TrainingInput

sess = sagemaker.Session()
region = 'us-east-1'
role = 'AWSGlueServiceSageMakerNotebookRole-job-testing'
container = sagemaker.image_uris.retrieve('xgboost', region, version='1.0-1')

s3_input_train = TrainingInput(s3_data='s3://chen115y-test/sonar-data/train/train.csv', content_type='csv')
s3_input_validation = TrainingInput(s3_data='s3://chen115y-test/sonar-data/validation/validation.csv', content_type='csv')

def training_process(instancetype, **context):
    estimator = sagemaker.estimator.Estimator(image_uri=container, role=role,
                        train_instance_count=1,
                        train_instance_type=instancetype, # "ml.m4.xlarge",
                        train_volume_size=30,
                        train_max_run=3600,
                        output_path="s3://chen115y-test/sonar-data/output/",  # replace
                        base_job_name="airflow-xgboost-sonar",
                        sagemaker_session=sess)

    estimator.set_hyperparameters(max_depth=5,
                            eta=0.2,
                            gamma=4,
                            min_child_weight=2,
                            subsample=0.8,
                            objective='multi:softmax',
                            early_stopping_rounds=5,
                            num_class=2,
                            num_round=100)
    estimator.fit({'train': s3_input_train, 'validation': s3_input_validation}, wait=True) 
    return estimator.latest_training_job.job_name

def glue_process(workertype, **context):
    client = boto3.client("glue")
    response = client.start_job_run(
        JobName='glue-shell-job-pandas-test',
        Timeout=2880,
        MaxCapacity=1.0 #   WorkerType=workertype, #  NumberOfWorkers=1
    )
    return response


def transform_job(workertype, **context):
    client = boto3.client("sagemaker")
    response = client.create_transform_job(
        TransformJobName='xgboost-sonar-classification-airflow',
        ModelName='xgboost-2021-02-24-04-53-28-334',
        BatchStrategy='MultiRecord',
        TransformInput={
            'DataSource': {
                'S3DataSource': {
                    'S3DataType': 'S3Prefix',
                    'S3Uri': 's3://chen115y-test/sonar-data/inference/inference.csv'
                }
            },
            'ContentType': 'text/csv',
            'CompressionType': 'None',
            'SplitType': 'Line'
        },
        TransformOutput={
            'S3OutputPath': 's3://chen115y-test/sonar-data/batch-inference'
        },
        TransformResources={
            'InstanceType': workertype,
            'InstanceCount': 1
        }
    )
    return response


default_args = {
    'owner': 'Ivan_Chen',
    'start_date': airflow.utils.dates.days_ago(2),
    'provide_context': True
}

dag = DAG('ml_flow_python_operator', default_args=default_args, schedule_interval=None)

# dummy operator
# init = DummyOperator(
#     task_id='start',
#     dag=dag
# )

init = PythonOperator(
    task_id = 'glue-job',
    python_callable = glue_process,
    op_args=['Standard'],
    provide_context=True,
    dag=dag
)

train_op = PythonOperator(
    task_id='training',
    python_callable=training_process,
    op_args=["ml.m4.xlarge"],
    provide_context=True,
    dag=dag)

transform_op = PythonOperator(
    task_id='batch-transformation',
    python_callable=transform_job,
    op_args=["ml.m4.xlarge"],
    provide_context=True,
    dag=dag)

init.set_downstream(train_op)
transform_op.set_upstream(train_op)