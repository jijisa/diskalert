#!/bin/bash

set -e

function USAGE() {
  echo "USAGE: $(basename $0) [-h] [-b] [-r] [debian|rocky]" 1>&2
  echo
  echo " -h                     Display this help message."
  echo " -b [debian|rocky]      Build diskpatrol."
  echo " -r [debian|rocky]      Run into diskpatrol build env."
  echo
}
while getopts 'b:r:h' opt; do
  case "${opt}" in
    b)
      DISTRO="${OPTARG}"
      break
      ;;
    r)
      DISTRO="${OPTARG}"
      break
      ;;
    h)
      USAGE
      exit 0
      ;;
    *)
      exit 1
      ;;
  esac
done

case "${DISTRO}" in
  debian)
    FROM="docker.io/debian:10-slim"
    ;;
  rocky)
    FROM="docker.io/rockylinux/rockylinux:8"
    ;;
  *)
    echo "Unknown distro ${DISTRO}."
    USAGE
    exit 1
    ;;
esac

IMAGE="docker.io/jijisa/diskpatrol-builder:${DISTRO}"

docker build -t ${IMAGE} --build-arg FROM=${FROM} -f Dockerfile .
if [[ "$opt" = "b" ]]; then
  docker run -v $(pwd)/output:/output --rm ${IMAGE}
fi
if [[ "$opt" = "r" ]]; then
  docker run -it -v $(pwd)/output:/output --rm --entrypoint=/bin/bash ${IMAGE}
fi

