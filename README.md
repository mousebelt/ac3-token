# AC3 Smart Contracts

## Token Overview

* This is a deployment of an ICON asset following the IIC2 standard

## tbears Installation

### Install python3.6, pip, virtualenv

**Install python3.6**
```
sudo apt-get install software-properties-common python-software-properties
sudo add-apt-repository ppa:jonathonf/python-3.6
sudo apt-get update
sudo apt-get install python3.6 python3.6-dev
```

**Install pip**
```
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python get-pip.py
sudo pip install -U pip
pip install virtualenv
```

**Install virtualenv**
```
virtualenv -p python3.6 env
```

### Install levelDB
```
sudo apt-get install libsnappy-dev

wget https://github.com/google/leveldb/archive/v1.20.tar.gz
tart -xzf v1.20.tar.gz
cd leveldb-1.2.0
make
sudo scp -r out-static/lib* out-shared/lib* "/usr/local/lib"
cd include
sudo scp -r leveldb "/usr/local/include"
sudo ldconfig
```

### Install secp256k1 library from source code
```
sudo apt-get install dh-autoreconf
git clone https://github.com/bitcoin-core/secp256k1
cd secp256k1
./autogen.sh
./configure --enable-module-recovery
make
./tests
sudo make install
```

** Important: Should compile with `--enable-module-recovery` flag **


### Install RabbitMQ
```
sudo apt-get install rabbitmq-server
```

### Install python secp256k1 package
```
pip install build-essential automake pkg-config libtool libffi-dev libgmp-dev # optional
pip install --no-binary :all: secp256k1
pip install --no-binary :all: pytest
```


## Deployment

```bash
$ tbears deploy -k <keystore_file> -c ac3token.json ac3_token
```

## Test
```bash
$ tbears test ac3_token
```

## References

* [ICON Token Standard](https://github.com/icon-project/IIPs/blob/master/IIPS/iip-2.md)

