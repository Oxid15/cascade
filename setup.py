import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cascade",
    version='0.2.1',
    author='Ilia Moiseev',
    author_email='ilia.moiseev.5@yandex.ru',
    description="Small ML-Engineering framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oxid15/cascade",
    project_urls={
        "Documentation": "https://oxid15.github.io/cascade",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache License 2.0",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    python_requires=">=3.6",
    install_requires=[
        'tqdm',
        'numpy',
        'pandas',
        'deepdiff',
        'pendulum',
        'plotly'
    ]
)
