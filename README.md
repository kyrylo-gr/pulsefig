# `pulsefig`: Draw Your Pulse Sequences

<h1 align="center">
<img src="docs/images/pulsefig-logo.png" width="400">
</h1><br>

[![Pypi](https://img.shields.io/pypi/v/pulsefig.svg)](https://pypi.org/project/pulsefig/)
![Python 3.7+](https://img.shields.io/badge/python-3.7%2B-blue)
[![License](https://img.shields.io/badge/license-LGPL-green)](./LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![CodeFactor](https://www.codefactor.io/repository/github/kyrylo-gr/pulsefig/badge/main)](https://www.codefactor.io/repository/github/kyrylo-gr/pulsefig/overview/main)
[![Codecov](https://codecov.io/gh/kyrylo-gr/pulsefig/graph/badge.svg?token=5U0FU9XNID)](https://codecov.io/gh/kyrylo-gr/pulsefig)
[![Download Stats](https://img.shields.io/pypi/dm/pulsefig)](https://pypistats.org/packages/pulsefig)
[![Documentation](https://img.shields.io/badge/docs-blue)](https://kyrylo-gr.github.io/pulsefig/)

`pulsefig` is a Python library designed for easy and intuitive drawing of pulse sequences, commonly used in quantum computing, nuclear magnetic resonance (NMR), and other fields that involve waveform manipulation. The library simplifies the process of visualizing pulse sequences by providing flexible and powerful tools to define, customize, and plot these sequences.

## Installation

You can install `pulsefig` via pip:

```bash
pip install pulsefig
```

For more detailed installation instructions, please refer to the [How to install](starting_guide/install.md) guide.

## Quick Start

### Basic Usage

Here is a simple example to get you started with `pulsefig`:

```python

import matplotlib.pyplot as plt

from pulsefig import Element, Line

# Define a line with elements attached
line1 = Line("line1").attach_elements(
    Element(0, 1),
    Element(2, 4),
)

# Define another line
line2 = Line("line2").attach_elements(
    Element(0, 2),
    Element(duration=4, delay=1),
)

# Create a figure and axis
fig, ax = plt.subplots(1, 1)

# Combine the lines into an ensemble and draw
(line1 + line2).draw(ax).config_ax(ax)

```

This code will generate a plot of two pulse sequences defined by the `line1` and `line2` objects. You can customize each element, its functions, and styling to create complex and detailed pulse sequence diagrams.
![basic example](docs/examples/figures/example_1.svg)

### Advanced Example

In the following example, we create a more complex pulse sequence involving multiple lines, Gaussian pulses, and exponential filters:

```python

import matplotlib.pyplot as plt

from pulsefig import Element, Line

reset_line = Line("reset").attach_elements(Element(0, 5).set(xlabel="10μs"))
flux_line = Line("flux").attach_elements(
    flux_rise := Element.ExpFilter(0, 3.75, duration=0.2)
    .set(ylabel=" Δᵩ")
    .update_style(alpha=0.3, data_index=0)
    .sweep_height(start_alpha=0.1)
)

drive_line = Line("drive").attach_elements(
    drive_pi := Element.Gaussian(flux_rise, duration=1).set(subtitle="π")
)
readout_line = Line("readout").attach_elements(Element(drive_pi, duration=1, delay=0.5))

# Combine all lines into an ensemble
ens = drive_line + readout_line + flux_line + reset_line

# Plotting the ensemble
fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))
ens.draw(ax1).config_ax(ax1)

```

In this advanced example:

- **Reset Line**: Represents a reset pulse with a duration of 5 units.
- **Flux Line**: Shows an exponential filter rising over time.
- **Drive Line**: Contains a Gaussian pulse corresponding to a π rotation.
- **Readout Line**: Follows the Gaussian pulse and includes a delay.

This sequence is typical in many quantum computing scenarios, where different pulse shapes and sequences are used to manipulate qubits.

![example_2](docs/examples/figures/example_2.svg)

### Custom pulses

You can create a completely custom shapes with `pulsefig`:

```python
import matplotlib.pyplot as plt
import numpy as np

from pulsefig import Element, Line

fig, ax = plt.subplots(1, 1)

# Define a line with elements attached
line1 = Line("drive").attach_elements(
    Element(0, 1)
    .attach_func(lambda x: np.sin(x * 2 * np.pi), end=0.25)
    .attach_func(lambda x: np.exp(-((x - 0.5) ** 2) / 0.05), start=0.5, end=1)
    .update_style(alpha=0.3, data_index=0)
    .sweep_height(start_alpha=0.1)
    .set(subtitle="pi", xlabel="dt"),
    Element(2, 4)
    .attach_func(lambda x: np.sin(x * 2 * np.pi), end=0.25)
    .attach_func(lambda x: np.exp(-((x - 0.5) ** 2) / 0.05), start=0.5, end=1)
    .update_style(alpha=0.3, data_index=0)
    .sweep_height(start_alpha=0.1),
)

# Define another line
line2 = Line("g_h").attach_elements(
    Element(1, 3)
    .set(alpha=0.3, marker="0")
    .set_subtitle("pi", xpos=0.3)
    .set_ylabel("amp", xpos=0.4, ypos=0.65)
    .set_xlabel("dt", xpos=0.3)
    .attach_func(lambda x: np.sin(x * 2 * np.pi), end=0.25)
    .attach_func(lambda x: np.exp(-((x - 0.5) ** 2) / 0.05), start=0.5, end=1)
    .update_style(alpha=0.3, data_index=0)
    .sweep_height(start_alpha=0.1),
)

# Combine the lines into an ensemble and draw
(line1 + line2).draw(ax).config_ax(ax)
```

This code will generate a plot of two pulse sequences defined by the `line1` and `line2` objects. You can customize each element, its functions, and styling to create complex and detailed pulse sequence diagrams.

![example_3](docs/examples/figures/example_3.svg)

## Documentation

For more detailed documentation, including additional examples, API reference, and tutorials, please visit the [pulsefig Documentation](https://kyrylo-gr.github.io/pulsefig/).

## Contributing

Contributions are welcome! If you would like to contribute to `pulsefig`, please take a look at our [contributing guide](CONTRIBUTING.md).

## License

`pulsefig` is licensed under the LGPL License. See the [LICENSE](./LICENSE) file for more details.

---

Feel free to explore the examples, customize the sequences, and integrate `pulsefig` into your projects for pulse sequence visualization!
