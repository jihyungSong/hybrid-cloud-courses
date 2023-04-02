# Azure Virtual Network 환경 구성

Azure Virtual Network 환경을 구성 합니다.  
아래 순서로 진행 됩니다.

1. Resource Group 구성
2. Virtual Network 및 Subnet 구성
3. Network Security Group 구성
---

## 1. Resource Group 구성

먼저, 이번 실습에 사용할 Resource Group 을 생성하도록 합니다.  
Resource Group 에서 `Create` 를 수행합니다.  

* Resource Group : `azure-environment`
* Region : `Korea Central`

## 2. Virtual Network 생성

Virtual Network 를 생성합니다.  
Virtual Networks 페이지로 이동하여, `Create` 를 수행 합니다.

* Resource Group : 이전 단계에서 생성한 `azure-environment` 선택
* Virtual Network name :  `azure-vnet`
* Region : `Korea Central`
* IP address : 
  * `default` 삭제
  * `Add an IP address space` 로 신규 IP 대역 설정.
    * Starting adress : `172.31.0.0`
    * Address space size : `/16`
* Subnet 신규 생성 (2개 생성)
  * Subnet 1
    * IP address space : `172.31.0.0/16`
    * Subnet template : `Default`
    * Name : `azure-vnet-subnet-01`
    * Starting address : `172.31.10.0`
    * Subnet size : `/24`
    * NAT gateway : `None`
    * Network security group : `None`
    * Route table : `None`
  * Subnet 2
    * IP address space : `172.31.0.0/16`
    * Subnet template : `Default`
    * Name : `azure-vnet-subnet-02`
    * Starting address : `172.31.20.0`
    * Subnet size : `/24`
    * NAT gateway : `None`
    * Network security group : `None`
    * Route table : `None`

## 4. Network Security Group 구성

Virtual Network 의 보안을 위한 Network Security Group 을 신규로 생성 합니다.

* Resource Group : `azure-environment`
* Name: `azure-vnet-nsg`
* Region : `Korea Central`

생성한 `azure-vnet-nsg` 를 눌러 `Inbound security rules` 메뉴에서 신규 규칙을 추가합니다.

* Source : `My IP address`
* Source port ranges : `*`
* Destination : `Any`
* Service : `SSH`
* Action : `Allow`
* Name : `AllowSSHInboundFromMyIP`