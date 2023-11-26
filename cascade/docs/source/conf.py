# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("../../.."))

import cascade

# -- Project information -----------------------------------------------------

project = "cascade"
author = "Ilia Moiseev"
copyright = f"2022-2023, {author}"

# The full version, including alpha/beta/rc tags
release = cascade.__version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx.ext.mathjax",
    "sphinx.ext.extlinks",
    "sphinx_copybutton",
    "nbsphinx",
    "sphinx_design",
]

autodoc_default_options = {"special-members": "__init__", "undoc-members": False}

napoleon_include_special_with_doc = True
# napoleon_use_admonition_for_notes = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

html_theme = "pydata_sphinx_theme"
html_favicon = "_static/logo_sq.svg"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = [
    'css/custom.css',
]

html_theme_options = {
    "header_links_before_dropdown": 4,
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/oxid15/cascade",
            "icon": "fa-brands fa-github",
            "type": "fontawesome",
        }
    ],
    "switcher": {
        "json_url": "https://oxid15.github.io/cascade/en/latest/switcher.json",
        "version_match": "latest",
    },
    "navbar_start": ["navbar-logo", "version-switcher"],
    "logo": {
        "image_light": "_static/logo_light.svg",
        "image_dark": "_static/logo_dark.svg",
   }
}
