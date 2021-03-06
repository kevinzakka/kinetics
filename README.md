# Kinetics Dataset

Python3 code to scrape YouTube clips for the Kinetics 700 dataset from [Deepmind](https://deepmind.com/).

[[Paper](https://arxiv.org/pdf/1907.06987.pdf)] - [[Webpage](https://deepmind.com/research/open-source/kinetics)]

**Disclaimer**. This is not an officially supported Deepmind project.

## Requirements

This library uses `youtube-dl` and `pandas` to scrape the dataset. Install them as follows:

```
pip install -r requirements.txt
```

## Usage

Start by downloading the list of YouTube video IDs from the Deepmind website by running the bash script below.

```bash
bash download.sh
```

You can now scrape the dataset by running `main.py`.

```bash
usage: main.py [-h] [--action_classes ACTION_CLASSES] [--vids_per VIDS_PER]
               [--split SPLIT] [--retry_fail RETRY_FAIL] [--verbose VERBOSE]

optional arguments:
  -h, --help            show this help message and exit
  --action_classes ACTION_CLASSES
                        Delimited list of action pairs to download.
  --vids_per VIDS_PER   Number of videos per action. Set to -1 to download
                        all.
  --split SPLIT         Which split to download.
  --retry_fail RETRY_FAIL
                        Whether to retry downloading failures.
  --verbose VERBOSE     Whether to print messages from youtube-dl and ffmpeg.
```

To download 20 videos per action on the **train** and **validation** splits as well as the unlabeled **test** split, run:

```
python main.py --split=all --vids_per=20
```

To download all videos in the **test** split in verbose mode, run:

```
python main.py --split=test --verbose=True
```

To download a specific subset of action classes specified as a comma-separated list, run:

```
python main.py --action_classes="archery,yawning,shining_shoes"
```
