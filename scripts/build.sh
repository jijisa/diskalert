#!/bin/bash

set -ex

PKGDIR="${WORKSPACE}/pkgdir"
BINFILE="${PKGDIR}/build/x86_64-unknown-linux-gnu/debug/exe/diskpatrol"

function get_distro() {
  if [[ -f /etc/os-release ]]; then
    source /etc/os-release
    echo ${ID}-${VERSION_ID}
  else
    echo "Unknown"
  fi
}

function prepare_centos7() {
  yum -y install python3-pip curl gcc make rpmdevtools rpmlint
}
function prepare_rocky() {
  dnf -y install python3-pip curl gcc make rpmdevtools rpmlint
}
function prepare_debian() {
  apt update && apt -y install python3-pip curl gcc make
}

function build_rpm() {
  rpmdev-setuptree
  pushd ${WORKSPACE}/scripts
    cp diskpatrol.spec /root/rpmbuild/SPECS/
    mkdir -p /diskpatrol-${VER}
    cp diskpatrol.conf.sample /diskpatrol-${VER}/diskpatrol.conf
    cp diskpatrol.service ${BINFILE} /diskpatrol-${VER}/
    cp diskpatrol.logrotate /diskpatrol-${VER}/
  popd
  pushd /
    tar cvzf /root/rpmbuild/SOURCES/diskpatrol-${VER}.tar.gz diskpatrol-${VER}
  popd
  rpmbuild -bb /root/rpmbuild/SPECS/diskpatrol.spec
  cp /root/rpmbuild/RPMS/x86_64/diskpatrol-${VER}*.rpm ${OUTPUT_DIR}
}

function main() {
  case $(get_distro) in
    centos-7)
      prepare_centos7
      ;;
    rocky-8.8)
      prepare_rocky
      ;;
    debian-10)
      prepare_debian
      ;;
  esac
  VER=$(python3 ${PKGDIR}/diskpatrol/__init__.py)
  python3 -m pip install -U pip
  python3 -m pip install pyoxidizer

  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | \
    sh -s -- --no-modify-path -y

  # build diskpatrol binary
  pyoxidizer build --system-rust --path=${PKGDIR}
  strip ${BINFILE}
  chmod 0755 ${BINFILE}
  cp ${BINFILE} ${OUTPUT_DIR}

  case $(get_distro) in
    centos-7)
      build_rpm
      ;;
    rocky-8.8)
      build_rpm
      ;;
    debian-10)
      build_deb
      ;;
  esac
}

main

