from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    README = readme_file.read()

requirements = ["numpy", "pandas", "matplotlib"]

setup(name="mortgages",
      version="0.0.1",
      author="Sean Brunson",
      author_email="sean.brunson25@gmail.com",
      description="A package to calculate mortgage payments",
      long_description=README,
      url="https://github.com/SeanBrunson/mortgages",
      packages=find_packages(),
      install_requires=requirements,
      classifiers=["Programming Language :: Python :: 3.5",
                   "License :: OSI Approved :: MIT License",
                  ],
     )

