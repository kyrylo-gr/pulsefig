"""
`pulsefig`: Draw Your Pulse Sequences
=====================================


Quick Start
===========

Basic Usage
-----------

Here is a simple example to get you started with `pulsefig`:

```python

from pulsefig import Element, Line, LineEnsemble
import numpy as np
import matplotlib.pyplot as plt


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

plt.show()
```

This code will generate a plot of two pulse sequences defined by the `line1` and `line2` objects. You can customize each element, its functions, and styling to create complex and detailed pulse sequence diagrams.

Advanced Example
-------

In the following example, we create a more complex pulse sequence involving multiple lines, Gaussian pulses, and exponential filters:

```python
reset_line = Line("reset").attach_elements(Element(0, 5).set(xlabel="10μs"))
flux_line = Line("flux").attach_elements(
    flux_rise := Element.ExpFilter(0, 3.75, duration=0.2)
    .set(ylabel="Δᵩ")
    .update_style(alpha=0.3, data_index=0)
    .sweep_height(start_alpha=0.1)
)

drive_line  = Line("drive").attach_elements(
    drive_pi := Element.Gaussian(flux_rise, duration=1).set(subtitle="π")
)
readout_line = Line("readout").attach_elements(Element(drive_pi, duration=1, delay=0.5))

# Combine all lines into an ensemble
ens = drive_line  + readout_line + flux_line + reset_line

# Plotting the ensemble
fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))
ens.draw(ax1).config_ax(ax1)
fig.suptitle("Pulse Sequence Example")
plt.show()
```

In this advanced example:

- **Reset Line**: Represents a reset pulse with a duration of 5 units.
- **Flux Line**: Shows an exponential filter rising over time.
- **Drive Line**: Contains a Gaussian pulse corresponding to a π rotation.
- **Readout Line**: Follows the Gaussian pulse and includes a delay.

This sequence is typical in many quantum computing scenarios, where different pulse shapes and sequences are used to manipulate qubits.

Custom pulses
-----------------

You can create a completely custom shapes with `pulsefig`:

```python
from pulsefig import Element, Line, LineEnsemble
import numpy as np
import matplotlib.pyplot as plt

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
line2 = Line("flux").attach_elements(
    Element(0, 2)
    .set(alpha=0.3, marker="0", xlabel="dt", ylabel="amp")
    .attach_func(lambda x: np.sin(x * 2 * np.pi), end=0.25)
    .update_style(alpha=0.3, data_index=0)
    .sweep_height(start_alpha=0.1),
    Element(duration=4, delay=1)
    .attach_func(lambda x: np.sin(x * 2 * np.pi), end=0.25)
    .attach_func(lambda x: np.exp(-((x - 0.5) ** 2) / 0.05), start=0.5, end=1)
    .update_style(alpha=0.3, data_index=0)
    .sweep_height(start_alpha=0.1),
)

# Create a figure and axis
fig, ax = plt.subplots(1, 1)

# Combine the lines into an ensemble and draw
(line1 + line2).draw(ax).config_ax(ax)
```

This code will generate a plot of two pulse sequences defined by the `line1` and `line2` objects. You can customize each element, its functions, and styling to create complex and detailed pulse sequence diagrams.


"""

# flake8: noqa: F401
from .__config__ import __version__
from .element import Element
from .line import Line, LineEnsemble
