ARG         FROM=docker.io/debian:10
FROM        ${FROM}

ENV         WORKSPACE="/pyoxidizer"
ENV         PATH="$PATH:/root/.cargo/bin"

WORKDIR     ${WORKSPACE}

RUN         apt-get update && \
            DEBIAN_FRONTEND=noninteractive apt -y install python3-pip curl && \
            python3 -m pip install -U pip && \
            python3 -m pip install pyoxidizer && \
            curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | \
                sh -s -- --no-modify-path -y

ENTRYPOINT  ["/usr/local/bin/pyoxidizer"]
CMD         ["-h"]
