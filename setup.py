from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='donkeyBriefing',
    version='0.1',
    author="Tom",
    author_email="grbtm@posteo.net",
    description="A RSS/Atom fueled daily briefing app",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/grbtm/project_donkey",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    python_requires='~=3.7',
)
