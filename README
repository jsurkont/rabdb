#RabDB


## Set up RabDB

How to install RabDB on two difference virtual machines using KVM. Everything runs on Ubuntu 14.04.

### Prepare host

1. Install KVM

    `sudo apt-get install qemu-kvm libvirt-bin bridge-utils`
    
2. To use GUI install also `virt-manager` and `qemu-system`

### rabdb-worker

* default user: rabdbworker
* default pass: 12345

Install python virtualenv and project (both rabifier and rabdb) python dependencies.

To start `celeryd` as boot run e.g. `rcconf`.

#### Rabifier

To compile matplotlib install `libxft-dev`

`meme` must be compiled at the worker machine (meme has issues with paths)

### rabdb-web

* default user: rabdbweb
* default pass: 12345

Install python virtualenv and project python dependencies.

Install `rabbitmq-server` and set it up

    sudo rabbitmqctl add_user myuser mypassword
    sudo rabbitmqctl add_vhost myvhost
    sudo rabbitmqctl set_permissions -p myvhost myuser ".*" ".*" ".*"


