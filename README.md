# Raw Astro Video Format (RAVF) Package

## Introduction

Python implementation of a reader/writer for the Raw Astro Video Format.

Specification: [RawAstroVideoFormat.md](docs/RawAstroVideoFormat.md)

RAVF is loosely based on the [Astro Digital Video](http://www.hristopavlov.net/adv/index.html) specification with an emphasis on writing in a variety of raw formats natively on CPU-bound hardware, where the goal is to get the data written quickly at higher frame rates sometimes needed for occultations.

Install:

	pip install "git+https://github.com/ChasinSpin/ravf.git"

Upgrade:

	pip install --upgrade --force-reinstall "git+https://github.com/ChasinSpin/ravf.git"`
