import src.aiextractpy

def test_version():
    assert hasattr(src.aiextractpy, "__version__"), "Package should have a '__version__' attribute"
    assert isinstance(src.aiextractpy.__version__, str), "Version should be a string"
    assert len(src.aiextractpy.__version__) > 0, "Version string should not be empty"
