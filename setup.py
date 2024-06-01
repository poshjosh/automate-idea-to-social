#!/usr/bin/env python

from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(name="automate-idea-to-social",
          version="0.0.7",
          description="Automate generating and publishing content from ideas to social media.",
          author="PyU Team",
          author_email="posh.bc@gmail.com",
          install_requires=["ruamel.yaml", "selenium", "requests",
                            "webvtt-py", "undetected-chromedriver"],
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
