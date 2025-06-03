import tempfile
import yaml
from src.config_loader import load_config, resolve_config_vars

def test_load_and_resolve_config():
    config_dict = {'secrets': [], 'key': '{{TEST_ENV}}'}
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        yaml.dump(config_dict, f)
        fname = f.name
    # Set environment variable for testing
    import os
    os.environ['TEST_ENV'] = 'value'
    config = load_config(fname)
    resolved = resolve_config_vars(config)
    assert resolved['key'] == 'value'
