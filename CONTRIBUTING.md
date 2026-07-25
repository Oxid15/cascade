# Contributing
Pull requests and issues are welcome! For major changes, please open an issue first to discuss what you would like to change.
  
Please make sure to update tests and docs as appropriate.

## Developer setup

### Repo

```bash
git clone https://github.com/Oxid15/cascade.git
```

### Installation

Use Python one version behind the latest as recommended.
Remember to create a venv!

``` bash
python -m venv ./venv
source ./venv/bin/activate
```

```bash
cd cascade
pip install -e .
```

### Testing

Install requirements

```bash
pip install -r cascade/tests/requirements.txt
```

Run all tests

```bash
cd cascade/tests
pytest
```

### Documentation

Install requirements

```bash
pip install -r cascade/docs/requirements.txt
```

You may also need to install `pandoc`
https://pandoc.org/installing.html

Build the docs

```bash
cd cascade/docs
sphinx-build source build
```

Format of docstrings is `numpy`.

### Code

Cascade uses `ruff`. Be sure that `ruff check .` passes before pushing the code.

Each file should have license notice in the header - be sure it is included.

### Release Checklist

Use this checklist before every new release

- [ ] Code quality
	- [ ] Version is bumped
	- [ ] Tests are passing on every supported system
	- [ ] Linters passing
- [ ] Documentation
	- [ ] Builds without warnings
	- [ ] License is up to date
	- [ ] cascade/docs/source/_static/switcher.json is up to date
    - [ ] README is relevant
- [ ] Changelog
