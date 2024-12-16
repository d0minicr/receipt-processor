# Use the latest Amazon Linux 2023 image as the base
FROM amazonlinux:2023

# Set an environment variable for the Python version
ENV PYTHON_VERSION="3.12.8"

# Install dependencies for building Python
RUN yum update -y && \
    yum groupinstall -y "Development Tools" && \
    yum install -y gcc openssl-devel bzip2-devel libffi-devel zlib-devel make wget


# Install Python using the version defined in the environment variable
RUN cd /tmp && \
    wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz && \
    tar xzf Python-${PYTHON_VERSION}.tgz && \
    cd Python-${PYTHON_VERSION} && \
    ./configure --enable-optimizations && \
    make altinstall

# Verify Python installation
RUN python3 --version

# Set the default Python version
RUN alternatives --install /usr/bin/python3 python3 /usr/local/bin/python${PYTHON_VERSION%.*} 1 && \
    alternatives --set python3 /usr/local/bin/python${PYTHON_VERSION%.*}

# Install pip for Python
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python${PYTHON_VERSION%.*} get-pip.py && \
    rm -f get-pip.py

# Set the working directory
WORKDIR /app

# By default, run a Python interactive shell
CMD ["python3"]