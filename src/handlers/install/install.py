import subprocess
from typing import Tuple

from src.handlers.common import extract_base_name, get_polkit_env
from src.core.logger import logger


def install_package(package_name: str) -> Tuple[bool, str]:
    logger.info(f"Installing package: {package_name}")
    
    try:
        base_name = extract_base_name(package_name)
        env = get_polkit_env()
        
        result = subprocess.run(
            ['pkexec', 'dnf', 'install', '-y', base_name],
            capture_output=True,
            text=True,
            timeout=300,
            env=env
        )
        
        if result.returncode == 0:
            logger.info(f"Successfully installed: {package_name}")
            return True, result.stdout
        else:
            error_msg = result.stderr if result.stderr else result.stdout
            logger.error(f"Installation failed for {package_name}: {error_msg}")
            return False, error_msg or 'Installation failed'
            
    except subprocess.TimeoutExpired:
        logger.error(f"Installation timed out for: {package_name}")
        return False, 'Installation timed out'
    except FileNotFoundError:
        logger.error("pkexec not found")
        return False, 'pkexec not found. Please install polkit.'
    except Exception as e:
        logger.error(f"Installation error for {package_name}: {e}")
        return False, f'Installation error: {str(e)}'


def uninstall_package(package_name: str) -> Tuple[bool, str]:
    logger.info(f"Uninstalling package: {package_name}")
    
    try:
        base_name = extract_base_name(package_name)
        env = get_polkit_env()
        
        result = subprocess.run(
            ['pkexec', 'dnf', 'remove', '-y', base_name],
            capture_output=True,
            text=True,
            timeout=300,
            env=env
        )
        
        if result.returncode == 0:
            logger.info(f"Successfully uninstalled: {package_name}")
            return True, result.stdout
        else:
            error_msg = result.stderr if result.stderr else result.stdout
            logger.error(f"Uninstallation failed for {package_name}: {error_msg}")
            return False, error_msg or 'Uninstallation failed'
            
    except subprocess.TimeoutExpired:
        logger.error(f"Uninstallation timed out for: {package_name}")
        return False, 'Uninstallation timed out'
    except FileNotFoundError:
        logger.error("pkexec not found")
        return False, 'pkexec not found. Please install polkit.'
    except Exception as e:
        logger.error(f"Uninstallation error for {package_name}: {e}")
        return False, f'Uninstallation error: {str(e)}'
