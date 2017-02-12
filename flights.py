#!/usr/bin/env python
# encoding: utf-8

import zipfile
import csv
import io
from sys import argv
from os.path import sep
import subprocess
import time
import os
import copy
import codecs
import translitcodec

debug = False

os.environ.setdefault("JAVA_HOME", "/usr/lib/jvm/jre")


class HdfsFile(io.TextIOWrapper):
    def __init__(self, path, namenode="hdfs://localhost:9000/"):
        self._proc = subprocess.Popen([
                             "/opt/hadoop/bin/hadoop", "fs",
                             "-fs", namenode,
                             "-put", "-", path,
                         ],
                         stdin=subprocess.PIPE)
        super().__init__(self._proc.stdin)


def open_zip(path):
    split_path = path.split('/')[-1].split('.')[0]
    print(split_path)
    with zipfile.ZipFile(path) as zz:
        print(zz.namelist())
        with zz.open(split_path + ".csv", mode='rU') as inside:
            analyse_csv(io.TextIOWrapper(inside, encoding='utf-8', errors='ignore'), split_path)


def analyse_csv(file_hand, out_name):
    reader = csv.DictReader(file_hand)

    with HdfsFile(sep + 'dataset' + sep + out_name + '.csv') as out_file:
        fdns = ['DayOfWeek', 'Origin', 'Dest', 'Carrier', 'DepDelay', 'ArrDelay']
        writer = csv.DictWriter(out_file, fieldnames=fdns)
        writer.writeheader()
        for row in reader:
            writer.writerow({k: codecs.encode(v, 'translit/long') for k, v in row.items() if k in fdns})


if __name__ == "__main__":
    try:
        open_zip(argv[1])
    except BrokenPipeError as e:
        print(e)
