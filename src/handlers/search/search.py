import subprocess
from typing import List, Dict, Any

from src.handlers.common import (
    is_metadata_line,
    parse_package_line,
    create_package_dict
)
from src.core.logger import logger


def search_packages(query: str) -> List[Dict[str, Any]]:
    logger.debug(f"Searching packages with query: {query}")
    
    try:
        result = subprocess.run(
            ['dnf', 'search', '--quiet', query],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        
        packages = []
        seen = set()
        
        for line in result.stdout.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if is_metadata_line(line):
                continue
            
            if ':' in line:
                name, summary = parse_package_line(line)
                if not name or name.lower() in seen:
                    continue
                seen.add(name.lower())
                pkg = create_package_dict(name, summary)
                if pkg:
                    packages.append(pkg)
            else:
                if line.lower() in seen:
                    continue
                seen.add(line.lower())
                pkg = create_package_dict(line, None)
                if pkg:
                    packages.append(pkg)
        
        logger.info(f"Found {len(packages)} packages for query: {query}")
        return packages
        
    except subprocess.TimeoutExpired:
        logger.error(f"DNF search timed out for query: {query}")
        raise Exception('DNF search timed out')
    except subprocess.CalledProcessError as e:
        logger.error(f"DNF search failed for query: {query}, error: {e}")
        raise Exception('DNF search failed')
    except Exception as e:
        logger.error(f"Unexpected error during package search: {e}")
        raise Exception(f'Failed to search packages: {str(e)}')
