import pandas as pd
import numpy as np
import boto3

df = pd.DataFrame(['Geeks', 'For', 'Geeks', 'is','portal', 'for', 'Geeks'])
npArray = np.array([1,2,3,4,5,6,7,8,9])

s3 = boto3.client('s3')
df.to_csv('temp.csv', index = False)
s3.upload_file('temp.csv', Bucket='chen115y-test', Key='write-csv/glue-shell-job-pandas-df.csv')