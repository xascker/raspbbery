# Debian GNU/Linux 13 (trixie)
cat /sys/fs/cgroup/cgroup.controllers


cd /boot/firmware/
dtc -I dtb -O dts -o bcm2710-rpi-zero-2-w.dts bcm2710-rpi-zero-2-w.dtb
vim bcm2710-rpi-zero-2-w.dts
#remove cgroup_disable=memory from 
chosen {
    bootargs = "coherent_pool=1M 8250.nr_uarts=0 snd_bcm2835.enable_headphones=0 cgroup_disable=memory snd_bcm2835.enable_hdmi=1 ...";
};

dtc -I dts -O dtb -o bcm2710-rpi-zero-2-w.dtb.new bcm2710-rpi-zero-2-w.dts
mv bcm2710-rpi-zero-2-w.dtb bcm2710-rpi-zero-2-w.dtb.bak
mv bcm2710-rpi-zero-2-w.dtb.new bcm2710-rpi-zero-2-w.dtb

vim /boot/firmware/cmdline.txt
# Add to the end of the single line:
cgroup_memory=1 cgroup_enable=memory
reboot

---------------------
master:~# curl -sfL https://get.k3s.io | sh -
master:~# cat /var/lib/rancher/k3s/server/node-token

curl -sfL https://get.k3s.io | K3S_URL=https://<MASTER_IP>:6443 K3S_TOKEN=<TOKEN> sh -
#curl -sfL https://get.k3s.io | K3S_URL=https://192.168.1.150:6443 K3S_TOKEN=K1027a2d94567eb420ae2f705cf90886ebeec4ac38c3e87da233e8920c9ea64989d::server:ff3c92d3432683715e755a9805d04610 sh -
curl -sfL https://get.k3s.io | K3S_URL=https://192.168.1.250:6443 K3S_TOKEN=K10db522e981c61f89c701c8b8aa0e79865aabc51ff3d76e4bcf497fd2d0defec6f::server:c5ea00bd0dd928c96ef1537dfaa9df47 sh -

kubectl label node pi-zw2-worker1 node-role.kubernetes.io/worker=worker
kubectl label node pi-zw2-worker1 location=pi-zw2

cat /etc/rancher/k3s/k3s.yaml

/usr/local/bin/k3s-uninstall.sh
/usr/local/bin/k3s-agent-uninstall.sh
------------------------------------------------

# Ubuntu 22
systemctl disable systemd-networkd-wait-online.service
systemctl mask systemd-networkd-wait-online.service
