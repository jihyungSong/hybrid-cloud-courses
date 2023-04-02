# On-premise 와 AWS Kinesis Firehose 연동

On-premise 에서 발생된 데이터를 AWS Kinesis Firehose 를 통해 실시간으로 S3 로 전송하는 구성입니다.

1. S3 Bucket 구성
2. Kinesis Firehose 배포
3. VPC Endpoint 구성
4. On-premise 서버에 Kinesis Firehose Agent 배포 및 설정
5. S3 로 데이터 전송 확인

---
## 1. S3 Bucket 구성

On-premise 에서 발생된 데이터를 S3 에 저장하기 위해, 먼저 S3 Bucket 을 구성 합니다.  
AWS Management console 에서 S3 로 이동하여, `Create Bucket` 을 수행 합니다.

- Bucket name : `on-premise-data`
- Region : AWS VPC 를 구성한 리전 (해당 예시에서는 `US East (N. Virginia) us-east-1` 사용)
- ACLs disable
- Block all public access 체크
- Bucket Versioning : `Disable`
- Encryption key type : SSE-S3

---
## 2. Kinesis Firehose 배포

On-premise 에서 발생되는 데이터를 받아 지속적으로 S3 에 전달하는 역할인 Kinesis Firehose 를 구성 합니다.  
AWS Management console 에서 `Kinesis Data Firehose` 로 이동하여 `Create delivery stream` 을 수행 합니다.

- Source : `Direct PUT`
- Destination : `Amazon S3`
- Delivery stream name : `on-prem-stream-data`
- Destination settings 의 S3 Bucket : 이전에 생성한 `on-premise-data` 버킷 
- Dynamic partitioning : `Not enabled`

---
## 3. VPC Endpoint 구성

On-premise 에서 Kinesis Firehose 로 데이터를 전송할 때, 보통은 인터넷 구간으로 전송됩니다.  
만약, VPN 을 통해 내부 네트워크로 통신하려면, VPC Endpoint 를 구성하여 가능합니다.  

먼저, Endpoint 를 구성하기 전에 Endpoint 에서 사용할 Security Group 을 생성합니다.  
VPC 페이지에서 Security Group 항목을 통해 `Create Security Group` 을 수행합니다.  

- name : `kinesis-firehose-sg`
- VPC : `aws-vpc` 
- Inbound Rule 
  - Source : `10.10.0.0/16`
  - Type : `All trafic`
  - Protocol : `All`
  - Port range : `All`
  - Description : `On-premise`
- Tags : `Name : kinesis-firehose-sg`


Security Group 생성이 완료 되었다면, 본격적으로 VPC Endpoint 를 구성 합니다.  
VPC 메뉴로 이동 하고, `Endpoint` 항목을 통해 `Create endpoint` 를 수행 합니다.  

- Name : `kinesis-firehose-endpoint`
- Service category : `AWS services`
- Service : `com.amazonaws.us-east-1.kinesis-firehose` 선택. (firehose 로 검색)
- VPC : `aws-vpc` 선택
- Enable DNS name 체크
- DNS record IP type : `IPv4 선택`
- Subnet : `aws-vpc` 에서 설정한 모든 AZ의 Subnet 설정
- Security Group : 이전에 생성한 `kinesis-firehose-sg` 선택
- Policy : `Full access`
- Tags : `Name : kinesis-firehose-endpoint`


---
## 4. On-premise 서버에 Kinesis Firehose Agent 배포 및 설정

Kinesis Firehose 와 VPC endpoint 까지 설정을 완료 했다면,  
On-premise 에 배포한 서버로 부터 데이터를 생성하여 Kinesis Firehose 로 전달할 수 있도록 agent 를 구성하고자 합니다.  

agent 는 On-premise 인스턴스에 설치해야 합니다.  
먼저, 설치 작업 전에 필요한 사전 준비 작업 부터 수행 합니다.  

---
### (사전 작업) 4-1. Agent 가 사용할 AWS Access Key 생성

AWS IAM 으로 이동하여, IAM User 를 생성 합니다.  

- User name : `kinesis-firehose`
- Permissions options : `Attach policies directly` 선택
  - Permission policies : `AmazonKinesisFirehoseFullAccess` 선택  

`kinesis-firehose` IAM User 생성을 완료 후, 해당 User 를 선택. `Security credentials` 탭으로 이동 하여 `Create Access Key` 를 수행 합니다.

- `Application running outside AWS` 선택
- Description tag value : `AWS Kinesis Agent for On-premise Server`

Access Key 생성시, `AKI` 로 시작하는 Access Key ID 와 랜덤 스트링으로 이루어진 Secret Key 를 확인 가능 합니다.  
Secret Key 의 경우, 최초 생성 이후에는 재 확인이 불가하므로, csv 파일을 다운로드 받고 외부 유출 되지 않도록 잘 보관 합니다.  

### (사전 작업) 4-2. Kinesis Firehose 내부 통신을 위한 VPC Endpoint 의 Private IP 확인

VPC Endpoint 가 구성 되면, 해당 VPC 에 Endpoint 통신을 담당하는 ENI (Elastic Network Interface) 가 생성 되며, 내부 통신을 처리할 Private IP 가 할당되어 있습니다.  
Private IP 는 Kinesis Agent 에서 사용 될 수 있도록 확인이 필요합니다.  

VPC Endpoint 용 Private IP 확인을 위해 `EC2` 페이지로 이동하여, `Network Interfaces` 메뉴로 이동 합니다.  

검색 필터를 사용해, ENI 를 검색 합니다.  
- VPC ID : `aws-vpc` 의 VPC ID
- Interface Type : `vpc_endpoint`

위 조건으로 검색시 총 두 개의 ENI 가 검색 될 것입니다. (Endpoint 설정시 VPC에 설정된 Subnet 을 모두 선택했는데, 실습 예제에서 Subnet 을 두 개 설정 하였기 때문),  
해당 ENI 를 선택 후, 하단 정보에서 Private IPv4 address 를 알아 둡니다.  
실습 예제에서 `aws-vpc` VPC 의 IP CIDR 로 `172.16.0.0/16` 대역을 사용 하였으므로, `172.16` 대역의 IP 임을 알 수 있습니다.


---

사전 작업이 완료되었다면,  
이전 가이드에서 구성했던 On-premise 인스턴스에 SSH 로 접속합니다. ([On-premise 환경에 서버 배포 항목 참고](../../02-01-On-premise/README.md))

```shell
ssh -i <KEYPAIR_FILE_NAME> ec2-user@<EC2_PUBLIC_IP_ADDR>
```

서버 접속에 성공하면, 작업의 원할함을 위해 `ec2-user` 에서 `root` 유저로 전환 합니다.

```shell
sudo su -
```

Kinesis 로 수집된 데이터를 전달하는 `aws-kinesis-agent` 를 설치합니다.  

```shell
yum install –y aws-kinesis-agent
```

agent 설정 파일을 열어 설정을 변경합니다. 

```shell
vim /etc/aws-kinesis/agent.json

{
  "cloudwatch.emitMetrics": true,
  "firehose.endpoint": "firehose.us-east-1.amazonaws.com",
  "awsAccessKeyId": "<사전준비에서_생성한_ACCESS_Key_ID>",
  "awsSecretAccessKey": "<사전준비에서_생성한_SECRET_Key>",

  "flows": [
    {
      "filePattern": "/tmp/data.log*",
      "kinesisStream": "on-prem-stream-data", # 위에서 생성한 Kinesis stream 이름
      "partitionKeyOption": "RANDOM"
    },
    {
      "filePattern": "/tmp/data.log*",
      "deliveryStream": "on-prem-stream-data" # 위에서 생성한 Kinesis stream 이름
    }
  ]
}
```

firehose 의 Endpoint 로 설정한 도메인 명인 `firehose.us-east-1.amazonaws.com` 의 경우,  
On-premise 환경에서는 VPC Endpoint 에서 제공하는 Private DNS 를 알 수 없기 때문에  
On-premise 서버에 도메인 정보를 직접 입력 하여 줍니다.  

사전 준비 단계에서 파악한 VPC Endpoint 용 ENI 의 Private IP 를 `/etc/hosts` 파일에 등록합니다.  

```shell
vim /etc/hosts

127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
::1         localhost6 localhost6.localdomain6

172.16.10.xxx	 firehose.us-east-1.amazonaws.com
172.16.20.yyy    firehose.us-east-1.amazonaws.com
```

이제 마지막으로, AWS Kinesis Agent 를 구동합니다.

```shell
service aws-kinesis-agent start
chkconfig aws-kinesis-agent on
```

Agent 가 정상 구동 상태인지 확인 합니다.  
Active (running) 여부 확인 합니다.  

```shell
service aws-kinesis-agent status

● aws-kinesis-agent.service - LSB: Daemon for Amazon Kinesis Agent.
     Loaded: loaded (/etc/rc.d/init.d/aws-kinesis-agent; generated)
     Active: active (running) since Sat 2023-04-01 12:02:56 UTC; 14s ago
       Docs: man:systemd-sysv-generator(8)
    Process: 51073 ExecStart=/etc/rc.d/init.d/aws-kinesis-agent start (code=exited, status=0/SUCCESS)
      Tasks: 19 (limit: 1112)
     Memory: 83.5M
        CPU: 2.291s
     CGroup: /system.slice/aws-kinesis-agent.service
             ├─51081 runuser aws-kinesis-agent-user -s /bin/sh -c "/usr/bin/start-aws-kinesis-agent  "
             └─51083 /bin/java -server -Xms32m -Xmx512m -Dlog4j.configurationFile=file:///etc/aws-kinesis/log4j.xml "-XX:OnOutOfMemoryError>

Apr 01 12:02:54 ip-10-10-10-39.us-west-2.compute.internal runuser[51081]: pam_unix(runuser:session): session opened for user aws-kinesis-ag>
Apr 01 12:02:56 ip-10-10-10-39.us-west-2.compute.internal aws-kinesis-agent[51080]: [34B blob data]
Apr 01 12:02:56 ip-10-10-10-39.us-west-2.compute.internal systemd[1]: Started aws-kinesis-agent.service - LSB: Daemon for Amazon Kinesis Ag>
```

---
## 5. S3 로 데이터 전송 확인

이전 단계에서 배포한 데이터 생성 스크립트를 구동해 봅니다.  

```bash
> python3 /usr/local/bin/generate_data.py
Generate Data for Training
success to generate data...SHPDV
success to generate data...ZUECW
success to generate data...KBRUY
success to generate data...XXFUD
success to generate data...THTHF
success to generate data...ZIKPM
success to generate data...YGTAC
success to generate data...GDSWB
success to generate data...GUXJA
success to generate data...NLQYT
success to generate data...PJYOL
```

해당 스크립트 구동시, 주기적으로 데이터를 발생시키며, /tmp/data.log 파일에 기록되게 됩니다.  
이 파일의 정보를 확인 하여, AWS Kinesis agent 는 지속적으로 Firehose 로 데이터를 전달하며, S3 에 기록됨을 확인 합니다.  


