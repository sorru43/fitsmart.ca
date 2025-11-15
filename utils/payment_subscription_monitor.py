#!/usr/bin/env python3
"""
Payment-Subscription Monitoring Script
Detects and alerts on payment success but subscription creation failure issues.
"""
import sys
import os
from datetime import datetime, timedelta
import logging

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database.models import db, Order, Subscription, User, MealPlan
from sqlalchemy import and_, or_

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('payment_subscription_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PaymentSubscriptionMonitor:
    """Monitor for payment-subscription mismatches"""
    
    def __init__(self):
        self.app = create_app()
        self.issues_found = []
    
    def check_payment_subscription_mismatch(self):
        """Check for orders with successful payments but no subscriptions"""
        with self.app.app_context():
            # Find orders that are confirmed but don't have associated subscriptions
            failed_orders = db.session.query(Order).filter(
                and_(
                    Order.status == 'confirmed',
                    Order.payment_status == 'captured',
                    ~Order.id.in_(
                        db.session.query(Subscription.order_id).filter(Subscription.order_id.isnot(None))
                    )
                )
            ).all()
            
            if failed_orders:
                logger.error(f"🚨 CRITICAL: Found {len(failed_orders)} orders with successful payments but NO subscriptions!")
                
                for order in failed_orders:
                    issue = {
                        'type': 'payment_success_no_subscription',
                        'order_id': order.id,
                        'user_id': order.user_id,
                        'meal_plan_id': order.meal_plan_id,
                        'amount': order.amount,
                        'payment_id': order.payment_id,
                        'razorpay_order_id': order.order_id,
                        'created_at': order.created_at,
                        'severity': 'CRITICAL'
                    }
                    self.issues_found.append(issue)
                    
                    logger.error(f"  Order {order.id}: User {order.user_id}, Amount {order.amount}, Created {order.created_at}")
                
                return failed_orders
            else:
                logger.info("✅ No payment-subscription mismatches found")
                return []
    
    def check_orphaned_subscriptions(self):
        """Check for subscriptions without corresponding orders"""
        with self.app.app_context():
            orphaned_subscriptions = db.session.query(Subscription).filter(
                and_(
                    Subscription.order_id.isnot(None),
                    ~Subscription.order_id.in_(db.session.query(Order.id))
                )
            ).all()
            
            if orphaned_subscriptions:
                logger.warning(f"⚠️ Found {len(orphaned_subscriptions)} orphaned subscriptions!")
                
                for subscription in orphaned_subscriptions:
                    issue = {
                        'type': 'orphaned_subscription',
                        'subscription_id': subscription.id,
                        'user_id': subscription.user_id,
                        'order_id': subscription.order_id,
                        'severity': 'WARNING'
                    }
                    self.issues_found.append(issue)
                    
                    logger.warning(f"  Subscription {subscription.id}: User {subscription.user_id}, Order {subscription.order_id}")
            
            return orphaned_subscriptions
    
    def check_duplicate_subscriptions(self):
        """Check for duplicate subscriptions for the same order"""
        with self.app.app_context():
            # Find orders with multiple subscriptions
            duplicate_orders = db.session.query(Subscription.order_id).filter(
                Subscription.order_id.isnot(None)
            ).group_by(Subscription.order_id).having(
                db.func.count(Subscription.id) > 1
            ).all()
            
            if duplicate_orders:
                logger.warning(f"⚠️ Found {len(duplicate_orders)} orders with duplicate subscriptions!")
                
                for (order_id,) in duplicate_orders:
                    subscriptions = Subscription.query.filter_by(order_id=order_id).all()
                    
                    issue = {
                        'type': 'duplicate_subscriptions',
                        'order_id': order_id,
                        'subscription_count': len(subscriptions),
                        'subscription_ids': [s.id for s in subscriptions],
                        'severity': 'WARNING'
                    }
                    self.issues_found.append(issue)
                    
                    logger.warning(f"  Order {order_id}: {len(subscriptions)} subscriptions")
            
            return duplicate_orders
    
    def check_recent_failures(self, hours=24):
        """Check for recent payment-subscription failures"""
        with self.app.app_context():
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            recent_failed_orders = db.session.query(Order).filter(
                and_(
                    Order.status == 'confirmed',
                    Order.payment_status == 'captured',
                    Order.created_at >= cutoff_time,
                    ~Order.id.in_(
                        db.session.query(Subscription.order_id).filter(Subscription.order_id.isnot(None))
                    )
                )
            ).all()
            
            if recent_failed_orders:
                logger.error(f"🚨 Found {len(recent_failed_orders)} recent payment-subscription failures (last {hours} hours)!")
                
                for order in recent_failed_orders:
                    issue = {
                        'type': 'recent_payment_failure',
                        'order_id': order.id,
                        'user_id': order.user_id,
                        'amount': order.amount,
                        'created_at': order.created_at,
                        'hours_ago': (datetime.now() - order.created_at).total_seconds() / 3600,
                        'severity': 'CRITICAL'
                    }
                    self.issues_found.append(issue)
                    
                    hours_ago = (datetime.now() - order.created_at).total_seconds() / 3600
                    logger.error(f"  Order {order.id}: {hours_ago:.1f} hours ago, Amount {order.amount}")
            
            return recent_failed_orders
    
    def check_webhook_failures(self, hours=24):
        """Check for potential webhook failures"""
        with self.app.app_context():
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Find orders that might have webhook issues
            webhook_suspicious_orders = db.session.query(Order).filter(
                and_(
                    Order.status == 'confirmed',
                    Order.payment_status == 'captured',
                    Order.created_at >= cutoff_time,
                    ~Order.id.in_(
                        db.session.query(Subscription.order_id).filter(Subscription.order_id.isnot(None))
                    )
                )
            ).all()
            
            if webhook_suspicious_orders:
                logger.warning(f"⚠️ Found {len(webhook_suspicious_orders)} orders that might have webhook issues!")
                
                for order in webhook_suspicious_orders:
                    issue = {
                        'type': 'potential_webhook_failure',
                        'order_id': order.id,
                        'user_id': order.user_id,
                        'razorpay_order_id': order.order_id,
                        'created_at': order.created_at,
                        'severity': 'WARNING'
                    }
                    self.issues_found.append(issue)
            
            return webhook_suspicious_orders
    
    def generate_report(self):
        """Generate a comprehensive report of all issues"""
        logger.info("🔍 Starting Payment-Subscription Monitor...")
        
        # Run all checks
        self.check_payment_subscription_mismatch()
        self.check_orphaned_subscriptions()
        self.check_duplicate_subscriptions()
        self.check_recent_failures()
        self.check_webhook_failures()
        
        # Generate summary
        if self.issues_found:
            logger.error(f"🚨 MONITORING REPORT: Found {len(self.issues_found)} issues!")
            
            critical_issues = [i for i in self.issues_found if i['severity'] == 'CRITICAL']
            warning_issues = [i for i in self.issues_found if i['severity'] == 'WARNING']
            
            logger.error(f"  CRITICAL: {len(critical_issues)}")
            logger.error(f"  WARNING: {len(warning_issues)}")
            
            # Group by type
            issue_types = {}
            for issue in self.issues_found:
                issue_type = issue['type']
                if issue_type not in issue_types:
                    issue_types[issue_type] = []
                issue_types[issue_type].append(issue)
            
            for issue_type, issues in issue_types.items():
                logger.error(f"  {issue_type}: {len(issues)} issues")
            
            return {
                'total_issues': len(self.issues_found),
                'critical_issues': len(critical_issues),
                'warning_issues': len(warning_issues),
                'issues_by_type': issue_types,
                'all_issues': self.issues_found
            }
        else:
            logger.info("✅ All systems operational - no issues found!")
            return {
                'total_issues': 0,
                'critical_issues': 0,
                'warning_issues': 0,
                'issues_by_type': {},
                'all_issues': []
            }
    
    def send_alert(self, report):
        """Send alert for critical issues"""
        if report['critical_issues'] > 0:
            logger.error("🚨 SENDING CRITICAL ALERT!")
            # Here you would integrate with your alerting system
            # (email, Slack, PagerDuty, etc.)
            
            alert_message = f"""
🚨 CRITICAL PAYMENT-SUBSCRIPTION ISSUES DETECTED!

Total Issues: {report['total_issues']}
Critical Issues: {report['critical_issues']}
Warning Issues: {report['warning_issues']}

Issue Breakdown:
"""
            
            for issue_type, issues in report['issues_by_type'].items():
                alert_message += f"- {issue_type}: {len(issues)} issues\n"
            
            logger.error(alert_message)
            
            # You can add email/Slack integration here
            # send_email_alert(alert_message)
            # send_slack_alert(alert_message)

def main():
    """Main monitoring function"""
    monitor = PaymentSubscriptionMonitor()
    report = monitor.generate_report()
    monitor.send_alert(report)
    return report

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Payment-Subscription Monitor")
    parser.add_argument("--check", action="store_true", help="Run all checks")
    parser.add_argument("--recent", type=int, default=24, help="Check recent failures (hours)")
    parser.add_argument("--alert", action="store_true", help="Send alerts for critical issues")
    
    args = parser.parse_args()
    
    if args.check:
        monitor = PaymentSubscriptionMonitor()
        report = monitor.generate_report()
        
        if args.alert:
            monitor.send_alert(report)
    else:
        print("Usage: python payment_subscription_monitor.py --check [--alert]")
        print("Example: python payment_subscription_monitor.py --check --alert")
