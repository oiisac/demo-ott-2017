import setuptools


version = "1.1.0"


install_requires = [
    "redis",
    "invoke",
    "bumpversion",
    "nose"
]

setuptools.setup(
    name="demo-task-for-ott",
    version=version,
    description='Demo task for OTT',
    license="MIT",
    author="Helgi Oiisac",
    author_email="helgi@oiisac.com",
    packages=(
        "service",
    ),
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
        ],
    }
)
