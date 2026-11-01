import sonofile


def test_package_exposes_version() -> None:
    assert isinstance(sonofile.__version__, str)
    assert sonofile.__version__
