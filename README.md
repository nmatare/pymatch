# pymatch

A lightweight pure-python centralized exchange matching engine

[![Python 3.7.11](https://img.shields.io/badge/python-3.7.11-blue.svg)](https://www.python.org/downloads/release/python-369/)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)![Unit Tests](https://github.com/nmatare/pymatch/actions/workflows/unit.yaml/badge.svg)


## Getting Started

### Docker

Start a matching engine instance in a Docker container named `pymatch` by
running the following commands:

```sh
docker build . --tag pymatch
docker run pymatch
```

Launch another terminal window and submit orders to the matching engine with
the following command:

```sh
docker exec -- ''
```

Observe trade and book messages as they occur:

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

See the [`pymatch/tests/test_orderbook.py::test_profile_orderbook`](pymatch/tests/test_orderbook.py) testcase for submitting orders to the matching engine within python.

```python
from pymatch import order as order_lib, orderbook as orderbook_lib

orderbook = orderbook_lib.PriceTimePriorityOrderbook(output_stdout=True)

x = 'B,1234567890,32503,1234567890'
buy_order = order_lib.build_order_from_ascii_string(x)

orderbook.add(buy_order)
```
