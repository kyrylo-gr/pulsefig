
Simple example
---

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

fig.savefig("../figures/example_1.svg")

```
 ![example_1](figures/example_1.svg)