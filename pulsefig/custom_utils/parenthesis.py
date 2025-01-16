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


def draw_parenthesis_between(
    ax, elm1, elm2, text: str, offset=0.1, lw=1.5, color="black"
):
    parent_width = 0.2
    ax.plot(
        *parenthesis_coordinates(
            elm1.start - offset,
            1.25,
            height=1.5,
            width=parent_width,
            direction="left",
        ),
        color=color,
        lw=lw,
    )
    ax.plot(
        *parenthesis_coordinates(
            elm2.end + offset,
            1.25,
            height=1.5,
            width=parent_width,
            direction="right",
        ),
        color=color,
        lw=lw,
    )
    ax.text(elm2.end + parent_width + offset, 2.6, text, ha="left", va="center")


def draw_repeat_between(
    ax,
    elm1,
    elm2,
    text: str,
    offset=0.1,
    lw=(1, 2),
    color="black",
    markersize=5,
    y_center=1.5,
    point_y_offset=0.25,
    height=1.25,
):
    parent_width = 0.2

    ax.plot(
        [elm1.start - offset, elm1.start - offset],
        [y_center - point_y_offset, y_center + point_y_offset],
        "o",
        color=color,
        markersize=markersize,
    )
    ax.plot(
        [elm1.start - 2 * offset, elm1.start - 2 * offset],
        [y_center - height, y_center + height],
        color=color,
        lw=lw[0],
    )
    ax.plot(
        [elm1.start - 3 * offset, elm1.start - 3 * offset],
        [y_center - height, y_center + height],
        color=color,
        lw=lw[1],
    )
    ax.plot(
        [elm2.end + offset, elm2.end + offset],
        [y_center - point_y_offset, y_center + point_y_offset],
        "o",
        color=color,
        markersize=markersize,
    )
    ax.plot(
        [elm2.end + 2 * offset, elm2.end + 2 * offset],
        [y_center - height, y_center + height],
        color=color,
        lw=lw[0],
    )
    ax.plot(
        [elm2.end + 3 * offset, elm2.end + 3 * offset],
        [y_center - height, y_center + height],
        color=color,
        lw=lw[1],
    )

    ax.text(
        elm2.end + parent_width + 3 * offset,
        y_center + height,
        text,
        ha="left",
        va="top",
    )
