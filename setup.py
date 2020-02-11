from setuptools import setup

from slack_integration.version import __version__

setup(
    version=__version__,
    install_requires=["slackclient"]
)