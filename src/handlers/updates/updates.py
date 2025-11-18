import subprocess
from typing import List, Dict, Any, Tuple, Optional

from src.handlers.common import extract_base_name, get_polkit_env
from src.utils import clean_package_name
from src.core.logger import logger


def check_updates() -> List[Dict[str, Any]]:
    logger.debug("Checking for available updates")
    
    try:
        result = subprocess.run(
            ['dnf', 'check-update', '--quiet'],
            capture_output=True,
            text=True,
            check=False,
            timeout=60
        )
        
        if result.returncode == 0 and not result.stdout.strip():
            logger.info("No updates available")
            return []
        
        updates = []
        seen = set()
        
        for line in result.stdout.split('\n'):
            line = line.strip()
            if not line or line.startswith('Last metadata'):
                continue
            
            parts = line.split()
            if len(parts) < 2:
                continue
            
            name = extract_base_name(parts[0])
            if name.lower() in seen:
                continue
            seen.add(name.lower())
            
            available_version = parts[1] if len(parts) > 1 else None
            current_version, summary = _get_package_details(name)
            display_name = clean_package_name(name)
            
            updates.append({
                'name': name,
                'display_name': display_name,
                'current_version': current_version,
                'available_version': available_version,
                'summary': summary
            })
        
        logger.info(f"Found {len(updates)} available updates")
        return sorted(updates, key=lambda x: x['name'].lower())
        
    except subprocess.TimeoutExpired:
        logger.error("Update check timed out")
        raise Exception('Update check timed out')
    except Exception as e:
        logger.error(f"Failed to check updates: {e}")
        raise Exception(f'Failed to check updates: {str(e)}')


def _get_package_details(package_name: str) -> Tuple[Optional[str], Optional[str]]:
    try:
        rpm_result = subprocess.run(
            ['rpm', '-q', '--queryformat', '%{VERSION}-%{RELEASE}\t%{SUMMARY}', package_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if rpm_result.returncode == 0:
            parts = rpm_result.stdout.split('\t', 1)
            current_version = parts[0] if len(parts) > 0 else None
            summary = parts[1] if len(parts) > 1 else None
            return current_version, summary
    except Exception:
        pass
    
    return None, None


def update_system() -> Tuple[bool, str]:
    logger.info("Updating system packages")
    
    try:
        env = get_polkit_env()
        
        result = subprocess.run(
            ['pkexec', 'dnf', 'upgrade', '-y'],
            capture_output=True,
            text=True,
            timeout=600,
            env=env
        )
        
        if result.returncode == 0:
            logger.info("System update completed successfully")
            return True, result.stdout
        else:
            error_msg = result.stderr if result.stderr else result.stdout
            logger.error(f"System update failed: {error_msg}")
            return False, error_msg or 'System update failed'
            
    except subprocess.TimeoutExpired:
        logger.error("System update timed out")
        return False, 'System update timed out'
    except FileNotFoundError:
        logger.error("pkexec not found")
        return False, 'pkexec not found. Please install polkit.'
    except Exception as e:
        logger.error(f"System update error: {e}")
        return False, f'System update error: {str(e)}'
