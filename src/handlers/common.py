import os
import subprocess
from typing import Dict, Optional, Tuple, Any

from src.utils import clean_package_name
from src.core.logger import logger


def extract_base_name(package_name: str) -> str:
    return package_name.split('.')[0] if '.' in package_name else package_name


def is_metadata_line(line: str) -> bool:
    metadata_patterns = [
        'matched:', 'matched fields', 'name (', 'summary (', 'description ('
    ]
    return any(line.lower().startswith(pattern) for pattern in metadata_patterns)


def parse_package_line(line: str) -> Tuple[str, Optional[str]]:
    colon_pos = line.find(':')
    if colon_pos == -1:
        return line.strip(), None
    
    name = line[:colon_pos].strip()
    summary = line[colon_pos + 1:].strip() or None
    base_name = extract_base_name(name)
    return base_name, summary


def create_package_dict(name: str, summary: Optional[str]) -> Optional[Dict[str, Any]]:
    base_name = extract_base_name(name)
    display_name = clean_package_name(name)
    
    if not base_name or not display_name:
        return None
    
    return {
        'name': base_name,
        'display_name': display_name,
        'summary': summary,
        'version': None,
        'installed': False
    }


def extract_value(line: str) -> Optional[str]:
    if ':' in line:
        return line.split(':', 1)[1].strip()
    return None


def check_installed_status(package_name: str) -> bool:
    try:
        result = subprocess.run(
            ['rpm', '-q', package_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception as e:
        logger.debug(f"Could not check installed status for {package_name}: {e}")
        return False


def get_polkit_env() -> Dict[str, str]:
    env = os.environ.copy()
    if 'DISPLAY' not in env:
        env['DISPLAY'] = ''
    if 'XAUTHORITY' not in env:
        env['XAUTHORITY'] = ''
    return env
