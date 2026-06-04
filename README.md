Conifugration uses Apache and rsync.

Prerequisites:
dnf -y install \
  httpd \
  rsync \
  dnf-plugins-core \
  createrepo_c \
  gnupg2 \
  firewalld

Metadata signature check requires to find and import GPG keys using the following commands:
GET:
sudo find /home1/repos/rocky -name "RPM-GPG-KEY*" -print
IMPORT exemple:
sudo gpg --import /home1/repos/rocky/8/BaseOS/x86_64/os/RPM-GPG-KEY-rockyofficial || true
sudo gpg --import /home1/repos/rocky/9/BaseOS/x86_64/os/RPM-GPG-KEY-Rocky-9 || true
