import tempfile
import yaml
import os
import pytest
from src.config_loader import load_config, resolve_config_vars, _validate_ftp_config, _validate_api_config

def test_load_and_resolve_config():
    config_dict = {
        'source': {'type': 'REST_API', 'api': {'url': 'http://test', 'method': 'GET'}},
        'destination': {},
        'secrets': [],
        'key': '{{TEST_ENV}}'
    }
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        yaml.dump(config_dict, f)
        fname = f.name
    os.environ['TEST_ENV'] = 'value'
    config = load_config(fname)
    resolved = resolve_config_vars(config)
    assert resolved['key'] == 'value'
    os.remove(fname)

def test_load_config_missing_file():
    with pytest.raises(FileNotFoundError):
        load_config('nonexistent.yaml')

def test_load_config_missing_section(tmp_path):
    config_dict = {'secrets': []}
    file_path = tmp_path / "config.yaml"
    with open(file_path, 'w') as f:
        yaml.dump(config_dict, f)
    with pytest.raises(ValueError):
        load_config(str(file_path))

def test_load_config_missing_secret(tmp_path):
    config_dict = {
        'source': {'type': 'REST_API', 'api': {'url': 'http://test', 'method': 'GET'}},
        'destination': {},
        'secrets': ['MISSING_ENV']
    }
    file_path = tmp_path / "config.yaml"
    with open(file_path, 'w') as f:
        yaml.dump(config_dict, f)
    if 'MISSING_ENV' in os.environ:
        del os.environ['MISSING_ENV']
    with pytest.raises(EnvironmentError):
        load_config(str(file_path))

def test_resolve_config_vars_partial_and_full():
    os.environ['FOO'] = 'bar'
    config = {'a': '{{FOO}}', 'b': 'literal', 'c': {'d': '{{FOO}}'}, 'e': [{'f': '{{FOO}}'}, 'g']}
    resolved = resolve_config_vars(config)
    assert resolved['a'] == 'bar'
    assert resolved['b'] == 'literal'
    assert resolved['c']['d'] == 'bar'
    assert resolved['e'][0]['f'] == 'bar'
    assert resolved['e'][1] == 'g'

def test_resolve_config_vars_missing_env():
    config = {'a': '{{MISSING}}'}
    if 'MISSING' in os.environ:
        del os.environ['MISSING']
    with pytest.raises(EnvironmentError):
        resolve_config_vars(config)

def test_validate_ftp_config_success():
    ftp_config = {
        'host': 'h', 'username': 'u', 'password': 'p', 'remote_dir': 'r', 'local_dir': 'l'
    }
    _validate_ftp_config(ftp_config)  # Should not raise

def test_validate_ftp_config_missing_field():
    ftp_config = {
        'host': 'h', 'username': 'u', 'password': 'p', 'remote_dir': 'r'
    }
    with pytest.raises(ValueError):
        _validate_ftp_config(ftp_config)

def test_validate_ftp_config_empty_field():
    ftp_config = {
        'host': 'h', 'username': '', 'password': 'p', 'remote_dir': 'r', 'local_dir': 'l'
    }
    with pytest.raises(ValueError):
        _validate_ftp_config(ftp_config)

def test_validate_api_config_success():
    api_config = {'url': 'http://test', 'method': 'GET'}
    _validate_api_config(api_config)  # Should not raise

def test_validate_api_config_missing_field():
    api_config = {'url': 'http://test'}
    with pytest.raises(ValueError):
        _validate_api_config(api_config)

def test_load_config_invalid_yaml(tmp_path):
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text("not: [valid: yaml")
    with pytest.raises(Exception):
        load_config(str(bad_yaml))

def test_load_config_malformed_yaml(tmp_path):
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text("not: [valid: yaml")
    with pytest.raises(Exception):
        load_config(str(bad_yaml))

def test_load_config_secret_debug(tmp_path, monkeypatch):
    import logging
    from src.config_loader import load_config
    config_dict = {
        'source': {'type': 'REST_API', 'api': {'url': 'http://test', 'method': 'GET'}},
        'destination': {},
        'secrets': ['TEST_SECRET']
    }
    file_path = tmp_path / "config.yaml"
    with open(file_path, 'w') as f:
        yaml.dump(config_dict, f)
    monkeypatch.setenv('TEST_SECRET', 'foo')
    logging.getLogger('src.config_loader').setLevel(logging.DEBUG)
    load_config(str(file_path))

def test_load_config_valid_ftp(tmp_path):
    from src.config_loader import load_config
    config_dict = {
        'source': {
            'type': 'FTP',
            'ftp': {
                'host': 'h', 'username': 'u', 'password': 'p', 'remote_dir': 'r', 'local_dir': 'l'
            }
        },
        'destination': {},
        'secrets': []
    }
    file_path = tmp_path / "ftp_config.yaml"
    with open(file_path, 'w') as f:
        yaml.dump(config_dict, f)
    load_config(str(file_path))

def test_resolve_config_vars_literal():
    from src.config_loader import resolve_config_vars
    config = {'foo': 'bar'}
    resolved = resolve_config_vars(config)
    assert resolved['foo'] == 'bar'

def test_resolve_config_vars_non_template_string():
    from src.config_loader import resolve_config_vars
    config = {'plain': 'not_a_template'}
    resolved = resolve_config_vars(config)
    assert resolved['plain'] == 'not_a_template'