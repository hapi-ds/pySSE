"""User interface modules for Streamlit tabs."""

from .attribute_tab import render_attribute_tab
from .non_normal_tab import render_non_normal_tab
from .reliability_tab import render_reliability_tab
from .variables_tab import render_variables_tab

__all__ = [
    "render_attribute_tab",
    "render_variables_tab",
    "render_non_normal_tab",
    "render_reliability_tab",
]
