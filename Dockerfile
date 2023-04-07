# Using official ubuntu image as a parent image
FROM ubuntu:latest

# Setting the working directory to /app
WORKDIR /ImageEye

# Copy the current directory contents into the container at /app
COPY . /ImageEye

# compile python from source - avoid unsupported library problems
RUN apt-get update \
    && apt-get install --assume-yes --no-install-recommends --quiet \
    make \
    gcc \
    clang \
    clang-tools \
    cmake \
    protobuf-compiler \
    python3 \
    python3-pip \
    python3-opencv \ 
    python3-boto3 \
    python3-tk \
    && apt-get clean all

RUN pip3 install pyparsing
RUN pip3 install z3-solver

# Run testing.py when the container launches
CMD ["/bin/bash", "-c", "python3 testing.py;python3 testing.py --no_goal_inference; python3 testing.py --no_partial_eval;python3 testing.py --no_equiv_reduction; mkdir eusolver/thirdparty/libeusolver/build; cd eusolver; ./scripts/build.sh; cd src/imgeye; python3 gen_imgeye_benchmarks.py"]