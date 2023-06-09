# ImageEye

ImageEye uses neuro-symbolic synthesis to automate image search and manipulation tasks. ImageEye was introduced in our paper [ImageEye: Batch Image Processing Using Program Synthesis](https://arxiv.org/abs/2304.03253). 

## Installation

Requirement: Python3 (version >=3.10), we suggest using the conda environment.

1. Install pip: conda install pip
2. Run requirements `pip install -r requirements.txt`

If there are more installation necessary to run this package, please update README and requirements.txt.

## How to Run the Docker Image

We have a Docker Image that reproduces the results in our paper. To load the saved image, use `docker load -i imageeye.tar`. To build the image from source code, use `docker build -t imageeye:v1 .`. Run the image with `docker run -v [PATH]:/ImageEye/data imageeye:v1`, where [PATH] is the location on your machine that you would like the results to be output to. The image runs the following experiments:

1. Runs ImageEye on 50 benchmarks as described in the paper.
2. Runs ablations for no goal inference, no partial evaluation, and no equivalence reduction.
3. Compares with EUSolver.

The results are summarized in csv files. It took about 5 hours to run everything on my machine.

## How to Run the GUI

We have a graphical user interface for ImageEye as well. You can run the GUI as follows:

1. [Install Node.js and npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
2. From the `image-eye-web` directory, run `npm install` and then `npm start`.
3. In a separate terminal (in the main `ImageEye` directory), run `python app.py`.
4. The interface should open in your browser.

This GUI is a work in progress. It currently has the following limitations:
- Only supports image search.
- Does not allow you to upload your own image batch. You can select from a set list of images batches.
- Does not allow you to download results.
