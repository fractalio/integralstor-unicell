#!/bin/bash

sed -i 's/rhgb/net.ifnames=0 biosdevname=0 ipv6.disable=1/' /etc/default/grub &>> /tmp/out_grub_conf
grub2-mkconfig -o /boot/grub2/grub.cfg &>> /tmp/out_grub_conf

