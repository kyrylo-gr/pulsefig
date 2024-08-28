"""
Advanced example
---

"""

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

fig.savefig("../figures/example_2.svg")
