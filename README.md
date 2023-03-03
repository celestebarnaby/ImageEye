# ImageEye: Batch Image Editing with Program Synthesis

This is the codebase for the paper "ImageEye: Batch Image Processing Using Program Synthesis."

## Getting Started

This code was tested on Python 3.10

<b>Install the required libraries:</b>
```
$ pip3 install -r requirements.txt
```
To use the boto3 API, you will also need a file called `credentials.csv` in your repository containing your [AWS credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html).

## Benchmarks

Run benchmarks with `python3 testing.py`. Results will be output to `data` directory. The test images we used for evaluation are not in this repository, but their abstract representations are stored in `test_images.json`.

### Ablations

You can run the ablations listed in the paper with the following commands:

1. No goal inference: `python3 testing.py -- --goal-inference=False`
2. No partial evaluation: `python3 testing.py -- --partial-eval=False`
3. No equivalence reduction: `python3 testing.py -- --equiv-reduction=False`

### Comparison with EUSolver

Our EUSolver implementation is in the `eusolver` directory. You can run it as follows:
1. Run `./scripts/build.sh` 
2. Run `python3 gen_imgeye_benchmarks.py` from the `eusolver/src/imgeye` directory
3. Results will be output to `eusolver/src/imgeye/data`

## Command Line Tool

Our current interface is a pretty simple command line tool, but it gets the job done. To start the tool, run `python3 synthesizer.py -- --imgdir=YOUR_DIRECTORY`. You will be prompted to select an image to annotate. Once the image is displayed, select the objects and the action you would like to apply. Then press q. You will be asked on the command line whether you want to annotate another image. If you answer no, the synthesizer will run. Once a program that matches your example(s) is synthesized, the program will be applied to all images in `YOUR_DIRECTORY`. The edited images will be saved to the `output` directory.
 
