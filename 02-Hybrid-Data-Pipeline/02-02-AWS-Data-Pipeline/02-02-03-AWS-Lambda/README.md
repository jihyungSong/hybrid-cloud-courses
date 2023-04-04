# AWS Lambda 를 활용한 분석 데이터 저장

Athena 를 통해 추출한 데이터를 Lambda 를 통해 주기적으로 S3 에 저장하는 실습을 진행 합니다.  

1. Athena 분석 결과를 저장할 S3 버킷 생성
2. Lambda 구성
---

## 1. Athena 분석 결과를 저장할 S3 버킷 생성

분석 쿼리를 저장할 S3 버킷을 생성합니다.
S3 페이지에서 Create bucket 을 수행합니다.  

* Name : `athena-query-data-bucket`
* Region : `us-east-1`
* ACLs disabled
* Block all public access

## 2. Lambda 구성

* `Author from scratch`
* Function name : `lambda-report-function`
* Runtime : `Python 3.8`
* Execution role : `Create a new role with basic Lambda permissions`

(사전 준비)
먼저, Athena 쿼리를 저장하고, 해당 쿼리를 실행하는 Lambda 코드를 작성합니다.
쿼리는 아래 쿼리를 사용하며, Save as 를 통해 쿼리 스트링을 저장합니다.

```sql
SELECT name, COUNT(*) as count, SUM(value) as total_value 
FROM "AwsDataCatalog"."on-premise-database"."on-premise-data-table"  
WHERE name LIKE 'Jackson%'
GROUP BY name
ORDER BY count desc
```

* Query name : `jason-report-query`

저장된 쿼리의 ID 를 기억해 놓도록 합니다.

[code]
```python
import os
import json
import boto3


def lambda_handler(event, context):
    athena_client = boto3.client('athena', region_name=os.environ['AWS_REGION'])
    
    response = athena_client.get_named_query(NamedQueryId=os.environ['QUERY_ID'])
    query_string = response.get('NamedQuery', {}).get('QueryString')

    query_execution = athena_client.start_query_execution(
        QueryString=query_string,
        ResultConfiguration={
            'OutputLocation': f's3://{os.environ["S3_BUCKET"]}/'
        }
    )
    query_execution_id = query_execution.get('QueryExecutionId')
    
    return {
        'statusCode': 200,
        'body': json.dumps('Success to execute a query')
    }
```

Configuration 에서 `Environment variables` 에 다음과 같이 추가 합니다.

* QUERY_ID : `jason-report-query` 의 Query ID
* S3_BUCKET : `athena-query-data-bucket`

Permission 으로 이동하여, Execution role 에 추가 권한을 부여 하도록 합니다.
Role name 을 클릭시, IAM 페이지로 이동합니다.  
Permission 탭에서 적용되어 있는 Policy 를 편집하여, 다음 권한을 추가하도록 합니다.

```json
...(중략)

  "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "glue:GetDatabase",
                "s3:GetBucketLocation",
                "s3:GetObject",
                "s3:PutObject",
                "s3:ListBucket",
                "s3:ListMultipartUploadParts",
                "s3:AbortMultipartUpload",
                "athena:StartQueryExecution",
                "athena:GetNamedQuery",
                "glue:GetTable"
            ],
            "Resource": "*"
        },
  ]
```

모든 설정이 완료 되었다면, `Test` 탭으로 이동하여, `Test` 버튼을 눌러 Lambda 코드를 invoke 해보도록 합니다. 
정상 실행 여부 확인을 위해 Athena 페이지로 이동하여, `Recent queries` 항목을 확인해 보고, Status 를 통해 정상적으로 쿼리가 `Completed` 되었는지 확인 합니다.  
또한, S3 Bucket 을 확인하여 쿼리 결과가 CSV 로 잘 적재 되었는지도 확인합니다.  

이상 없이 실행되었다면, Lambda 페이지로 이동하 `Add trigger` 를 눌러 아래와 같이 설정 하여, Lambda 코드가 매일 정오에 주기적으로 실행되도록 합니다.  

* Trigger : `EventBridge (CloudWatch Events)`
* Rule : `Create a new rule`
* Rule name : `daily-athena-query`
* Rule type : `Schedule expression`
* Schedule expression : `cron(0 12 * * ? *)`
