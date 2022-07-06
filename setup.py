from pip._internal.operations import freeze
import os

with open('requirements.txt', 'r') as req:
    requirements = req.readlines()
    installed = freeze.freeze()

    for line in requirements:
        if line.strip() in installed:
            continue
        else:
            os.system(f'pip install {line.strip()}')
