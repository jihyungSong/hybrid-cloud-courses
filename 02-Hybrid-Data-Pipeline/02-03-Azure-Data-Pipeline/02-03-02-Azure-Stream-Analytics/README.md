# Azure Stream Analytics 를 활용한 실시간 분석 

1. Storage Account 에서 Blob Container 생성
2. Stream Analytics Jobs 구성
3. Storage Account 에 샘플 데이터 import 후 동작 확인
---

## 1. Storage Account 에서 Blob Container 생성

먼저, Stream Analytics 에서 Input 데이터 저장소로 활용할 Container 를 구성합니다.  
이전 단계에서 File shares 를 위해 생성한 Storage Account 를 동일하게 사용합니다.  

Storage Account `dataforonpremisesvr` 를 선택하고, `Containers` 메뉴로 이동하여 `+ Container` 를 수행합니다.  

* Name : `on-prem-input-data`
* Public access level : `Private`

그리고, output 데이터 저장용 Container 도 추가로 생성합니다.  

* Name : `on-prem-output-data`
* Public access level : `Private`

## 2. Stream Analytics Jobs 구성

이제 Container 에 저장된 Object 의 데이터를 분석할 Stream Analytics Jobs 를 구성합니다.  
Stream Analytics Jobs 페이지로 이동하여 `+ Create` 를 수행합니다.

* Resource group : `azure-environment`
* Name : `on-prem-data-analytics-job`
* Region : `Korea Central`
* Hosting environment : `Cloud`
* Streaming units : 1

생성이 완료 되면, 해당 job 으로 들어가 input / output / query 를 설정합니다.  

[Input]
* Stream input : `Blob storage/ADLS Gen2`
* Input alias : `on-prem-data`
* `Select Blob storage/ADLS Gen2 from your subscriptions` 선택
* Storage account : `dataforonpremisesvr`
* Container : `Use existing` 선택 후, 이전 단계에서 생성한 `on-prem-input-data` 선택
* Event serialization format : `JSON`
* Encoding : `UTF-8`

[Output]
* `Blob storage/ADLS Gen2` 선택
* Input alias : `on-prem-output-report`
* `Select Blob storage/ADLS Gen2 from your subscriptions` 선택
* Storage account : `dataforonpremisesvr`
* Container : `Use existing` 선택 후, 이전 단계에서 생성한 `on-prem-output-data` 선택
* Event serialization format : `JSON`
* Encoding : `UTF-8`
 
[Query]
```SQL
SELECT 
    id, name, value
INTO
    [on-prem-output-report]
FROM
    [on-prem-data]
```

해당 쿼리 작성 후 테스트 해봅니다.
`Test query` 수행시 Test results 가 정상인지 확인 합니다.  

모든 설정이 완료 되었다면 `on-prem-data-analytics-job` 를 Start 합니다.  



## 3. Storage Account 에 샘플 데이터 import 후 동작 확인



