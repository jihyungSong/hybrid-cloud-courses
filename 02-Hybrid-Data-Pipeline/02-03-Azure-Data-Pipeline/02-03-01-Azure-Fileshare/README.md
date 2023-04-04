# Azure File share 를 활용한 On-premise 연동

1. Azure Storage Account 생성
2. Fire share 및 Private endpoint 구성
3. On-premise 서버에서 NFS 마운트 및 데이터 적재 확인
---

## 1. Azure Storage Account 생성

On-premise 의 데이터를 저장할 스토리지 공간을 설정합니다.  
Storage Account 페이지로 이동하여, `Create` 를 수행합니다.  

* Resource Group : `azure-environment`
* Storage account name : `dataforonpremisesvr`
* Region : `Korea Central`
* Performance : `Standard`
* Redundancy : `Geo-redundant storage (GRS)`

On-premise 서버가 Storage Account 에서 제공하는 NFS 에 연결하기 위해, File shares 를 생성합니다.  
메뉴 중 `File shares` 로 이동하여, `File share` 를 수행합니다.  

* Name : `on-prem-data`
* Tier : `Transaction optimized`

## 2. Fire share 및 Private endpoint 구성

On-premise 와 Fireshare 간 내부 통신을 위해 Private endpoint 를 설정합니다.  
Networking 메뉴로 이동 하여 `Private endpoint connections` 탭으로 이동하여 `Private endpoint` 생성을 수행합니다.  

* Resource Group : `azure-environment`
* Name : `on-prem-endpoint`
* Network Interface Name : `on-prem-endpoint-nic`
* Region : `Korea Central`
* Target sub-resource : `file`
* Virtual network : `azure-vnet`
* Subnet : `azure-vnet-subnet-01` 또는 `02` 선택
* Private IP configuration : `Statically allocate IP address`
  * Name : `file-share-endpoint-ip`
  * Private IP :  `172.31.10.xx` (subnet 을 02 로 선택했을 경우, `172.31.20.xx`)
* Integrate with private DNS zone : `Yes`

## 3. On-premise 서버에서 NFS 마운트 및 데이터 적재 확인

이제, On-premise 서버에 접속하여, NFT 마운트를 위해 다음과 같이 명령어를 수행 합니다.  

먼저, NFS 마운트를 위한 패키지를 설치합니다.  

```shell
yum install cifs-utils
```

다음과 같은 Script 를 복사 후 실행합니다.  

```shell
vim file_share_mount.sh

-------------------------------
sudo mkdir /mnt/on-prem-data
if [ ! -d "/etc/smbcredentials" ]; then
sudo mkdir /etc/smbcredentials
fi
if [ ! -f "/etc/smbcredentials/dataforonpremisesvr.cred" ]; then
    sudo bash -c 'echo "username=dataforonpremisesvr" >> /etc/smbcredentials/dataforonpremisesvr.cred'
    sudo bash -c 'echo "password=XXXXXXXXXXXXXXXXXXX" >> /etc/smbcredentials/dataforonpremisesvr.cred'
fi
sudo chmod 600 /etc/smbcredentials/dataforonpremisesvr.cred

sudo bash -c 'echo "//PRIVATE_ENDPOINT_IP/on-prem-data /mnt/on-prem-data cifs nofail,credentials=/etc/smbcredentials/dataforonpremisesvr.cred,dir_mode=0777,file_mode=0777,serverino,nosharesock,actimeo=30" >> /etc/fstab'
sudo mount -t cifs //PRIVATE_ENDPOINT_IP/on-prem-data /mnt/on-prem-data -o credentials=/etc/smbcredentials/dataforonpremisesvr.cred,dir_mode=0777,file_mode=0777,serverino,nosharesock,actimeo=30
```

해당 script 저장 후 실행합니다.  
```shell
sh file_share_mount.sh
```

파일 시스템 정보를 확인시, 다음과 같이 /mnt/on-prem-data 경로로 5.0T 공간이 마운트 된 것을 확인 가능합니다.
```shell
> df -h
Filesystem                  Size  Used Avail Use% Mounted on
devtmpfs                    4.0M     0  4.0M   0% /dev
tmpfs                       477M     0  477M   0% /dev/shm
tmpfs                       191M  2.9M  188M   2% /run
/dev/xvda1                  8.0G  2.1G  5.9G  27% /
tmpfs                       477M  5.2M  472M   2% /tmp
//172.31.10.5/on-prem-data  5.0T  512K  5.0T   1% /mnt/on-prem-data
tmpfs                        96M     0   96M   0% /run/user/1000
```

이제, 데이터 생성 스크립트에서 저장 path 를 `/tmp/data.log` 에서 `/mnt/on-prem-data/data.log` 로 변경하도록 합니다.

```python
...(중략)

if __name__ == "__main__":
    print("Generate Data for Training")
    while True:
        with open("/mnt/on-prem-data/data.log", mode="a") as file:
            data = generate_data()
            file.write(f"{data}\n")
            file.close()
            print(f"success to generate data...{data.get('id')}")

        time.sleep(1)
```

스크립트 실행시, Azure Cloud 환경의 Storage Account 에 데이터가 저장되는 것을 확인 할 수 있다.
