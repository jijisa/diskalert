#!/bin/bash

set -ex

PKGDIR="${WORKSPACE}/pkgdir"

dnf -y install python3-pip curl gcc make
python3 -m pip install -U pip
python3 -m pip install pyoxidizer
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | \
    sh -s -- --no-modify-path -y

VER=$(python3 ${PKGDIR}/diskpatrol/__init__.py)
BINFILE="${PKGDIR}/build/x86_64-unknown-linux-gnu/debug/exe/diskpatrol"

# build diskpatrol binary
pyoxidizer build --system-rust --path=${PKGDIR}
strip ${BINFILE}
chmod 0755 ${BINFILE}
cp ${BINFILE} ${OUTPUT_DIR}

# build rpm package
dnf install -y rpmdevtools rpmlint
rpmdev-setuptree

pushd ${WORKSPACE}/scripts
  cp diskpatrol.spec /root/rpmbuild/SPECS/
  mkdir -p /diskpatrol-${VER}
  cp diskpatrol.conf diskpatrol.service ${BINFILE} /diskpatrol-${VER}/
popd
pushd /
  tar cvzf /root/rpmbuild/SOURCES/diskpatrol-${VER}.tar.gz diskpatrol-${VER}
popd
rpmbuild -bb /root/rpmbuild/SPECS/diskpatrol.spec
cp /root/rpmbuild/RPMS/x86_64/diskpatrol-${VER}*.rpm ${OUTPUT_DIR}

