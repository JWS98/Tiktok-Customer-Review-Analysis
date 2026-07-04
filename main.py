#!/usr/bin/env python
"""
Main runner script - Orchestrates the entire pipeline
Runs all 4 steps: scrape -> clean -> analyze -> report
"""

import sys
import subprocess
from utils.logger import setup_logger
from config import get_config_summary

logger = setup_logger(__name__)

def run_pipeline():
    """
    Run the complete review analysis pipeline
    
    Returns:
        True if all steps succeed, False otherwise
    """
    logger.info("\n" + "#"*80)
    logger.info("# TIKTOK REVIEW ANALYSIS PIPELINE")
    logger.info("#"*80)
    
    # Print configuration
    config = get_config_summary()
    logger.info("\nConfiguration:")
    for key, value in config.items():
        logger.info(f"  {key}: {value}")
    
    steps = [
        ("scripts/01_scrape_reviews.py", "Scraping Reviews"),
        ("scripts/02_clean_data.py", "Cleaning Data"),
        ("scripts/03_analyze_reviews.py", "Analyzing Reviews"),
        ("scripts/04_generate_report.py", "Generating Report"),
    ]
    
    logger.info("\n" + "="*80)
    logger.info("STARTING PIPELINE EXECUTION")
    logger.info("="*80)
    
    for script, step_name in steps:
        logger.info(f"\n>>> Step: {step_name}")
        logger.info(f"    Script: {script}")
        logger.info("-"*80)
        
        try:
            result = subprocess.run([sys.executable, script], check=False)
            
            if result.returncode != 0:
                logger.error(f"\n✗ {step_name} failed!")
                return False
            
            logger.info(f"✓ {step_name} completed successfully\n")
        
        except Exception as e:
            logger.error(f"Error running {script}: {str(e)}")
            return False
    
    return True

def print_completion_message():
    """
    Print completion message with next steps
    """
    logger.info("\n" + "#"*80)
    logger.info("# PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
    logger.info("#"*80)
    logger.info("\n✓ All steps completed successfully!")
    logger.info("\nGenerated Files:")
    logger.info("  • data/raw/ - Raw scraped reviews (JSON)")
    logger.info("  • data/processed/ - Cleaned and analyzed reviews (CSV + JSON)")
    logger.info("  • output/review.html - Interactive HTML report")
    logger.info("  • logs/app.log - Detailed execution logs")
    logger.info("\nNext Steps:")
    logger.info("  1. Open 'output/review.html' in your web browser")
    logger.info("  2. Review the analysis and insights")
    logger.info("  3. Export cleaned data for further analysis if needed")
    logger.info("\nTo run the pipeline again, simply execute:")
    logger.info("  python main.py\n")

if __name__ == "__main__":
    try:
        if run_pipeline():
            print_completion_message()
            sys.exit(0)
        else:
            logger.error("\n" + "#"*80)
            logger.error("# PIPELINE FAILED")
            logger.error("#"*80)
            logger.error("\nPlease check the logs above for details.")
            logger.error(f"Full logs available in: logs/app.log\n")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.warning("\n\nPipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
