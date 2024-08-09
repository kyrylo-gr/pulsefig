# pulsefig. Try to make Matplotlib great again.

<h1 align="center">
<img src="images/pulsefig-logo.png" width="400">
</h1><br>

[![Pypi](https://img.shields.io/pypi/v/pulsefig.svg)](https://pypi.org/project/pulsefig/)
![Python 3.7+](https://img.shields.io/badge/python-3.7%2B-blue)
[![License](https://img.shields.io/badge/license-LGPL-green)](./LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![CodeFactor](https://www.codefactor.io/repository/github/kyrylo-gr/pulsefig/badge/main)](https://www.codefactor.io/repository/github/kyrylo-gr/pulsefig/overview/main)
[![Codecov](https://codecov.io/gh/kyrylo-gr/pulsefig/graph/badge.svg?token=5U0FU9XNID)](https://codecov.io/gh/kyrylo-gr/pulsefig)
[![Download Stats](https://img.shields.io/pypi/dm/pulsefig)](https://pypistats.org/packages/pulsefig)
[![Documentation](https://img.shields.io/badge/docs-blue)](https://kyrylo-gr.github.io/pulsefig/)

`pulsefig` - is a wrapper around Matplotlib that reduces the code required for plotting.

## Motivation

pulsefig is a wrapper around Matplotlib that reduces the code required for plotting. It makes the code shorter and more pleasant, while still maintaining generality.

Currently plotting with matplotlib is a nightmare. Normally there are so many line to plot a simple plot. Take as an example your code for plotting on grid 2x2 and count how make duplication information you have. So this library is a way how to write less to have the same plots. It’s a wrapper around Matplotlib and therefore you still have all function from it, so don’t worry to not have some functionality. But the main changes are the following:

- Every plot or set method on axes return the axes itself. Which allows your to stack command and
- You can create the list of the axes and do manipulations on a list. Like setting labels or plotting some data, which reduce by a lot the repeating information.
- As usual it’s typed as well as original matplotlib, there for you have hints to allow you very smooth manipulation.

Here's a simple example demonstrating how this package can significantly reduce the number of lines in your code. In this example, it went from 13 to 5 lines, remained perfectly readable and potentially prettier.

Matplotlib code:

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2)
x = np.linspace(0, 2 * np.pi, 100)
z = np.sin(x) + 1j * np.cos(x)

axes[0][0].plot(x, np.real(z))
axes[0][0].set_ylabel("Real")
axes[1][0].plot(x, np.imag(z))
axes[1][0].set_ylabel("Imag")
axes[0][1].plot(x, np.abs(z))
axes[0][1].set_ylabel("Amp")
axes[1][1].plot(x, np.unwrap(np.angle(z)))
axes[1][1].set_ylabel("Phase")
for axes_row in axes:
    for ax in axes_row:
        ax.set(xlabel="Time (s)")
fig.suptitle("Complex Signal")
fig.tight_layout()
```

pulsefig compact code

```python
import pulsefig as ap
x = np.linspace(0, 2 * np.pi, 100)
z = np.sin(x) + 1j * np.cos(x)

axes = (
    ap.axs(2, 2)
    .plot(x, [[np.real(z), np.abs(z)], [np.imag(z), np.unwrap(np.angle(z))]])
    .suptitle("Complex Signal")
    .set(xlabel="Time (s)", ylabel=[["Real", "Abs"], ["Imag", "Phase"]])
    .tight_layout()
)
```

You can also access the axes as usual.

```python
axes = (
    ap.axs(2, 2)
    .suptitle("Complex Signal")
    .set(xlabel="Time (s)", ylabel=[["Real", "Abs"], ["Imag", "Phase"]])
    .tight_layout()
)
axes[0].plot(x, [np.real(z), np.abs(z)])
axes[1][0].plot(x, np.imag(z))
axes[1][1].plot(x, np.unwrap(np.angle(z)))
```

You can use `autoaxis` method to let is name the axis for your draft plots

```python
axes = (
    ap.axs(2, 2)
    .plot(x, [[np.real(z), np.abs(z)], [np.imag(z), np.unwrap(np.angle(z))]])
    .suptitle("Complex Signal")
    .autoaxis()
    .tight_layout()
)
```

## Install

`pip install pulsefig`

For more installation details, please refer to the [How to install](starting_guide/install.md)

## How to use

For further insight, please refer to the [First Steps guide](starting_guide/first_steps.md)
