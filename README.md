# Pabutools: PB as easy as [ABC](https://github.com/martinlackner/abcvoting)

[![PyPI Status](https://img.shields.io/pypi/v/pabutools.svg)](https://pypi.python.org/pypi/pabutools)
[![Build badge](https://github.com/pbvoting/pabutools/workflows/build/badge.svg?branch=main)](https://github.com/pbvoting/pabutools/actions/workflows/build.yml)
[![codecov](https://codecov.io/gh/pbvoting/pabutools/branch/main/graphs/badge.svg)](https://codecov.io/gh/pbvoting/pabutools/tree/main)

## Overview

The pabutools are a complete set of tools work with
participatory budgeting instances.

Participatory budgeting (PB) is a democratic tool used to allocate
a given amount of money to a collection of projects based on a
group of individuals' preferences over the projects. It has been invented
in Brazil in the late 80's and is now a widely implemented. See the
[Wikipedia page](https://en.wikipedia.org/wiki/Participatory_budgeting)
for more details.

In this library, we provide tools that
* handle PB instances of different kinds,
* compute voting rules to determine the outcome of the elections,
* analyse outcomes, and
* provide full support for the instances taken from the [pabulib](http://pabulib.org) library of PB data.

## Installation

The package can be installed [from PyPI](https://pypi.org/project/pabutools/) using:
```shell
pip3 install pabutools
```

## Documentation

The complete documentation is available [here](https://pbvoting.github.io/pabutools/).
It includes
* [installation instructions](https://pbvoting.github.io/pabutools/installation.html),
* a [short guide](https://pbvoting.github.io/pabutools/quickstart.html) for a quick start,
* a [complete guide](https://pbvoting.github.io/pabutools/usage.html) for more advanced usage, and
* a [reference guide](https://pbvoting.github.io/pabutools/reference/index.html) to get all the details.

## Development

We are more than happy to receive help with the development of the package.
If you want to contribute, here are some elements to take into account.

First, install the development dependencies by running the following command:
```shell
pip install -e ".[dev]"
```

You can run the unit tests with the following:
```shell
python -m unittest
```

The doc is generated using sphinx. We use the [numpy style guide](https://numpydoc.readthedocs.io/en/latest/format.html).
The [napoleon](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html) extension for Sphinx is used
and the HTML style is defined by the [Book Sphinx Theme](https://sphinx-book-theme.readthedocs.io/en/stable/).

To generate the doc, first move inside the `docs-source` folder and run the following:
```shell
make clean 
make html
```

This will generate the documentation locally (in the folder `docs-source/build`). If you want the documentation 
to also be updated when pushing, run:
```shell
make github
```

After having pushed, the documentation will automatically be updated.

Note that a large part of the documentation is done by hand (to ensure proper display and correct ordering). 
This means that if you create new class of functions that should appear in the documentation, you may have
to add they yourself using to autodoc directives (take inspiration from the files in `docs-source/source`). 

If you want to help, check the `todos.txt` file, several todos are described there.
