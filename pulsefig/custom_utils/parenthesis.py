# Function to draw a parenthesis using a parametric equation of a curve
import numpy as np


def parenthesis_coordinates(x_center, y_center, height, width, direction="left"):
    y = np.linspace(-1, 1, 100)  # Generate y-values within the range
    x = width * np.sqrt(1 - (y**2))  # Elliptical equation x = sqrt(1 - y^2)
    if direction == "left":
        x = -x  # Invert for left parenthesis
    x += x_center  # Shift horizontally
    y = y * height + y_center  # Scale and shift vertically
    return x, y


def draw_parenthesis_between(ax, elm1, elm2, text: str, offset=0.1):
    parent_width = 0.2
    ax.plot(
        *parenthesis_coordinates(
            elm1.start - offset,
            1.25,
            height=1.5,
            width=parent_width,
            direction="left",
        ),
        color="black",
        lw=2,
    )
    ax.plot(
        *parenthesis_coordinates(
            elm2.end + offset,
            1.25,
            height=1.5,
            width=parent_width,
            direction="right",
        ),
        color="black",
        lw=2,
    )
    ax.text(elm2.end + parent_width + offset, 2.6, text, ha="left", va="center")
