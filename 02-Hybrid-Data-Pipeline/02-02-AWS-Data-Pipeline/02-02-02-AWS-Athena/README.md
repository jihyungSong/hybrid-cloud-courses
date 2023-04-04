# AWS Athena 를 활용한 데이터 분석

S3 에 저장된 데이터를 AWS Athena 를 활용해 Query 로 분석하는 실습입니다.

1. AWS Glue 를 활용한 Data Source 구성
2. AWS Athena 를 활용한 Query 실습
---

## 1. AWS Glue 를 활용한 Data Source 구성

AWS Glue 는 S3 에 저장된 데이터를 손쉽게 추출하고 변환 적재하는 ETL 서비스 입니다.  
서버리스 이기 때문에 별도로 서버를 관리하거나 운영할 필요가 없다는 장점이 있습니다.  

On-premise 를 통해 S3 에 저장된 데이터를 Athena 를 통해 쿼리 분석을 하기 위해 Data Source 로 활용할 수 있도록 Glue Data Catalog 를 이용합니다.  

AWS Glue 페이지로 이동하여, Databases 메뉴 에서 `Add database` 를 수행합니다.  

* Name : `on-premise-database`

Athena 페이지로 이동하여 `Data sources` 메뉴로 이동하여 `Create data source` 를 수행합니다.

* Data source : `S3 - AWS Glue Data Catalog` 선택
* Choose an AWS Glue Data Catalog : `AWS Glue Data Catalog in this account` 선택
* Choose a way to create a table : `Create a table manually` 선택
* Table name : `on-premise-data-table`
* Choose an existing database : `on-premise-data` 선택
* Dataset : `Browse S3` 를 통해 `on-premise-data` 선택
* Table type : `Apache Hive`
* File format : `JSON`
* SerDe library : `org.openx.data.jsonserde.JsonSerDe`
* Column details : 

```JSON
{
  "name": "Sophia Taylor", 
  "id": "JLRQJ", 
  "ip": "22.78.103.189", 
  "latitude": "-41.50424331102771", 
  "longitude": "31.585450221675416", 
  "value": 1.675371043244104, 
  "created_at": "2023-04-01 09:40:10"
}
```

Column 정보는 JSON 파일 포맷 정보를 기반으로 설정 합니다.  

| Column # | Name       | Data type | partition key |
|----------|------------|-----------|---------------|
| 1        | id         | string    | O             |
| 2        | name       | string    |               |
| 3        | ip         | string    |               |
| 4        | latitude   | string    |               |
| 5        | longitude  | string    |               |
| 6        | value      | float     |               |
| 7        | created_at | date      |               |



## 2. AWS Athena 를 활용한 Query 실습

설정한 Data Source 를 기반으로 Athena 를 통해 Query 를 실행하여 원하는 데이터를 추출해 봅니다.  
Amazon Athena 페이지에서 `Query editor` 메뉴로 이동합니다.  
Editor 탭에서 다음과 같이 쿼리를 수행합니다.  

```sql
SELECT * 
FROM "AwsDataCatalog"."on-premise-database"."on-premise-data-table" 
LIMIT 10;
```

Query results 에서 S3 로 부터 추출한 데이터 결과를 확인 가능합니다.  

다음 쿼리를 통해, Jackson 이라는 이름을 가진 사람 별 총 합과 그들의 value 값 총합을 total_value 내림 차순으로 정렬한 결과를 확인해 봅시다.  
```sql
SELECT name, COUNT(*) as count, SUM(value) as total_value 
FROM "on-premise-data-table" 
WHERE name LIKE 'Jackson%'
GROUP BY name
ORDER BY total_value desc;
```

