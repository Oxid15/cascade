import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cascade",
    version='0.2.1',
    author='Ilia Moiseev',
    author_email='ilia.moiseev.5@yandex.ru',
    license='Apache License 2.0',
    description="Small ML-Engineering framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oxid15/cascade",
    project_urls={
        "Documentation": "https://oxid15.github.io/cascade",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Apache License 2.0",
        "Operating System :: OS Independent",
        'Topic :: Software Development :: Libraries :: Python Modules'
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research'
    ],
    package_dir={"cascade": "./cascade"}, # , 'cascade_utils': './cascade/utils'
    packages=['cascade'], # , 'cascade_utils'
    python_requires=">=3.8",
    install_requires=[
        'tqdm',
        'numpy',
        'pandas',
        'deepdiff',
        'pendulum',
        'plotly'
    ]
)
