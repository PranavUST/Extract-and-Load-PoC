from src.schema_generator import CSVSchemaGenerator

def test_infer_column_type():
    gen = CSVSchemaGenerator()
    assert gen.infer_column_type(['1', '2', '3']) == 'INTEGER'
    assert gen.infer_column_type(['1.1', '2.2']) == 'REAL'
    assert gen.infer_column_type(['true', 'false']) == 'BOOLEAN'
    assert gen.infer_column_type(['2023-01-01']) == 'TIMESTAMP'
