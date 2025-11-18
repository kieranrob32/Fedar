import subprocess
from typing import List, Dict, Any

from src.utils import clean_package_name
from src.core.logger import logger


def get_installed_packages() -> List[Dict[str, Any]]:
    logger.debug("Fetching installed packages")
    
    try:
        result = subprocess.run(
            ['rpm', '-qa', '--queryformat', '%{NAME}\t%{VERSION}\t%{RELEASE}\t%{SUMMARY}\n'],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        
        packages = []
        for line in result.stdout.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            parts = line.split('\t', 3)
            if len(parts) < 2:
                continue
            
            name = parts[0]
            version = parts[1] if len(parts) > 1 else None
            release = parts[2] if len(parts) > 2 else None
            summary = parts[3] if len(parts) > 3 else None
            display_name = clean_package_name(name)
            
            packages.append({
                'name': name,
                'display_name': display_name,
                'version': version,
                'release': release,
                'summary': summary
            })
        
        logger.info(f"Found {len(packages)} installed packages")
        return sorted(packages, key=lambda x: x['name'].lower())
        
    except subprocess.TimeoutExpired:
        logger.error("Timeout while fetching installed packages")
        raise Exception('Failed to get installed packages: timeout')
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get installed packages: {e}")
        raise Exception(f'Failed to get installed packages: {str(e)}')
    except Exception as e:
        logger.error(f"Unexpected error getting installed packages: {e}")
        raise Exception(f'Failed to get installed packages: {str(e)}')
