"""
Memory Monitoring Utilities
Provides memory usage tracking and cleanup functions.
"""

import gc
import logging
import psutil
import os
from typing import Dict

logger = logging.getLogger(__name__)


def get_memory_usage() -> Dict[str, float]:
    """
    Get current memory usage statistics.
    
    Returns:
        Dictionary with memory metrics in MB
    """
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    
    return {
        "rss_mb": mem_info.rss / 1024 / 1024,  # Resident Set Size
        "vms_mb": mem_info.vms / 1024 / 1024,  # Virtual Memory Size
        "percent": process.memory_percent(),
        "available_mb": psutil.virtual_memory().available / 1024 / 1024
    }


def log_memory_usage(context: str = ""):
    """Log current memory usage with optional context."""
    usage = get_memory_usage()
    logger.info(
        f"Memory [{context}]: RSS={usage['rss_mb']:.1f}MB, "
        f"VMS={usage['vms_mb']:.1f}MB, "
        f"Usage={usage['percent']:.1f}%, "
        f"Available={usage['available_mb']:.1f}MB"
    )
    return usage


def cleanup_memory():
    """
    Force garbage collection to free memory.
    Call periodically or after heavy operations.
    """
    logger.info("Running garbage collection...")
    before = get_memory_usage()
    
    # Force full garbage collection
    collected = gc.collect()
    
    after = get_memory_usage()
    freed_mb = before['rss_mb'] - after['rss_mb']
    
    logger.info(
        f"GC collected {collected} objects, "
        f"freed {freed_mb:.1f}MB"
    )
    
    return freed_mb


def check_memory_limit(max_mb: int = 512, cleanup_threshold: float = 0.8):
    """
    Check if memory usage is approaching limit and cleanup if needed.
    
    Args:
        max_mb: Maximum memory in MB (Render free tier is 512MB)
        cleanup_threshold: Percentage (0-1) at which to trigger cleanup
        
    Returns:
        True if under limit, False if exceeded
    """
    usage = get_memory_usage()
    current_mb = usage['rss_mb']
    threshold_mb = max_mb * cleanup_threshold
    
    if current_mb > threshold_mb:
        logger.warning(
            f"Memory usage ({current_mb:.1f}MB) exceeds threshold "
            f"({threshold_mb:.1f}MB). Running cleanup..."
        )
        cleanup_memory()
        
        # Check again after cleanup
        new_usage = get_memory_usage()
        if new_usage['rss_mb'] > max_mb:
            logger.error(
                f"Memory limit exceeded: {new_usage['rss_mb']:.1f}MB > {max_mb}MB"
            )
            return False
    
    return True


if __name__ == "__main__":
    # Test memory monitoring
    logging.basicConfig(level=logging.INFO)
    
    print("Current memory usage:")
    usage = log_memory_usage("test")
    
    print("\nRunning cleanup:")
    freed = cleanup_memory()
    
    print("\nChecking limits:")
    check_memory_limit(max_mb=512)
