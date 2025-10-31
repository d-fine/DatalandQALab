FROM debian:bullseye

RUN apt-get update && \
    apt-get install -y \
        python3 \
        python3-pip \
        python3-dev \
        default-jre \
        build-essential \
        cmake \
        libffi-dev \
        libzmq3-dev \
        git \
        && apt-get clean 

RUN pip3 install -U pip pdm

WORKDIR /workspace
COPY . /workspace

RUN ./bin/setup_dev_environment.sh

EXPOSE 8000

CMD ["tail", "-f", "/dev/null"]