# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join("..", "..")))
import pabutools

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "pabutools"
copyright = "2023, Simon Rey, Grzegorz Pierczyński, Markus Utke and Piotr Skowron"
author = "Simon Rey, Grzegorz Pierczyński, Markus Utke and Piotr Skowron"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.napoleon", "sphinx.ext.viewcode", "sphinx.ext.autodoc"]

add_module_names = False
autodoc_member_order = "groupwise"
autodoc_typehints_format = "short"
python_use_unqualified_type_names = True

napoleon_google_docstring = False

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

source_suffix = ".rst"
master_doc = "index"

version = pabutools.__version__
release = pabutools.__version__
language = "en"

pygments_style = "sphinx"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
# html_static_path = ["_static"]

html_title = "Pabutools"
html_theme_options = {
    "repository_url": "https://github.com/pbvoting/pabutools",
    "use_repository_button": True,
}
html_context = {"default_mode": "light"}
