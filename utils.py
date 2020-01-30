import os


def makedir(s):
  if not os.path.exists(s):
    os.makedirs(s)