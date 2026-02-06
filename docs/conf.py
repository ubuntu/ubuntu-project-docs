import datetime
import os
import yaml
import re
from docutils.parsers.rst import roles
from sphinx.util.docutils import SphinxRole
from docutils import nodes

# Configuration for the Sphinx documentation builder.
# All configuration specific to your project should be done in this file.
#
# If you're new to Sphinx and don't want any advanced or custom features,
# just go through the items marked 'TODO'.
#
# A complete list of built-in Sphinx configuration values:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
#
# Our starter pack uses the custom Canonical Sphinx extension
# to keep all documentation based on it consistent and on brand:
# https://github.com/canonical/canonical-sphinx


#######################
# Project information #
#######################

# Project name
#
# TODO: Update with the official name of your project or product

project = "Ubuntu project"
author = "Canonical Ltd."


# Sidebar documentation title; best kept reasonably short
#
# TODO: To include a version number, add it here (hardcoded or automated).
#
# TODO: To disable the title, set to an empty string.

html_title = project + " documentation"


# Copyright string; shown at the bottom of the page
#
# Now, the starter pack uses CC-BY-SA as the license
# and the current year as the copyright year.
#
# TODO: If your docs need another license, specify it instead of 'CC-BY-SA'.
#
# TODO: If your documentation is a part of the code repository of your project,
#       it inherits the code license instead; specify it instead of 'CC-BY-SA'.
#
# NOTE: For static works, it is common to provide the first publication year.
#       Another option is to provide both the first year of publication
#       and the current year, especially for docs that frequently change,
#       e.g. 2022–2023 (note the en-dash).
#
#       A way to check a repo's creation date is to get a classic GitHub token
#       with 'repo' permissions; see https://github.com/settings/tokens
#       Next, use 'curl' and 'jq' to extract the date from the API's output:
#
#       curl -H 'Authorization: token <TOKEN>' \
#         -H 'Accept: application/vnd.github.v3.raw' \
#         https://api.github.com/repos/canonical/<REPO> | jq '.created_at'

copyright = "%s CC-BY-SA, %s" % (datetime.date.today().year, author)


# Documentation website URL
#
# TODO: Update with the official URL of your docs or leave empty if unsure.
#
# NOTE: The Open Graph Protocol (OGP) enhances page display in a social graph
#       and is used by social media platforms; see https://ogp.me/

ogp_site_url = "https://documentation.ubuntu.com/project/"


# Preview name of the documentation website
#
# TODO: To use a different name for the project in previews, update as needed.

ogp_site_name = project


# Preview image URL
#
# TODO: To customize the preview image, update as needed.

ogp_image = "https://assets.ubuntu.com/v1/cc828679-docs_illustration.svg"


# Product favicon; shown in bookmarks, browser tabs, etc.

# TODO: To customize the favicon, uncomment and update as needed.

# html_favicon = '.sphinx/_static/favicon.png'


# Dictionary of values to pass into the Sphinx context for all pages:
# https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_context

html_context = {
    # Product page URL; can be different from product docs URL
    #
    "product_page": "documentation.ubuntu.com",
    # Product tag image; the orange part of your logo, shown in the page header
    #
    # 'product_tag': '_static/tag.png',
    # Your Discourse instance URL
    #
    # NOTE: If set, adding ':discourse: 123' to an .rst file
    #       will add a link to Discourse topic 123 at the bottom of the page.
    "discourse": "https://discourse.ubuntu.com",
    # Your Mattermost channel URL
    #
    "mattermost": "",
    # Your Matrix channel URL
    #
    "matrix": "https://matrix.to/#/#devel:ubuntu.com",
    # Your documentation GitHub repository URL
    #
    # NOTE: If set, links for viewing the documentation source files
    #       and creating GitHub issues are added at the bottom of each page.
    "github_url": "https://github.com/ubuntu/ubuntu-project-docs",
    # Docs branch in the repo; used in links for viewing the source files
    #
    "repo_default_branch": "main",
    # Docs location in the repo; used in links for viewing the source files
    #
    "repo_folder": "/docs/",
    # To enable or disable the Previous / Next buttons at the bottom of pages
    # Valid options: none, prev, next, both
    # "sequential_nav": "both",
    # To enable listing contributors on individual pages, set to True
    "display_contributors": False,
    #
    # Required for feedback button
    "github_issues": "enabled",
}

html_extra_path = []

# To enable the edit button on pages, uncomment and change the link to a
# public repository on GitHub or Launchpad. Any of the following link domains
# are accepted:
# - https://github.com/example-org/example"
# - https://launchpad.net/example
# - https://git.launchpad.net/example

html_theme_options = {
    "source_edit_link": html_context["github_url"],
}

# Project slug; see https://meta.discourse.org/t/what-is-category-slug/87897
#
# If your documentation is hosted on https://docs.ubuntu.com/,
#       uncomment and update as needed.

slug = "project"


#######################
# Sitemap configuration: https://sphinx-sitemap.readthedocs.io/
#######################

# Use RTD canonical URL to ensure duplicate pages have a specific canonical URL
html_baseurl = os.environ.get("READTHEDOCS_CANONICAL_URL", "/")

# URL scheme.
sitemap_url_scheme = "{link}"

# Include `lastmod` dates in the sitemap:
sitemap_show_lastmod = True

# Exclude generated pages from the sitemap:

sitemap_excludes = [
    '404/',
    'genindex/',
    'search/',
]

# Template and asset locations
html_static_path = [".sphinx/_static"]
# templates_path = [".sphinx/_static/_templates"]


#############
# Redirects #
#############

# To set up redirects: https://documatt.gitlab.io/sphinx-reredirects/usage.html
# For example: 'explanation/old-name.html': '../how-to/prettify.html',

# To set up redirects in the Read the Docs project dashboard:
# https://docs.readthedocs.io/en/stable/guides/redirects.html

# NOTE: If undefined, set to None, or empty,
#       the sphinx_reredirects extension will be disabled.

redirects = {}

# Rediraffe (internal) redirects
# ------------------------------

rediraffe_branch = "main"
rediraffe_redirects = "redirects.txt"


###########################
# Link checker exceptions #
###########################

# A regex list of URLs that are ignored by 'make linkcheck'

linkcheck_ignore = [
    "http://127.0.0.1:8000",
    "https://www.gnu.org/*",
    "https://discourse.canonical.com/",
    "https://git.launchpad.net/ubuntu/+source/*",
    "https://wiki.ubuntu.com/*",
]


# A regex list of URLs where anchors are ignored by 'make linkcheck'

linkcheck_anchors_ignore_for_url = [
    r"https://github\.com/.*",
    r"https://matrix\.to/.*",
    r"https://git\.launchpad\.net/ubuntu/\+source/.*",
]

# give linkcheck multiple tries on failure
# linkcheck_timeout = 30
linkcheck_retries = 3

########################
# Configuration extras #
########################

# Custom MyST syntax extensions; see
# https://myst-parser.readthedocs.io/en/latest/syntax/optional.html
#
# NOTE: By default, the following MyST extensions are enabled:
#       substitution, deflist, linkify

myst_enable_extensions = {
    "colon_fence",
    "dollarmath",
    "tasklist",
    "fieldlist",
    "substitution",
    "html_admonition",
}


# Custom Sphinx extensions; see
# https://www.sphinx-doc.org/en/master/usage/extensions/index.html

# NOTE: The canonical_sphinx extension is required for the starter pack.

extensions = [
    "canonical_sphinx",
    "notfound.extension",
    "sphinx_design",
    "sphinx_reredirects",
    "sphinx_tabs.tabs",
    "sphinxcontrib.jquery",
    "sphinxext.opengraph",
    "sphinx_config_options",
    "sphinx_contributor_listing",
    "sphinx_filtered_toctree",
    "sphinx_related_links",
    "sphinx_roles",
    "sphinx_terminal",
    "sphinx_ubuntu_images",
    "sphinx_youtube_links",
    "sphinxcontrib.cairosvgconverter",
    "sphinx_last_updated_by_git",
    "sphinx.ext.intersphinx",
    "sphinx_sitemap",
    # Custom extensions for this docs set:
    "sphinx.ext.mathjax",
    "sphinxcontrib.mermaid",
    "hoverxref.extension",
    "sphinx_prompt",
    "sphinx.ext.extlinks",
    "sphinxext.rediraffe",
    "sphinx_togglebutton",
    "sphinx.ext.graphviz",
]

# Excludes files or directories from processing
exclude_patterns = ["maintainers/niche-package-maintenance/rustc/common"]


# Adds custom CSS files, located under 'html_static_path'
html_css_files = ["custom_styles.css"]


# Adds custom JavaScript files, located under 'html_static_path'
# html_js_files = []


# Specifies a reST snippet to be appended to each .rst file

rst_epilog = """
.. include:: /reuse/links.txt
"""

# Feedback button at the top; enabled by default
#
# To disable the button, uncomment this.

# disable_feedback_button = True


# Your manpage URL
#
#       To enable manpage links, uncomment and replace {codename} with required
#       release, preferably an LTS release (e.g. noble). Do *not* substitute
#       {section} or {page}; these will be replaced by sphinx at build time
#
# NOTE: If set, adding ':manpage:' to an .rst file
#       adds a link to the corresponding man section at the bottom of the page.

# manpages_url = 'https://manpages.ubuntu.com/manpages/{codename}/en/' + \
#     'man{section}/{page}.{section}.html'

stable_distro = "questing"

manpages_url = (
    "https://manpages.ubuntu.com/manpages/"
    + stable_distro
    + "/en/man{section}/{page}.{section}.html"
)

myst_substitutions = {
    "stable_distro": stable_distro,
    "release_schedule": "https://discourse.ubuntu.com/t/questing-quokka-release-schedule/36462",
}

# Configure hoverxref options
hoverxref_role_types = {
    "term": "tooltip",
}
hoverxref_roles = [
    "term",
]

# Configure copybutton extension
# This option excludes line numbers and prompts from being selected when
# users copy commands using the copybutton
# https://sphinx-copybutton.readthedocs.io/en/latest/use.html#automatic-exclusion-of-prompts-from-the-copies

# Following option only works when the 'console' syntax highlighting
# is used; better to use a regex.
# copybutton_exclude = ".linenos, .gp"

# Following regex stupidly using '|' because of a bug in copybutton ext.:
#         https://github.com/executablebooks/sphinx-copybutton/issues/96
# Replace with   r"(\S+@\S+)?[\$\#] "  when the bug is fixed.
copybutton_prompt_text = r"\S+@\S+[\$\#] |[\$\#] "
copybutton_prompt_is_regexp = True
copybutton_line_continuation_character = "\\"

# Specifies a reST snippet to be prepended to each .rst file
# This defines a :center: role that centers table cell content.
# This defines a :h2: role that styles content for use with PDF generation.

rst_prolog = """
.. role:: center
   :class: align-center
.. role:: h2
    :class: hclass2
.. role:: woke-ignore
    :class: woke-ignore
.. role:: vale-ignore
    :class: vale-ignore
"""


# Allow for use of link substitutions
extlinks = {
    "lpsrc": ("https://launchpad.net/ubuntu/+source/%s", "%s"),
    "lpbug": ("https://bugs.launchpad.net/bugs/%s", "LP: #%s"),
    "matrix": ("https://matrix.to/#/#%s:ubuntu.com", "#%s:ubuntu.com"),
}


# Workaround for https://github.com/canonical/canonical-sphinx/issues/34

if "discourse_prefix" not in html_context and "discourse" in html_context:
    html_context["discourse_prefix"] = html_context["discourse"] + "/t/"

# Workaround for substitutions.yaml

if os.path.exists("./reuse/substitutions.yaml"):
    with open("./reuse/substitutions.yaml", "r") as fd:
        myst_substitutions = yaml.safe_load(fd.read())

# Add configuration for intersphinx mapping

intersphinx_mapping = {
    "ubuntu-server": ("https://documentation.ubuntu.com/server/", None),
    "pkg-guide": (
        "https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/"
        "en/2.0-preview/",
        None,
    ),
    "starter-pack": (
        "https://canonical-starter-pack.readthedocs-hosted.com/latest/",
        None,
    ),
    "launchpad": ("https://documentation.ubuntu.com/launchpad/", None),
}


# Redefine the Sphinx 'command' role to behave/render like 'literal'


class CommandRole(SphinxRole):
    def run(self):
        text = self.text
        node = nodes.literal(text, text)
        return [node], []


def unescape_amp_in_links(app, exception):
    """
    Post-process HTML files to mitigate
      https://github.com/executablebooks/MyST-Parser/issues/1028
    by unescaping &amp;amp; to &amp;
    To be minimally invasive this is:
      - only changing text in href attributes
      - only affecting &amp;amp; (over just &amp;) which is a
        more clear indication of that bug
      - only affecting parametrized URLs that follow to an ?
      - only running for html builders
      - only writing on changed content
    """
    if exception:
        return

    # Only run for html builders
    if app.builder.format != 'html':
        return

    def unescape_match(match):
        return match.group(0).replace('&amp;amp;', '&amp;')

    for root, dirs, files in os.walk(app.outdir):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    new_content = re.sub(r'href=".*\?([^"]*)"',
                                         unescape_match, content)
                    if new_content != content:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                except Exception as e:
                    print(f"Failed to process {path}: {e}")


def setup(app):
    roles.register_local_role("command", CommandRole())
    app.connect('build-finished', unescape_amp_in_links)


# Define a custom role for package-name formatting
def pkg_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    node = nodes.literal(rawtext, text)
    return [node], []


roles.register_local_role("pkg", pkg_role)
