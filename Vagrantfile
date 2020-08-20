# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.define "master" do |master|
  master.vm.box = "centos/7"
  master.vm.network "private_network", ip: "192.168.99.55"
    master.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
      vb.cpus = 2
      vb.name = "artifactory"
    end
  master.vm.provision "shell",
                      path: "install.sh"
  end
end



