import setuptools


version = "0.0.0"


install_requires = [
    "redis",
    "invoke",
    "bumpversion"
]

setuptools.setup(
    name="demo-task-for-ott",
    version=version,
    description='Demo task for OTT',
    license="MIT",
    author="Helgi Oiisac",
    author_email="helgi@oiisac.com",
    packages=(
        "app",
    ),
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
        ],
    }
)
