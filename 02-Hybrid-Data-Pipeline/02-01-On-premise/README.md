# On-premise 환경에 서버 배포

On-premise 환경으로 가정한 VPC 에 EC2 Instance 를 배포합니다.

1. EC2 Instance 배포
2. 데이터 생성 스크립트 배포

---

## 1. EC2 Instance 배포
이전 실습 과정 중, On-premise 로 가정한 VPC 환경에 EC2 Instance 를 배포합니다. 해당 가이드 참고 ([01-01-On-premise-environments](../../01-Hybrid-Cloud/01-01-On-premise-environments))  
먼저, VPC 를 배포한 리전을 선택하고, `EC2` - `Instance` 메뉴로 이동하여, `Launch Instance` 를 실행합니다.

- Name : `on-premise-server-01`
- AMI : `Amazon Linux 2023 AMI` (최신 이미지 선택)
- Architecture : `64-bit(x86)`
- Instance Type : `t2.micro` (가장 작은 스펙 사용)
- Key pair : 미리 생성한 keypair 선택
- Network Settings
  - VPC : `on-premise-network` (이전 실습에서 생성한 VPC)
  - Subnet : `No preference`
  - Auto-assign public IP : `Enable`
  - Firewall (security group) : Select existing security group -> `default` 선
- Root Volume : gp3 8GB

---

## 2. 데이터 생성 스크립트 배포

인스턴스 생성이 완료되면, SSH 로 서버에 접속한다.  
SSH 통신을 위해서 먼저 Security Group 의 Inbound rule 에 22번 포트(SSH)를 오픈한다.

로컬 PC 에서 터미널을 열고 인스턴스의 Public IP Address 를 확인 후 접속한다.

```bash
> ssh -i <KEYPAIR_FILE_NAME> ec2-user@<PUBLIC_IP_ADDR>
```

서버 접속에 성공하면, 작업의 원할함을 위해 `ec2-user` 에서 `root` 유저로 전환한다.

```bash
[ec2-user@ip-10-10-10-39 ~]$ sudo su -
Last login: Sat Apr  1 05:28:21 UTC 2023 on pts/1
[root@ip-10-10-10-39 ~]# 
```

스크립트를 배포할 적절한 디렉토리로 이동 후, 스크립트 파일을 배포한다.  
해당 실습에서는 /usr/local/bin 디렉토리에 배포한다.

```bash
[root@ip-10-10-10-39 ~]# cd /usr/local/bin/
```
