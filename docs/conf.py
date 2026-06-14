# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os, sys
from dotenv import load_dotenv

# Додаємо шлях до кореня проєкту
sys.path.insert(0, os.path.abspath('..'))

# Завантажуємо змінні середовища з .env
load_dotenv(dotenv_path=os.path.join(os.path.abspath('..'), '.env'))

project = 'Rest API'
copyright = '2026, Kalynychenko'
author = 'Kalynychenko'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',      # Автоматична генерація з docstrings
    'sphinx.ext.napoleon',     # Підтримка Google/NumPy стилю docstrings
    'sphinx.ext.viewcode',     # Додає посилання на вихідний код
    'sphinx.ext.coverage'      # Перевірка покриття документації
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'en'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'nature'
html_static_path = ['_static']

# Опції autodoc
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True
}
