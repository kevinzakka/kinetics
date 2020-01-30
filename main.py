import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np
import pandas as pd
import utils


def dump_json(ns, ls):
  for n, l in zip(ns, ls):
    with open(n, "w") as f:
      json.dump(l, f, indent="")


def scrape_test(verbose):
  # create folder
  foldername = os.path.join("./data/", "test")
  utils.makedir(foldername)
  # read previously saved video errors
  failname = os.path.join(foldername, "failures.json")
  try:
    with open(failname, "r") as f:
      video_errors = json.load(f)
  except:
    video_errors = []
  # read previously downloaded videos
  succname = os.path.join(foldername, "successes.json")
  try:
    with open(succname, "r") as f:
      video_successes = json.load(f)
  except:
    video_successes = []
  # read csv file
  try:
    db = pd.read_csv(os.path.join("data/kinetics700/test.csv"))
  except FileNotFoundError:
    print("[!] Could not find the kinetics700 folder. Download it by running the bash script.")
    sys.exit()
  # remove any video that's already been downloaded
  # and exit if no more to download
  print("[*] Trimming {} already downloaded videos.".format(len(video_successes+video_errors)))
  db = db[~db['youtube_id'].isin(video_successes+video_errors)]
  if len(db) == 0:
    print("[*] No more {} videos to download. Exiting.".format(split))
    return
  print("[*] Downloading {} videos.".format(len(db)))
  counter = 0
  for index, vid in db.iterrows():
    tmp = os.path.join(foldername, 'tmp.mp4')
    videoname = os.path.join(foldername, vid.youtube_id + '.mp4')
    # downloading a video can sometimes fail because
    # the account has been terminated.
    # for now, we simply skip the video if we're unable
    # to download it
    quiet_yt = """""" if verbose else """ -q --no-warnings"""
    quiet_ff = """""" if verbose else """ -nostats -loglevel 0"""
    try:
      # download full video
      dl_cmd = """youtube-dl""" + quiet_yt + """ -f mp4 -o {} https://www.youtube.com/watch?v={}"""
      subprocess.call(dl_cmd.format(tmp, vid.youtube_id), shell=True)
      # trim the specified duration
      trim_cmd = """ffmpeg""" + quiet_ff + """ -ss {} -i {} -to {} -c copy {}"""
      duration = vid.time_end - vid.time_start
      subprocess.call(trim_cmd.format(vid.time_start, tmp, duration, videoname), shell=True)
      # delete full video
      os.remove(tmp)
      video_successes.append(vid.youtube_id)
      print("{}/{} - success".format(counter, len(db)))
    except KeyboardInterrupt:
      print("[*] Control-C detected. Exiting.")
      dump_json([failname, succname], [video_errors, video_successes])
      sys.exit()
    except Exception:
      video_errors.append(vid.youtube_id)
      print("{}/{} - failure".format(counter, len(db)))
    counter += 1
  dump_json([failname, succname], [video_errors, video_successes])


def scrape_train_validate(splits, vids_per, verbose):
  for split in splits:
    # create folder
    foldername = os.path.join("./data/", split)
    utils.makedir(foldername)
    # read previously saved video errors
    failname = os.path.join(foldername, "failures.json")
    try:
      with open(failname, "r") as f:
        video_errors = json.load(f)
    except:
      video_errors = {}
    # read previously downloaded videos
    succname = os.path.join(foldername, "successes.json")
    try:
      with open(succname, "r") as f:
        video_successes = json.load(f)
    except:
      video_successes = {}
    # read csv file
    try:
      db = pd.read_csv(os.path.join("data/kinetics700/{}.csv".format(split)))
    except FileNotFoundError:
      print("[!] Could not find the kinetics700 folder. Download it by running the bash script.")
      sys.exit()
    # remove any video that's already been downloaded
    # and exit if no more to download
    id_succ = []
    for key, val in video_successes.items():
      id_succ.extend(val)
    id_err = []
    for key, val in video_errors.items():
      id_err.extend(val)
    print("[*] Trimming {} already downloaded videos.".format(len(id_succ+id_err)))
    db = db[~db['youtube_id'].isin(id_succ+id_err)]
    if len(db) == 0:
      print("[*] No more {} videos to download. Exiting.".format(split))
      return
    # stratified subsampling
    if vids_per != -1:
      vids_by_action = db.groupby('label', group_keys=False).apply(
        lambda x: x.sample(min(len(x), vids_per)))
    else:
      vids_by_action = db
    print("[*] Downloading {} videos.".format(len(vids_by_action)))
    counter = 0
    # make a folder for each type of action
    actions = vids_by_action['label'].unique().tolist()
    actions = [a.replace(" ", "_") for a in actions]
    if not video_successes:
      video_successes = {key: [] for key in actions}
    if not video_errors:
      video_errors = {key: [] for key in actions}
    for action in actions:
      utils.makedir(os.path.join(foldername, action))
    for index, vid in vids_by_action.iterrows():
      action = vid.label.replace(" ", "_")
      tmp = os.path.join(foldername, action, 'tmp.mp4')
      videoname = os.path.join(foldername, action, vid.youtube_id + '.mp4')
      # downloading a video can sometimes fail because
      # the account has been terminated.
      # for now, we simply skip the video if we're unable
      # to download it
      quiet_yt = """""" if verbose else """ -q --no-warnings"""
      quiet_ff = """""" if verbose else """ -nostats -loglevel 0"""
      try:
        # download full video
        dl_cmd = """youtube-dl""" + quiet_yt + """ -f mp4 -o {} https://www.youtube.com/watch?v={}"""
        subprocess.call(dl_cmd.format(tmp, vid.youtube_id), shell=True)
        # trim the specified duration
        trim_cmd = """ffmpeg""" + quiet_ff + """ -ss {} -i {} -to {} -c copy {}"""
        duration = vid.time_end - vid.time_start
        subprocess.call(trim_cmd.format(vid.time_start, tmp, duration, videoname), shell=True)
        # delete full video
        os.remove(tmp)
        video_successes[action].append(vid.youtube_id)
        print("{}/{} - success".format(counter, len(vids_by_action)))
      except KeyboardInterrupt:
        print("[*] Control-C detected. Exiting.")
        dump_json([failname, succname], [video_errors, video_successes])
        sys.exit()
      except Exception:
        video_errors[action].append(vid.youtube_id)
        print("{}/{} - error".format(counter, len(vids_by_action)))
      counter += 1
  dump_json([failname, succname], [video_errors, video_successes])


def main(args):
  splits = ["train", "validate"]
  if args.split == "all":
    scrape_train_validate(splits, args.vids_per, args.verbose)
    scrape_test(args.verbose)
  elif args.split == "train":
    scrape_train_validate(splits[:1], args.vids_per, args.verbose)
  elif args.split in ["valid", "validate"]:
    scrape_train_validate(splits[-1:], args.vids_per, args.verbose)
  elif args.split == "test":
    scrape_test(args.verbose)
  else:
    raise ValueError("[!] {} split not supported.".format(args.split))


if __name__ == "__main__":
  def str2bool(s):
    return s.lower() in ['true', '1']
  parser = argparse.ArgumentParser()
  parser.add_argument("--vids_per", type=int, default=50,
                      help="Number of videos per action. Set to -1 to download all.")
  parser.add_argument("--split", type=str, default="all",
                      help="Which split to download.")
  parser.add_argument("--verbose", type=str2bool, default=False,
                      help="Whether to print messages from youtube-dl and ffmpeg.")
  args, unparsed = parser.parse_known_args()
  main(args)