#!/bin/bash

# setup mongo
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927
echo "deb http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.2.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo cp mongodb.service /etc/systemd/system/mongodb.service
sudo systemctl daemon-reload
sudo systemctl start mongodb
sudo systemctl enable mongodb

# setup python
sudo add-apt-repository -y ppa:jonathonf/python-3.6
sudo apt update
sudo apt install -y python3.6
curl https://bootstrap.pypa.io/get-pip.py | sudo python3.6
sudo apt-get install build-essential libssl-dev libffi-dev python3.6-dev
sudo pip install -U setuptools
sudo pip install -U virtualenv
virtualenv env

# setup redis
wget http://download.redis.io/releases/redis-3.2.11.tar.gz
tar xzf redis-3.2.11.tar.gz
rm redis-3.2.11.tar.gz
cd redis-3.2.11
make

echo "sudo service mongod start" >> /home/ubuntu/.profile
echo "cd /vagrant" >> /home/ubuntu/.profile
echo "source /vagrant/env/bin/activate" >> /home/ubuntu/.profile
echo "redis-3.2.11/src/redis-server &" >> /home/ubuntu/.profile

