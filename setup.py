from setuptools import setup
from pathlib import Path

HERE = Path(__file__).parent


with open(HERE / "README.md", encoding="utf-8") as readme:
    long_description = readme.read()

setup(
    name='another-exponential-backoff',
    version='1.0.0',
    packages=['backoff'],
    url='https://github.com/dragdev-studios/exponential-backoff-python',
    project_urls={
        "Issue Tracker": "https://github.com/dragdev-studios/exponential-backoff-python",
        "Repository": "https://github.com/dragdev-studios/exponential-backoff-python"
    },
    include_package_data=True,
    license='MIT',
    author='EEKIM10',
    author_email='eek@clicksminuteper.net',
    description='Simple exponential backoff script',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
    extras_require={
        "tests": ["pytest"]
    }
)
