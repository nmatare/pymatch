# pymatch

A lightweight pure-python centralized exchange matching engine

[![Python 3.7.11](https://img.shields.io/badge/python-3.7.11-blue.svg)](https://www.python.org/downloads/release/python-369/)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)![Unit Tests](https://github.com/nmatare/pymatch/actions/workflows/unit.yaml/badge.svg)

## Installation

### Docker

### Local

## Getting Started

### Docker

Start an orderbook instance in a Docker container named ``:

```sh
docker build . --tag pymatch
docker run pymatch --detach
```

Submit orders to the Docker container, observing trade messages as they occur:

```sh
docker exec -- ''
```

### Local

First, you will need to install the [conda package manager.](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html#install-linux-silent)

Next, create an isolated conda environment and then run the installation commands.


```sh
conda create --name pymatch python=3.7 --yes && conda activate pymatch
pip install pip --upgrade

pip install -e .[tests]
```

Run the testcases:

```sh
pytest pymatch/tests/
```

You can submit orders to the orderbook with the following command:
```sh
```
