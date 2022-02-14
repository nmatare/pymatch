# pymatch

A lightweight pure-python centralized exchange matching engine

[![Python 3.7.11](https://img.shields.io/badge/python-3.7.11-blue.svg)](https://www.python.org/downloads/release/python-369/)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)![Unit Tests](https://github.com/nmatare/pymatch/actions/workflows/unit.yaml/badge.svg)


## Getting Started

### Docker (preferred)

Start a matching engine instance in a Docker container named `pymatch` by
running the following commands:

```sh
docker build -f tools/docker/Dockerfile . -t pymatch
```

Launch another terminal window and submit orders to the matching engine with
the following command:

```sh
echo $'B,1234567890,32503,1234567890\nB,1138,31502,7500' | docker run -i pymatch
```

Observe trade and book messages as they occur...

### Local Testing

First, you will need to install the [conda package manager.](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html#install-linux-silent)

Next, create an isolated conda environment and then run the installation commands:

```sh
conda create --name pymatch python=3.7 --yes && conda activate pymatch
pip install pip==22.0.3 --upgrade

pip install -e .[tests]
```

Run the testcases:

```sh
pytest pymatch/tests/
```

See the [`pymatch/tests/lse/test_lse_orderbook.py::test_profile_orderbook`](pymatch/tests/lse/test_lse_orderbook.py) testcase for submitting orders to the matching engine within python.

```sh
echo $'B,1234567890,32503,1234567890\nB,1138,31502,7500' | python -m pymatch.main
```

The output to stdout:

```sh
██████╗ ██╗   ██╗███╗   ███╗ █████╗ ████████╗ ██████╗██╗  ██╗
██╔══██╗╚██╗ ██╔╝████╗ ████║██╔══██╗╚══██╔══╝██╔════╝██║  ██║
██████╔╝ ╚████╔╝ ██╔████╔██║███████║   ██║   ██║     ███████║
██╔═══╝   ╚██╔╝  ██║╚██╔╝██║██╔══██║   ██║   ██║     ██╔══██║
██║        ██║   ██║ ╚═╝ ██║██║  ██║   ██║   ╚██████╗██║  ██║
╚═╝        ╚═╝   ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝

[WARNING] - Printing orderbook output to stdout. This will severly degrade performance! Set the `ENABLE_PROFILING=1` flag to enable profiling...
[INFO] - Expecting input from stdin...
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|1234567890|1,234,567,890| 32,503|       |             |          |
|      1138|        7,500| 31,502|       |             |          |

```

## Performance

Please note, performance is severely degraded if displaying messages to stdout is also enabled.

To profile the performance of the orderbook set the set the environment variable to `ENABLE_PROFILING=1`.

```sh
head pymatch/tests/lse/test_data/profile.txt

cat pymatch/tests/lse/test_data/profile.txt | ENABLE_PROFILING=1 python -m pymatch.main
```
