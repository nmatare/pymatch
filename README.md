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
echo A,6808,32505,7777\nB,1138,31502,7500\nA,42100,32507,300 \
| docker run -i -e ENABLE_PROFILING=0 pymatch
```

Observe trade and book messages as they occur...

### Local Testing

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

See the [`pymatch/tests/lse/test_lse_orderbook.py::test_profile_orderbook`](pymatch/tests/lse/test_lse_orderbook.py) testcase for submitting orders to the matching engine within python.

```python
from pymatch import lse as lse_order_lib

orderbook = lse_order_lib.LSEOrderbook()

buy_order = lse_order_lib.build_order_from_ascii_string('B,1234567890,32503,1234567890')

orderbook.add(buy_order)
```

The output to stdout:

```python
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|1234567890|1,234,567,890| 32,503|       |             |          |
+-----------------------------------------------------------------+
```

## Performance

Please note, performance is severely degraded if displaying messages to stdout is also enabled.

To profile the performance of the orderbook set the set the environment variable to `ENABLE_PROFILING=1`.

```sh
head pymatch/tests/lse/test_data/orders.txt

cat pymatch/tests/lse/test_data/orders.txt | docker run -i -e ENABLE_PROFILING=1 pymatch
```
