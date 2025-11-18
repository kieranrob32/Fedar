import subprocess
from typing import Dict, Any, Optional

from src.handlers.common import (
    extract_base_name,
    extract_value,
    check_installed_status
)
from src.core.logger import logger


def get_package_info(package_name: str) -> Dict[str, Any]:
    logger.debug(f"Getting package info for: {package_name}")
    
    try:
        base_name = extract_base_name(package_name)
        
        result = subprocess.run(
            ['dnf', 'info', base_name],
            capture_output=True,
            text=True,
            check=False,
            timeout=10
        )
        
        if result.returncode != 0:
            logger.debug(f"DNF info failed, trying RPM info for: {base_name}")
            return _try_rpm_info(base_name)
        
        info = _parse_dnf_info(result.stdout, base_name)
        logger.debug(f"Successfully retrieved info for: {package_name}")
        return info
        
    except subprocess.TimeoutExpired:
        logger.error(f"Package info lookup timed out for: {package_name}")
        raise Exception('Package info lookup timed out')
    except Exception as e:
        if 'Package not found' in str(e):
            logger.warning(f"Package not found: {package_name}")
            raise
        logger.error(f"Failed to get package info for {package_name}: {e}")
        raise Exception(f'Failed to get package info: {str(e)}')


def _try_rpm_info(base_name: str) -> Dict[str, Any]:
    try:
        rpm_result = subprocess.run(
            ['rpm', '-qi', base_name],
            capture_output=True,
            text=True,
            check=False,
            timeout=10
        )
        
        if rpm_result.returncode == 0:
            logger.debug(f"Found package info via RPM for: {base_name}")
            return _parse_rpm_info(rpm_result.stdout, base_name)
        else:
            logger.warning(f"Package not found via RPM: {base_name}")
            raise Exception('Package not found')
            
    except subprocess.TimeoutExpired:
        logger.error(f"RPM info lookup timed out for: {base_name}")
        raise Exception('Package info lookup timed out')
    except Exception:
        raise


def _parse_dnf_info(output: str, base_name: str) -> Dict[str, Any]:
    info = {
        'name': base_name,
        'version': None,
        'release': None,
        'architecture': None,
        'size': None,
        'summary': None,
        'description': None,
        'url': None,
        'license': None,
        'repository': None,
        'installed': False
    }
    
    current_section = None
    description_lines = []
    
    for line in output.split('\n'):
        line = line.strip()
        if not line:
            if current_section == 'description':
                current_section = None
            continue
        
        if line.startswith('Name'):
            info['name'] = extract_value(line) or base_name
        elif line.startswith('Version'):
            info['version'] = extract_value(line)
        elif line.startswith('Release'):
            info['release'] = extract_value(line)
        elif line.startswith('Architecture'):
            info['architecture'] = extract_value(line)
        elif line.startswith('Size'):
            info['size'] = extract_value(line)
        elif line.startswith('Summary'):
            info['summary'] = extract_value(line)
        elif line.startswith('URL'):
            info['url'] = extract_value(line)
        elif line.startswith('License'):
            info['license'] = extract_value(line)
        elif line.startswith('From repo'):
            info['repository'] = extract_value(line)
        elif line.startswith('Description'):
            current_section = 'description'
            desc = extract_value(line) or ''
            if desc:
                description_lines.append(desc)
        elif current_section == 'description':
            description_lines.append(line)
    
    info['description'] = '\n'.join(description_lines) if description_lines else None
    info['installed'] = check_installed_status(base_name)
    
    return info


def _parse_rpm_info(output: str, package_name: str) -> Dict[str, Any]:
    info = {
        'name': package_name,
        'version': None,
        'release': None,
        'architecture': None,
        'size': None,
        'summary': None,
        'description': None,
        'url': None,
        'license': None,
        'repository': None,
        'installed': True
    }
    
    current_section = None
    description_lines = []
    
    for line in output.split('\n'):
        line = line.strip()
        if not line:
            if current_section == 'Description':
                current_section = None
            continue
        
        if line.startswith('Name'):
            info['name'] = extract_value(line) or package_name
        elif line.startswith('Version'):
            info['version'] = extract_value(line)
        elif line.startswith('Release'):
            info['release'] = extract_value(line)
        elif line.startswith('Architecture'):
            info['architecture'] = extract_value(line)
        elif line.startswith('Size'):
            info['size'] = extract_value(line)
        elif line.startswith('Summary'):
            info['summary'] = extract_value(line)
        elif line.startswith('URL'):
            info['url'] = extract_value(line)
        elif line.startswith('License'):
            info['license'] = extract_value(line)
        elif line.startswith('Description'):
            current_section = 'Description'
            desc = extract_value(line) or ''
            if desc:
                description_lines.append(desc)
        elif current_section == 'Description':
            description_lines.append(line)
    
    info['description'] = '\n'.join(description_lines) if description_lines else None
    return info
