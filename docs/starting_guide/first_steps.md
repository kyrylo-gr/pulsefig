# Getting Started with `pulsefig`

Make sure you have [installed the package](install.md) before.

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

For more advance examples explore [more examples](../examples)
