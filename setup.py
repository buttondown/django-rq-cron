from setuptools import find_packages, setup
import os

# Read the long description from README.md
with open(os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="django-rq-cron",
    version="0.1.1",
    description="A Django app for running cron jobs with django-rq",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Buttondown",
    author_email="hello@buttondown.email",
    url="https://github.com/buttondown/django-rq-cron",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Django>=3.2",
        "django-rq>=2.5.0",
        "python-crontab>=2.6.0",
    ],
)
