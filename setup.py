# -*- coding: utf-8 -*-
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

print("packages: %s"%setuptools.find_packages("."))

setuptools.setup(
    name='tweet2latex',
    version='1.1',
    scripts=['tweet2latex.py'],
    author="Václav Haisman",
    author_email="vhaisman+tweet2latex@gmail.com",
    description="Utility to retrieve tweets and format them into LaTeX fragments.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wilx/tweet2latex/",
    packages=setuptools.find_packages(),
    classifiers=[
         "Development Status :: 4 - Beta",
         "Topic :: Utilities",
         "Topic :: Internet",
         "Topic :: Text Processing :: Markup :: LaTeX",
         "Programming Language :: Python :: 3",
         "Programming Language :: Python :: 2",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent"
    ],
    install_requires=[
          'twarc',
          'six',
          'PyICU'
    ],
)
