from setuptools import find_packages, setup

setup(
    name="mail_box",
    version="0.1.0",
    author="appinirohan",
    author_email="appinirohan@gmail.com",
    url="https://github.com/rohan2921/mail_box",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=["sqlmodel==0.0.19", "alembic==1.13.1"],
)
