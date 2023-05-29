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

## Image Search web interface

1. Install dependencies. Make sure you already have [`nodejs`](https://nodejs.org/en/) & [`npm`](https://www.npmjs.com/) installed in your system, and are using python >= 3.10.
```bash
$ pip install -r requirements.txt
$ cd image-eye-web
$ npm install # or yarn
```

2. Run it
```bash
$ npm start # or yarn start
```
from the `image-search-web` directory. And, in a separate terminal,
```bash
$ python app.py
```
from the ImageEye directory.

## Image Search baseline interface

The same thing, but using the `image-eye-baseline` directory instead.

1. Install dependencies. Make sure you already have [`nodejs`](https://nodejs.org/en/) & [`npm`](https://www.npmjs.com/) installed in your system, and are using python >= 3.10.
```bash
$ pip install -r requirements.txt
$ cd image-eye-baseline
$ npm install # or yarn
```

2. Run it
```bash
$ npm start # or yarn start
```
from the `image-eye-baseline` directory. And, in a separate terminal,
```bash
$ python baseline_app.py
```
from the ImageEye directory.