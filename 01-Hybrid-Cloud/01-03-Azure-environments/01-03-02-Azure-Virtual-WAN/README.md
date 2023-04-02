# Azure Virtual WAN 환경 구성

1. Virtual WAN 생성
2. Hubs 생성과 함께 VPN Gateway 배포
3. AWS Customer Gateway 설정
4. AWS VPN Connection 설정
5. Azure VPN site 생성 및 연결
6. Azure Virtual Network 와 Hub 연결
7. AWS VPC 와 On-premise 의 Route 설정 추가
8. Azure Virtual Network 의 Network Security Group 설정 추가
9. AWS 및 On-premise 환경 연결 확인
---

## 1. Virtual WAN 생성

* Resource Group : `azure-environment`
* Region : `Korea Central`
* Name : `azure-vwan`
* Type : `Standard`

## 2. Hubs 생성과 함께 VPN Gateway 배포

* Region : `Korea Central`
* Name : `azure-hub`
* Hub private address space : `192.168.0.0/24`
* Virtual hub capacity : `2 Routing Infrastructure Units, 3 Gbps Router, Supports 2000 VMs`
* Hub routing preference : `VPN`
* Site to site 생성 : `Yes`
  * AS Number : `65515`
  * Gateway scale units : `1 scale unit - 500 Mbps x 2`
  * Routing preference : `Microsoft network`

## 3. AWS Customer Gateway 설정

AWS 쪽에 Azure VPN Gateway 를 선언하기 위해 Customer Gateway 를 설정 합니다.  
Azure VPN Gateway 인스턴스가 2개가 있으므로, Customer Gateway 도 2개를 설정합니다.  

---
(사전 작업)  
AWS Customer Gateway 를 생성하기 위해서는 Azure VPN Gateway 의 BGP ASN 정보와 Public IP 가 필요합니다.  
해당 정보를 미리 파악하도록 합니다.  
이전 단계에서 생성한 `azure-vwan` 에서 Hubs 중 `azure-hub` 를 선택하고, `VPN (Site to site)` 메뉴로 이동하여, `Gateway configuration` 의 `View/Configure` 를 통해 VPN Gateway 정보를 파악 합니다.  
---


Azure VPN Gateway 정보를 미리 파악했다면, 이제 AWS 의 VPC 페이지에서 `Customer gateways` 메뉴를 선택하여, `Create customer gateway` 를 수행합니다.  

* Name : `azure-vpn-gw-01`
* BGP ASN : `65515` (사전 작업에서 파악한 BGP ASN)
* IP Address : (사전작업에서 파악한 VPN Instance 0 의 `Public IP Address`)

## 4. AWS VPN Connection 설정

* Name : `azure-vpn-conn`
* Target gateway type : `Transit gateway`
* Transit gateway : `aws-transit-gateway` (이전 단계에서 생성한 Transit gateway 선택)
* Customer gateway : `Existing`
* Customer gateway ID : 이전 단계에서 `azure-vpn-gw-01` 선택
* Routing options : `Dynamic (requires BGP)`
* Tunnel inside IP version : `IPv4`
* Local IPv4 network CIDR : 설정 X 
* Remote IPv4 network CIDR : 설정 X
* Outisde IP address type : `PublicIpv4`

[Tunnel 1 options]
* Inside IPv4 CIDR for tunnel 1 : `169.254.21.0/30` 
* Pre-shared key for tunnel 1 : `hybridcloud123`
* Advanced options for tunnel 1 : `Use default options`

[Tunnel 2 options]
* Inside IPv4 CIDR for tunnel 1 : `169.254.22.0/30` 
* Pre-shared key for tunnel 1 : `hybridcloud123`
* Advanced options for tunnel 1 : `Use default options`

VPN Connection 생성이 완료되면, 두 개의 Tunnel 설정을 `Tunnel details` 탭에서 확인 가능합니다. 이 정보는 이후에 Azure vHub 의 VPN site 설정 시 사용됩니다.  


## 5. Azure VPN site 생성 및 연결

AWS VPN Connection 생성을 완료했다면, 해당 정보를 바탕으로 Azure Virtual WAN 의 VPN Site 연결 작업을 시작합니다.  
위 단계에서 구성한 Virtual WAN `azure-vwan` 의 Hub `azure-hub` 를 선택하고, `VPN (Site to site)` 메뉴로 이동합니다.  
여기서, 하단의 `Create new VPN site` 를 수행하도록 합니다. 

* Region : `Korea Central`
* Name : `aws-vpn-conn-01`
* Device vendor : `aws`
* Link 설정
  * Link name : `azure-vpn-conn-tun1`
  * Link speed : `200`
  * Link provider name : `aws`
  * Link IP address : 위 AWS VPN Connection 생성 후, Tunnel1 의 Outside IP address
  * Link BGP address : `169.254.21.1`
  * Link ASN : `64512`

VPN site 생성 후, 해당 site 를 선택 후 `Connect VPN sites` 를 수행합니다.

* Pre-shared key : `hybridcloud123` (AWS VPN Connection 생성시 입력한 key)
* Propagate : `Enabled`

해당 설정까지 완료되고 기다리면, Site 상태 (Provisioning status) 와 Connectivity status 가 모두 `Succeeded` 와 `Connected` 로 변경됨을 확인 가능합니다.  
또한, AWS VPN connection 의 Tunnel 1 의 상태가 `Up` 으로 변경되어 있는것이 확인 됩니다.  

만약, 추가로 AWS VPN Connection 의 Tunnel 2 와 연결을 추가하고 싶다면 VPN Site 를 하나 더 생성하도록 합니다.  

## 6. Azure Virtual Network 와 Hub 연결

Virtual Hub 에 Azure Virtual Network 를 연동 하도록 합니다.  
`azure-vwan` Virtual WAN 을 선택 후, `Virtual network connections` 메뉴로 이동 하여, `Add connection` 을 수행 합니다.  

* Connection name : `azure-vnet-conn`
* Hubs : `azure-hub`
* Resource Group : `azure-environment`
* Virtual network : `azure-vnet` 
* Propagate to none : `No`
* Associate Route Table : `Default`
* Propagate to Route Tables : `Default`
* Propagate to labels : `default`

연결이 완료되었으면, `azure-hub` 의 `Route Tables` 정보를 업데이트합니다.  
현재 생성되어 있는 Route Table 로 `Default` 를 선택합니다.  
여기서 `Propagations` 탭에서 다음과 같이 정보를 설정 합니다.  

* Propagate routes from connections to this route table?  `Yes`  
* Virtual Network : `azure-vnet` 선택

## 7. AWS VPC 와 On-premise 의 Route 설정 추가

AWS VPC 와 On-premise 네트워크에 배포된 인스턴스가 Azure Virtual Network 와 통신하기 위해 추가적인 경로 설정을 합니다.  
AWS VPC 가 있는 Region 으로 이동하여, `VPC` 페이지를 통해 `Route Tables` 메뉴로 이동하여, 해당 VPC 와 맵핑된 Route table 을 선택합니다.  
하단 Route 탭에서 `Edit routes` 를 수행합니다.  

* Destination : `172.31.0.0/16` (Azure Virtual Network CIDR)
* Target : Transit gateway (`aws-tgw-attach`)

마찬가지로, On-premise 네트워크가 있는 리전으로 이동하여,  동일하게 Route 정보를 아래와 같이 추가해 줍니다.  

* Destination : `172.31.0.0/16` (Azure Virtual Network CIDR)
* Target : Instance (`infra-vpngw-test`)
 
## 8. Azure Virtual Network 의 Network Security Group 설정 추가

Virtual Network 의 Subnet 에 설정된 Network Security Group 인 `azure-vnet-nsg` 에 추가적으로,  
AWS VPC 와 On-premise 의 네트워크 대역을 허용하는 룰을 설정합니다.  

[Inbound Rule #1]
* Source : `10.10.0.0/16` (On-premise 네트워크 대역)
* Source port ranges : `*`
* Destination : `Any`
* Service : `Custom`
* Destination port ranges : `*`
* Name : `AllowOnPremCidrBlockCustomAnyInbound`
* Action : `Allow`

[Inbound Rule #2]
* Source : `172.16.0.0/16` (AWS VPC 네트워크 대역)
* Source port ranges : `*`
* Destination : `Any`
* Service : `Custom`
* Destination port ranges : `*`
* Name : `AllowAWSVPCCidrBlockCustomAnyInbound`
* Action : `Allow`

[Outbound Rule #1]
* Source : `Any` 
* Source port ranges : `*`
* Destination : `IP Address`
* Destination IP addresses/CIDR ranges : `10.10.0.0/16` (On-premise 네트워크 대역)
* Service : `Custom`
* Destination port ranges : `*`
* Name : `AllowOnPremCidrBlockCustomAnyOutbound`
* Action : `Allow`

[Outbound Rule #2]
* Source : `Any` 
* Source port ranges : `*`
* Destination : `Any`
* Destination IP addresses/CIDR ranges : `172.16.0.0/16` (AWS VPC 네트워크 대역)
* Service : `Custom`
* Destination port ranges : `*`
* Name : `AllowAWSVPCCidrBlockCustomAnyOutbound`
* Action : `Allow`

## 9. AWS 및 On-premise 환경 연결 확인

마지막으로, AWS, Azure, On-premise 네트워크에 각각 인스턴스를 배포 후, Ping 을 통해 통신 테스트를 합니다.  
AWS, On-premise 환경에 배포된 인스턴스의 Security Group 도 각각의 대역에 대한 통신 허가가 필요합니다.  
