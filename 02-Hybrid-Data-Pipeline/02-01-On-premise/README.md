# On-premise 환경에 서버 배포

On-premise 환경으로 가정한 VPC 에 EC2 Instance 를 배포합니다.

1. EC2 Instance 배포
2. 데이터 생성 스크립트 배포
3. 스크립트 실행 및 데이터 생성 확인

---

## 1. EC2 Instance 배포
이전 실습 과정 중, On-premise 로 가정한 VPC 환경에 EC2 Instance 를 배포합니다. 해당 가이드 참고 ([01-01-On-premise-environments](../../01-Hybrid-Cloud/01-01-On-premise-environments/README.md))  
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

인스턴스 생성이 완료되면, SSH 로 서버에 접속합니다.  
SSH 통신을 위해서 먼저 Security Group 의 Inbound rule 에 22번 포트(SSH)를 오픈 합니다.

로컬 PC 에서 터미널을 열고 인스턴스의 Public IP Address 를 확인 후 접속 합니다.

```bash
ssh -i <KEYPAIR_FILE_NAME> ec2-user@<PUBLIC_IP_ADDR>
```

서버 접속에 성공하면, 작업의 원할함을 위해 `ec2-user` 에서 `root` 유저로 전환 합니다.

```bash
sudo su -
```

스크립트를 배포할 적절한 디렉토리로 이동 후, 스크립트 파일을 배포 합니다.  
해당 실습에서는 /usr/local/bin 디렉토리에 배포 합니다.  
스크립트는 github 에 있는 파일을 `wget` 을 이용해 다운로드 받도록 합니다.

```bash
cd /usr/local/bin/
wget https://raw.githubusercontent.com/jihyungSong/hybrid-cloud-courses/master/02-Hybrid-Data-Pipeline/02-01-On-premise/generate_data/generate_data.py
```

---

## 3. 스크립트 실행 및 데이터 생성 확인

다운로드 받은 스크립트를 실행 해보도록 합니다.  
해당 스크립트는 python 으로 구현 되어 있으며, json 포맷 데이터를 1초에 한번씩 랜덤으로 생성하여 `/tmp/data.log` 파일을 생성하는 예제 입니다.  
스크립트를 실행하면, 아래와 같이 1초에 한번씩 데이터가 생성됨을 확인 가능 합니다.

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

데이터가 /tmp/data.log 파일에 기록되고 있는지 확인 가능 합니다.

```bash
> tail -f /tmp/data.log
{'name': 'Isabella Brown', 'id': 'PJYOL', 'ip': '132.5.243.3', 'latitude': '57.684020104755064', 'longiitude': '-37.55966341186334', 'value': 4.851429404317784, 'created_at': '2023-04-01 08:19:34'}
{'name': 'Sophia Jackson', 'id': 'EODPU', 'ip': '232.169.86.41', 'latitude': '-13.120496867364736', 'longiitude': '-80.74471768661853', 'value': 3.754722574423016, 'created_at': '2023-04-01 08:20:54'}
{'name': 'Sophia Jackson', 'id': 'JMPQK', 'ip': '29.24.246.30', 'latitude': '-43.56834245007847', 'longiitude': '30.710612523176565', 'value': 9.291653666063263, 'created_at': '2023-04-01 08:20:55'}
{'name': 'Olivia Thomas', 'id': 'KYLPI', 'ip': '94.21.24.98', 'latitude': '85.1620773284435', 'longiitude': '178.0039350042951', 'value': 7.145006594804742, 'created_at': '2023-04-01 08:20:56'}
{'name': 'Emma Moore', 'id': 'JDDTL', 'ip': '163.205.52.94', 'latitude': '-17.757523884949578', 'longiitude': '175.92182995493937', 'value': 7.565661710716935, 'created_at': '2023-04-01 08:20:57'}
{'name': 'Isabella Taylor', 'id': 'ECDOU', 'ip': '37.26.110.136', 'latitude': '-71.20046801063216', 'longiitude': '-87.70170434892036', 'value': 9.749078686959699, 'created_at': '2023-04-01 08:20:58'}
{'name': 'Jackson Anderson', 'id': 'BETMP', 'ip': '114.224.197.141', 'latitude': '70.02809766004557', 'longiitude': '-159.11247910226558', 'value': 8.607070404372791, 'created_at': '2023-04-01 08:20:59'}
...
```