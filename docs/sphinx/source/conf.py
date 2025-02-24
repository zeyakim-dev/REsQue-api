import os
import sys

sys.path.insert(0, os.path.abspath("../../"))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "REsQue-api"
copyright = "2025, zeyakim-dev"
author = "zeyakim-dev"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# docs/sphinx/source/conf.py

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosectionlabel',  # 추가
    'sphinxcontrib.mermaid'
]

templates_path = ["_templates"]
exclude_patterns = []

language = "ko"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
# html_static_path = ['_static']

# Mermaid 설정 (선택 사항)
mermaid_output_format = "raw"  # 'png' 또는 'svg'로 변경 가능
mermaid_version = "10.3.0"  # 특정 버전 지정
mermaid_init_js = """
mermaid.initialize({
    theme: 'dark',
    securityLevel: 'loose'
});
"""

# 문서 전체에서 고유한 섹션 ID 생성
autosectionlabel_prefix_document = True

# 최대 헤딩 깊이 제한 (1: #, 2: ##, ...)
autosectionlabel_maxdepth = 3
