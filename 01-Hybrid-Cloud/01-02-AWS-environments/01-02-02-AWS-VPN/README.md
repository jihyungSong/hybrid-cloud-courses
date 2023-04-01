# AWS VPC 와 On-premise 연동

AWS VPC 환경을 구성 합니다.  
아래 순서로 진행됩니다.

1. Transit Gateway 구성
2. Transit Gateway 와 AWS VPC 연동
3. On-premise 연결을 위한 VPN Connection 구성
4. Transit Gateway 와 VPN 연동
5. Customer Gateway 구성을 위한 EIP 생성
6. On-premise 환경에 VPN Gateway 설치(StrongSwan) 및 Customer Gateway 구성
7. AWS VPC 와 On-premise 간 통신 확인을 위한 EC2 Instance 배포 및 통신 확인


