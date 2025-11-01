import yaml
import os

def get_project_root() -> str:
    """Returns an absolute path to the project root."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

def load_config(config_path: str = "config.yaml") -> dict:
    """Loads and returns config.yaml file as dictionary."""
    project_root = get_project_root()
    full_path = os.path.join(project_root, config_path)
    
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Config file not found: {full_path}")
    
    with open(full_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    
    return config