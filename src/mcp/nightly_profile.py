"""Nightly profiling job for continuous optimization monitoring.

Runs automated profiling analysis and generates optimization reports.
Designed to be run as cron job or scheduled task.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Setup logging for cron execution
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/nightly_profiling.log'),
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger(__name__)


def nightly_profiling_job():
    """Run nightly profiling and analysis."""
    
    logger.info("="*60)
    logger.info("Nightly Profiling Job - Starting")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("="*60)
    
    try:
        from src.mcp import ProfilingAnalyzer
        
        # Step 1: Analyze existing profiling data
        logger.info("Step 1: Analyzing profiling traces...")
        findings = ProfilingAnalyzer.analyze_trace("logs/profiling")
        
        logger.info(f"Found {findings['metrics']['num_bottlenecks']} bottlenecks")
        logger.info(f"Optimization potential: {findings['metrics']['optimization_potential']:.0f}%")
        
        # Step 2: Generate recommendations
        logger.info("\nStep 2: Generating optimization recommendations...")
        
        if findings["recommendations"]:
            logger.info(f"Generated {len(findings['recommendations'])} recommendations:")
            for i, rec in enumerate(findings["recommendations"], 1):
                logger.info(f"  {i}. [{rec['priority']}] {rec['action']}")
                logger.info(f"     Expected speedup: {rec['expected_speedup']}")
        else:
            logger.info("No optimization opportunities identified")
        
        # Step 3: Save report
        logger.info("\nStep 3: Saving nightly report...")
        report_dir = Path("logs/nightly_reports")
        report_dir.mkdir(exist_ok=True)
        
        report_file = report_dir / f"profiling_report_{datetime.now().strftime('%Y%m%d')}.json"
        
        import json
        with open(report_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "findings": findings,
                "summary": {
                    "bottlenecks": len(findings["bottlenecks"]),
                    "recommendations": len(findings["recommendations"]),
                    "optimization_potential": findings["metrics"]["optimization_potential"],
                }
            }, f, indent=2)
        
        logger.info(f"Report saved to: {report_file}")
        
        # Step 4: Check if action needed
        logger.info("\nStep 4: Determining required actions...")
        
        high_priority_recs = [
            r for r in findings["recommendations"] 
            if r["priority"] == "HIGH"
        ]
        
        if high_priority_recs:
            logger.warning(f"⚠️ {len(high_priority_recs)} HIGH priority optimizations available!")
            logger.warning("Recommend reviewing and applying optimizations.")
        else:
            logger.info("✅ No urgent optimizations needed")
        
        # Step 5: Send summary (email/slack in production)
        logger.info("\nStep 5: Notification summary...")
        logger.info(f"  Bottlenecks: {len(findings['bottlenecks'])}")
        logger.info(f"  High priority: {len(high_priority_recs)}")
        logger.info(f"  Potential speedup: {findings['metrics']['optimization_potential']:.0f}%")
        
        logger.info("\n" + "="*60)
        logger.info("Nightly Profiling Job - Completed Successfully")
        logger.info("="*60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Nightly profiling job failed: {e}", exc_info=True)
        logger.error("="*60)
        return 1


if __name__ == "__main__":
    exit_code = nightly_profiling_job()
    sys.exit(exit_code)

