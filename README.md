# ImageEye: Batch Image Editing with Program Synthesis

This is a Docker image for running the experiments in "ImageEye: Batch Image Editing with Program Synthesis"

## How to Run

To load the saved image, use `docker load -i imageeye.tar`. To build the image from source code, use `docker build -t imageeye:v1 .`. Run the image with `docker run -v [PATH]:/ImageEye/data imageeye:v1`, where [PATH] is the location on your machine that you would like the results to be output to. The image runs the following experiments:

1. Runs ImageEye on 50 benchmarks as described in the paper.
2. Runs ablations for no goal inference, no partial evaluation, and no equivalence reduction.
3. Compares with EUSolver.

The results are summarized in csv files. It took about 5 hours to run everything on my machine.