#!/usr/bin/env bash
#

sudo setenforce 0
sudo sed -i s/^SELINUX=.*$/SELINUX=disabled/ /etc/selinux/config

sudo yum install -y deltarpm

sudo yum install -y wget java-11-openjdk*

sudo wget https://bintray.com/jfrog/artifactory-rpms/rpm -O /etc/yum.repos.d/bintray-jfrog-artifactory-oss-rpms.repo

sudo yum install -y jfrog-artifactory-oss

cat < system.yaml
configVersion: 1
shared:
    extraJavaOpts: "-server -Xms512m -Xmx2g -Xss256k -XX:+UseG1GC"
    security:
    node:
    database:
EOF

sudo cp -brvf system.yaml /var/opt/jfrog/artifactory/etc/system.yaml

sudo systemctl enable --now artifactory