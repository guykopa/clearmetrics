import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "clearmetrics"
author = "clearmetrics team"
release = "0.1.0"
language = "en"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
]

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

napoleon_google_docstring = True
napoleon_include_init_with_doc = False

html_theme = "furo"
html_static_path = ["_static"]

exclude_patterns = ["_build"]
