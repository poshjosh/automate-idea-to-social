#!/usr/bin/env python

from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(name="automate-idea-to-social",
          version="0.3.1",
          description="Automate generating and publishing content from ideas to social media.",
          author="PoshJosh",
          author_email="posh.bc@gmail.com",
          install_requires=["flask", "flask-cors",
                            "ruamel.yaml", "selenium", "requests",
                            "webvtt-py", "undetected-chromedriver",
                            "pyu"],
          license="MIT",
          classifiers=[
              "Programming Language :: Python :: 3",
              "License :: OSI Approved :: MIT License",
              "Operating System :: OS Independent",
          ],
          url="https://github.com/poshjosh/automate-idea-to-social",
          packages=find_packages(
              where='src',
              include=['aideas', 'aideas.*'],
              exclude=['test', 'test.*']
          ),
          package_dir={"": "src"},
          )
