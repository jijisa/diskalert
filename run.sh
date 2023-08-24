#!/bin/bash
OS_FLAVOR=${1:-'debian'}

echo $OS_FLAVOR

docker build -t docker.io/jijisa/diskpatrol-builder:${OS_FLAVOR} \
    -f Dockerfile.${OS_FLAVOR} .
docker run -v /tmp/output:/output --rm \
    docker.io/jijisa/diskpatrol-builder:${OS_FLAVOR}
#docker run -it -v $(pwd)/output:/output --rm --entrypoint=/bin/bash \
#    docker.io/jijisa/diskpatrol-builder:${OS_FLAVOR}
