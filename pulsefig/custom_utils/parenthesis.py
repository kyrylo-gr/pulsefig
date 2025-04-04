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
    ax,
    elm1,
    elm2,
    text: str,
    offset=0.1,
    lw=1.5,
    color="black",
    text_y_coord=2.6,
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
    ax.text(
        elm2.end + parent_width + offset,
        text_y_coord,
        text,
        ha="left",
        va="center",
    )


def draw_repeat_between(
    ax,
    elm1,
    elm2,
    text: str,
    offset=0.1,
    lw=(1, 2),
    color="black",
    markersize=5,
    y_center=None,
    height=None,
    text_y_offset=0,
    point_y_offset=0.25,
):
    parent_width = 0.2
    if y_center is None:
        y_center = max(elm1.y_offset, elm2.y_offset)
    if height is None:
        height = abs(elm1.y_offset - elm2.y_offset)
    start = getattr(elm1, "start", elm1)
    end = getattr(elm2, "end", elm2)

    ax.plot(
        [start - offset, start - offset],
        [y_center - point_y_offset, y_center + point_y_offset],
        "o",
        color=color,
        markersize=markersize,
    )
    ax.plot(
        [start - 2 * offset, start - 2 * offset],
        [y_center - height, y_center + height],
        color=color,
        lw=lw[0],
    )
    ax.plot(
        [start - 3 * offset, start - 3 * offset],
        [y_center - height, y_center + height],
        color=color,
        lw=lw[1],
    )
    ax.plot(
        [end + offset, end + offset],
        [y_center - point_y_offset, y_center + point_y_offset],
        "o",
        color=color,
        markersize=markersize,
    )
    ax.plot(
        [end + 2 * offset, end + 2 * offset],
        [y_center - height, y_center + height],
        color=color,
        lw=lw[0],
    )
    ax.plot(
        [end + 3 * offset, end + 3 * offset],
        [y_center - height, y_center + height],
        color=color,
        lw=lw[1],
    )

    ax.text(
        end + parent_width + 3 * offset,
        y_center + height + text_y_offset,
        text,
        ha="left",
        va="top",
    )
