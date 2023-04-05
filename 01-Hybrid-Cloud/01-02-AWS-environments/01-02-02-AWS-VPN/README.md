# AWS VPC 와 On-premise 연동

AWS VPC 환경을 구성 합니다.  
아래 순서로 진행됩니다.

1. Transit Gateway 구성
2. Transit Gateway 와 AWS VPC 연동
3. On-premise 연결을 위한 Customer Gateway 생성
4. On-premise 연결을 위한 VPN Connection 구성
5. On-premise 환경에 VPN Gateway 설치(StrongSwan) 및 Customer Gateway 구성
6. Transit Gateway 와 VPN 연동
7. AWS VPC 와 On-premise 간 통신 확인을 위한 EC2 Instance 배포 및 통신 확인
---

## 1. Transit Gateway 구성

먼저, AWS VPC 와 On-premise 사이를 Relay 역할을 담당하는 Transit Gateway 를 구성합니다.  
AWS VPC 가 자리잡고 있는 리전인 `us-east-1` 으로 이동하여, VPC 페이지에서 `Transit Gateway` 메뉴로 이동하여 `Create transit gateway` 를 수행 합니다.  

- name : `aws-transit-gateway`
- ASN : 비워두면 자동으로 `64512` 로 구성


## 2. Transit Gateway 와 AWS VPC 연동

Transit gateway 구성이 완료되었으면, AWS VPC 와 Transit gateway 를 연결하도록 합니다.  
`Transit gateway attachments` 메뉴로 이동하여, `Create transit gateway attachment` 를 수행 합니다.  

- name : `aws-tgw-attach`
- Transit gateway ID : 이전 단계에서 생성한 `aws-transit-gateway` 선택
- Attachment type : `VPC`
- VPC ID : `aws-vpc` 선택

구성 완료 후, 시간이 지나면, State 가 `Available` 로 변경되는 것을 확인 합니다.  

이후, AWS VPC 로 이동하여, On-premise network 와 네트워크 통신이 가능하도록, 경로 설정을 추가하도록 합니다.  
`Route tables` 메뉴로 이동하여, `aws-vpc` 에 연결된 Route table 을 선택 하고, 하단 `Route` 탭으로 이동하여, `Edit routes` 를 수행합니다.

- Destination : `10.10.0.0/16` (On-premise 네트워크의 CIDR)
- Target : Transit gateway 선택 (`aws-tgw-attach`)

## 3. On-premise 연결을 위한 Customer Gateway 생성

On-premise 의 VPN Gateway 역할을 할 Customer Gateway 를 생성합니다.  
해당 Gateway 는 실제 VPN 장비를 생성하는 것은 아닙니다. 이는 이후 5번 단계에서 실제 VPN Gateway 를 배포 하며, Customer Gateway 는 이에 대한 준비 단계로 이해하면 됩니다.  

**(사전 준비)**  
설정을 시작하기 전에, Customer Gateway 에서 사용할 EIP 를 할당 받도록 합니다.  
EIP 는 `Elastic IPs` 메뉴로 이동하여 `Allocate Elastic IP address` 를 수행 하면 됩니다.  
*(참고) 이때, 해당 EIP 의 `Allocation ID`(`eipalloc` 으로 시작하는 ID) 를 꼭 기억해 두어야 합니다. 이후 설정에 필요 합니다.*

EIP 할당이 완료 되었다면, VPC 페이지에서 `Customer Gateway` 메뉴로 이동 하고, `Create customer gateway` 를 수행 합니다. 

* name : `on-premise-cgw`
* BGP ASN : `65000`
* IP Address : 할당 받은 EIP 주소
* Tags : `Name: on-premise-cgw`


## 4. On-premise 연결을 위한 VPN Connection 구성

On-premise 구간을 연동할 VPN Connection 설정을 시작 합니다.
`Site-to-Site VPN connections` 메뉴로 이동하여, `Create VPN connection` 을 수행 합니다.  

- Name : `on-prem-conn`
- Target gateway type : `Transit gateway`
- Transit gateway : 이전 단계에서 생성한 `aws-transit-gateway` 선택
- Customer gateway : `Existing`
- Customer gateway ID : `on-premise-cgw`
- BGP ASN : 65000
- Routing options : `Dynamic (requires BGP)`
- Tunnel inside IP version : `IPv4`
- Tags : `Name : on-prem-conn`

## 5. On-premise 환경에 VPN Gateway 설치(StrongSwan) 및 Customer Gateway 구성

On-premise 환경과 Transit Gateway 구간을 VPN 으로 연동하려면, VPN 전용 장비가 필요합니다.  
하지만, 실습 목적의 환경에서 VPN 전용 장비를 사용하긴 어려우므로, EC2 Instance 에 VPN 역할을 수행할 수 있도록 오픈소스 S/W(StrongSwan, Quagga) 를 설치하여 동작시킬 예정입니다.  
해당 오픈소스를 처음부터 구성하려면 시간이 꽤 소요될 수 있으므로, 관련 설정은 Cloudformation 이라는 AWS 의 배포 자동화 서비스를 활용하며, 관련 코드는 AWS 의 공식 블로그를 참고한 점을 밝힙니다. ([참고](https://aws.amazon.com/ko/blogs/networking-and-content-delivery/simulating-site-to-site-vpn-customer-gateways-strongswan/))

먼저, Cloudformation 구성 파일을 다운로드 받습니다. 다운로드 주소는 해당 링크를 [클릭](https://raw.githubusercontent.com/aws-samples/vpn-gateway-strongswan/main/vpn-gateway-strongswan.yml) 하면 됩니다. 

---
**(사전 준비)**  
본격적으로 Cloudformation 을 통해 배포하기 앞서, 구성에 필요한 준비를 몇가지 수행 합니다.

### (사전 준비-1) VPN Connection Configuration 다운로드 받기
VPN Gateway 서버 구성을 위해, VPN Connection 설정 정보가 필요합니다. 따라서, 해당 설정 정보가 담겨 있는 파일을 다운로드 받도록 합니다.  
`Site-to-Site VPN connections` 메뉴로 이동하여, 위에서 생성한 `on-prem-conn` 을 선택 후, `Download configuration` 버튼을 누릅니다.

- Vendor : `Generic`
- Platform : `Generic`
- Software : `Vendor Agnostic`
- IKE version : `ikev1`

위 항목을 선택 후, Download 버튼을 누르면, 로컬 PC 에 VPN Connection 에 대한 설정 정보 파일을 확인 가능합니다.  
해당 파일에 기재된 일부 정보들은 Cloudformation 수행시 참조될 예정입니다.  

### (사전 준비-2) Secret manager 를 통한 Pre-shared Key 암호화 저장

`사전 준비-1` 을 통해 다운로드 받은 설정 내역 중 Pre-Shared Key 의 경우, VPN connection 의 데이터 암호화에 사용되는 인증키 입니다.   
따라서 해당 키값을 좀 더 안전하게 보관하기 위해, AWS Secrets manager 를 사용하여 해당 키 값을 암호화 해서 저장하고, 해당 secret 정보를 Cloudformation 에 입력해서 사용하면 됩니다.  

먼저, on-premise-network 가 존재하는 리전으로 이동합니다. 위 예제에서는 Oregon (`us-west-2`) 로 이동합니다.  
그리고 `Secrets manager` 서비스 페이지로 이동하여, `Store a new secret` 를 수행합니다. (총 2개 생성)

- Secret type : `Other type of secret`
- key / value : key 에는 `psk` value 에는 다운로드 받은 VPN configuration 파일 `IPSec Tunnel #1` 항목에서 `Pre-shared key` 를 복사하여 사용합니다. 
- Secret name : `vpn-tun1` 

동일한 방식으로 두개의 secret 을 생성합니다. 나머지 하나는 `vpn-tun2` 라는 이름으로 생성하며, value 로는 `IPSec Tunnel #2` 항목의 `Pre-shared key` 를 사용합니다.

---

사전 준비를 마쳤다면, 본격적으로 Cloudformation 을 수행합니다.  
Cloudformation 페이지로 이동하여, `Stacks` 메뉴에서 `Create stack` 을 수행 합니다.  

- Prerequisite : `Template is ready`
- Template source : `Upload a template file` 선택 후, 이전에 다운로드 받은 Cloudformation 구성 파일(`vpn-gateway-strongswan.yml`) 을 첨부합니다. 
- Stack name : `vpn-gateway`
- Parameter
  - Organization Identifier : `fc`
  - System Identifier : `infra`
  - Application Identifier : `vpngw`
  - Environment Purpose : `test`
  - Authentication type : `psk`
  - VPN Tunnel 1
    - Name of secret in AWS Secrets Manager for VPN Tunnel1 Pre-Shared key : 위에서 생성한 Secret 이름 `vpn-tun1`
    - Virtual Private Gateway Outside IP Address : 설정 파일에서 `IPSec Tunnel #1` 항목 중 `Outside IP Addresses - Virtual Private Gateway` 에 IP 주소 값
    - Customer Gateway Inside IP Address : 설정 파일에서 `IPSec Tunnel #1` 항목 중 `Inside IP Addresses - Customer Gateway` 에 IP 주소 값
    - Virtual Private Gateway Inside IP Address : 설정 파일에서 `IPSec Tunnel #1` 항목 중 `Inside IP Addresses - Virtual Private Gateway` 에 IP 주소 값
    - Virtual Private Gateway BGP ASN : 설정 파일에서 `IPSec Tunnel #1` 항목 중 `BGP Configuration Options - Virtual Private  Gateway ASN` 에 ASN 값
    - BGP Neighbor IP Address : 설정 파일에서 `IPSec Tunnel #1` 항목 중 `Inside IP Addresses - Neighbor IP Address` 에 IP 주소 값
  - VPN Tunnel 2
    - Name of secret in AWS Secrets Manager for VPN Tunnel2 Pre-Shared key : 위에서 생성한 Secret 이름 `vpn-tun2`
    - Virtual Private Gateway Outside IP Address : 설정 파일에서 `IPSec Tunnel #2` 항목 중 `Outside IP Addresses - Virtual Private Gateway` 에 IP 주소 값
    - Customer Gateway Inside IP Address : 설정 파일에서 `IPSec Tunnel #2` 항목 중 `Inside IP Addresses - Customer Gateway` 에 IP 주소 값
    - Virtual Private Gateway Inside IP Address : 설정 파일에서 `IPSec Tunnel #2` 항목 중 `Inside IP Addresses - Virtual Private Gateway` 에 IP 주소 값
    - Virtual Private Gateway BGP ASN : 설정 파일에서 `IPSec Tunnel #2` 항목 중 `BGP Configuration Options - Virtual Private  Gateway ASN` 에 ASN 값
    - BGP Neighbor IP Address : 설정 파일에서 `IPSec Tunnel #2` 항목 중 `Inside IP Addresses - Neighbor IP Address` 에 IP 주소 값
  - VPC ID : `on-premise-network` VPC ID
  - VPC CIDR Block : `10.10.0.0/16`
  - Subnet ID for VPN Gateway : `on-premise-network` VPC 에 배포된 Subnet 중 하나 선택
  - Use Elastic IP Address : `true`
  - Elastic IP Address Allocation ID : 이전 단계에서 생성한 Customer Gateway 용 EIP 의 Allocation ID
  - Local VPN Gateway's BGP ASN : `65000` 
  - EC2 AMI ID : `/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-ebs`
  - EC2 Instance Type : `t3a.micro`

파라미터 설정을 마친 후, Cloudformation 을 수행하면, 일정 시간 이후, Stack 의 상태가 `CREATE_COMPLETE` 로 변경되면 모두 정상 작동한 것입니다.

## 6. Transit Gateway 와 VPN 연동

On-premise 에 VPN Gateway 구성을 마쳤다면, VPN Connection 과 Transit Gateway 를 연동합니다.  
`Transit gateway attachments` 메뉴로 이동하여, `Create transit gateway attachment` 를 수행 합니다.  

- name : `on-prem-tgw-attach`
- Transit gateway ID : 이전 단계에서 생성한 `aws-transit-gateway` 선택
- Attachment type : `VPN`
- Customer Gateway : `Existing`
- Customer Gateway ID : `on-premise-cgw`
- Routing options : `Dynamic (requires BGP)`

구성 완료 후, 시간이 지나면, State 가 `Available` 로 변경되는 것을 확인 합니다.  

이후, AWS VPC 로 이동하여, On-premise network 와 네트워크 통신이 가능하도록, 경로 설정을 추가하도록 합니다.  
`Route tables` 메뉴로 이동하여, `aws-vpc` 에 연결된 Route table 을 선택 하고, 하단 `Route` 탭으로 이동하여, `Edit routes` 를 수행합니다.

- Destination : `10.10.0.0/16` (On-premise 네트워크의 CIDR)
- Target : Transit gateway 선택 (`aws-tgw-attach`)

On-premise 네트워크에서도 VPN 과 통신이 가능하도록 경로 설정을 추가하도록 합니다.  
`Route tables` 메뉴에서 `on-premise-network` 에서 사용 중인 route table 을 선택하고 하단 탭에서 `Routes` 를 선택하여, `Edit routes` 를 수행합니다.

* Destination : `172.16.0.0/16`
* Target : `Instance` 선택 후, VPN Gateway 로 생성된 인스턴스를 선택합니다. (예시대로 생성시, `infra-vpngw-test`)


## 7. AWS VPC 와 On-premise 간 통신 확인을 위한 EC2 Instance 배포 및 통신 확인

AWS VPC 와 On-premise 간 VPN 연동을 위한 모든 설정을 마쳤습니다.  
실제 통신이 되는지, VPC 와 On-premise 네트워크 각각 EC2 Instance 를 생성하고 두 인스턴스간 Private IP 로 Ping 을 통해 연결이 되는지 확인합니다.  
(Security Group 에서 ICMP 통신 허용 필요)

