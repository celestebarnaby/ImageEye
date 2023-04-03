# Using official ubuntu image as a parent image
FROM ubuntu:latest

# Setting the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# compile python from source - avoid unsupported library problems
RUN apt-get update \
    && apt-get install --assume-yes --no-install-recommends --quiet \
    python3 \
    python3-pip \
    python3-opencv \ 
    python3-boto3 \
    python3-tk \
    # z3 \
    && apt-get clean all

RUN pip3 install psutil

# Run testing.py when the container launches
CMD ["python3", "testing.py"]