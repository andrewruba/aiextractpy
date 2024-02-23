from src.aiextractpy.data_extractor import DataExtractor

def test_init():
    extractor = DataExtractor()
    assert isinstance(extractor, DataExtractor)
