"""
Gmail Add-on Demonstration
Shows how to use the modular email threat detection system with multiple user profiles.
"""

from gmail_addon_integration import GmailAddonIntegration


def print_separator(char='=', length=80):
    """Print a separator line."""
    print(char * length)


def display_analysis_result(result: dict):
    """Display email analysis result in a formatted way."""
    print(f"\n📧 Email Analysis Result:")
    print(f"   Sender: {result.get('sender', 'N/A')}")
    print(f"   Subject: {result.get('subject', 'N/A')}")
    print(f"   Threat Score: {result.get('threat_score', 0):.2%}")
    print(f"   Threat Type: {result.get('threat_type', 'N/A')}")
    print(f"   Confidence: {result.get('confidence', 'N/A')}")
    
    if result.get('is_threat'):
        print(f"   ⚠️  STATUS: THREAT DETECTED!")
    else:
        print(f"   ✓ STATUS: Appears Legitimate")
    
    if result.get('risk_factors'):
        print(f"\n   Risk Factors:")
        for factor in result['risk_factors']:
            print(f"      • {factor}")
    
    if result.get('recommendations'):
        print(f"\n   Recommendations:")
        for rec in result['recommendations'][:3]:  # Show top 3
            print(f"      {rec}")


def demo_basic_usage():
    """Demonstrate basic usage of the Gmail add-on."""
    print("\n" + "="*80)
    print("GMAIL ADD-ON DEMO - Basic Usage")
    print("="*80)
    
    # Initialize the integration
    addon = GmailAddonIntegration()
    
    # Setup user profiles
    print("\n1. Setting up user profiles...")
    print_separator('-')
    
    addon.setup_user_profile(
        username='alice',
        email='alice@example.com',
        threat_threshold=0.6,
        auto_flag=True
    )
    
    addon.setup_user_profile(
        username='bob',
        email='bob@example.com',
        threat_threshold=0.7,
        auto_flag=True
    )
    
    # Add sample emails
    print("\n2. Adding sample emails to inboxes...")
    print_separator('-')
    
    addon.add_sample_emails('alice', count=15, phishing_ratio=0.3)
    addon.add_sample_emails('bob', count=10, phishing_ratio=0.4)
    
    # Scan inboxes
    print("\n3. Scanning Alice's inbox...")
    print_separator('-')
    
    alice_scan = addon.scan_inbox('alice')
    print(f"\n📊 Alice's Scan Results:")
    print(f"   Total Emails Scanned: {alice_scan['total_scanned']}")
    print(f"   Threats Found: {alice_scan['threats_found']}")
    print(f"   Threat Rate: {alice_scan['threat_rate']:.1%}")
    
    # Show first few results
    print(f"\n   Sample Results (first 3):")
    for i, result in enumerate(alice_scan['results'][:3], 1):
        print(f"\n   Email {i}:")
        print(f"      Subject: {result['subject']}")
        print(f"      Sender: {result['sender']}")
        print(f"      Threat Score: {result['threat_score']:.2%}")
        print(f"      Status: {'⚠️ THREAT' if result['is_threat'] else '✓ Safe'}")
    
    print("\n4. Scanning Bob's inbox...")
    print_separator('-')
    
    bob_scan = addon.scan_inbox('bob')
    print(f"\n📊 Bob's Scan Results:")
    print(f"   Total Emails Scanned: {bob_scan['total_scanned']}")
    print(f"   Threats Found: {bob_scan['threats_found']}")
    print(f"   Threat Rate: {bob_scan['threat_rate']:.1%}")
    
    # Show dashboard
    print("\n5. User Dashboards...")
    print_separator('-')
    
    alice_dashboard = addon.get_user_dashboard('alice')
    print(f"\n📊 Alice's Dashboard:")
    print(f"   Email: {alice_dashboard['email']}")
    print(f"   Add-on Enabled: {alice_dashboard['addon_enabled']}")
    print(f"   Threat Threshold: {alice_dashboard['threat_threshold']:.1%}")
    print(f"   Inbox Count: {alice_dashboard['inbox_count']}")
    print(f"   Flagged Count: {alice_dashboard['flagged_count']}")
    print(f"   Total Scanned: {alice_dashboard['statistics']['total_emails_scanned']}")
    print(f"   Threats Detected: {alice_dashboard['statistics']['threats_detected']}")
    
    bob_dashboard = addon.get_user_dashboard('bob')
    print(f"\n📊 Bob's Dashboard:")
    print(f"   Email: {bob_dashboard['email']}")
    print(f"   Add-on Enabled: {bob_dashboard['addon_enabled']}")
    print(f"   Threat Threshold: {bob_dashboard['threat_threshold']:.1%}")
    print(f"   Inbox Count: {bob_dashboard['inbox_count']}")
    print(f"   Flagged Count: {bob_dashboard['flagged_count']}")
    print(f"   Total Scanned: {bob_dashboard['statistics']['total_emails_scanned']}")
    print(f"   Threats Detected: {bob_dashboard['statistics']['threats_detected']}")


def demo_single_email_analysis():
    """Demonstrate analyzing a single email."""
    print("\n" + "="*80)
    print("GMAIL ADD-ON DEMO - Single Email Analysis")
    print("="*80)
    
    addon = GmailAddonIntegration()
    
    # Ensure profile exists
    addon.setup_user_profile('charlie', 'charlie@example.com')
    
    # Test with a phishing email
    print("\n1. Analyzing a PHISHING email...")
    print_separator('-')
    
    phishing_email = {
        'sender': 'security@paypa1-verify.com',
        'sender_name': 'PayPal Security',
        'subject': 'URGENT: Your Account Has Been Suspended!',
        'body': '''
        Your PayPal account has been suspended due to suspicious activity. 
        You must verify your identity immediately by clicking the link below.
        
        VERIFY NOW: http://paypal-verify-2026.tk/login
        
        You have only 24 hours before permanent suspension!
        
        Act now or lose access forever!
        ''',
        'urls': ['http://paypal-verify-2026.tk/login']
    }
    
    result = addon.analyze_single_email('charlie', phishing_email)
    display_analysis_result({**phishing_email, **result})
    
    # Test with a legitimate email
    print("\n\n2. Analyzing a LEGITIMATE email...")
    print_separator('-')
    
    legitimate_email = {
        'sender': 'newsletter@company.com',
        'sender_name': 'Company Newsletter',
        'subject': 'Weekly Newsletter - January 2026',
        'body': '''
        Hello,
        
        Here is your weekly newsletter with the latest updates and articles.
        
        This week's highlights:
        - New product features
        - Customer success stories
        - Upcoming events
        
        Visit our blog: https://company.com/blog
        
        Best regards,
        The Company Team
        ''',
        'urls': ['https://company.com/blog']
    }
    
    result = addon.analyze_single_email('charlie', legitimate_email)
    display_analysis_result({**legitimate_email, **result})


def demo_whitelist_blacklist():
    """Demonstrate whitelist/blacklist functionality."""
    print("\n" + "="*80)
    print("GMAIL ADD-ON DEMO - Whitelist/Blacklist Management")
    print("="*80)
    
    addon = GmailAddonIntegration()
    
    # Setup profile
    addon.setup_user_profile('david', 'david@example.com')
    
    print("\n1. Adding senders to whitelist and blacklist...")
    print_separator('-')
    
    addon.add_to_whitelist('david', 'trusted@company.com')
    addon.add_to_whitelist('david', 'newsletter@news.com')
    addon.add_to_blacklist('david', 'spam@badactor.com')
    
    print("✓ Added to whitelist: trusted@company.com, newsletter@news.com")
    print("✓ Added to blacklist: spam@badactor.com")
    
    print("\n2. Testing email from whitelisted sender...")
    print_separator('-')
    
    whitelisted_email = {
        'sender': 'trusted@company.com',
        'subject': 'Even if this looks suspicious, it should pass',
        'body': 'URGENT! Click here now! Verify your account immediately!',
        'urls': ['http://suspicious-link.com']
    }
    
    result = addon.analyze_single_email('david', whitelisted_email)
    print(f"   Sender: {whitelisted_email['sender']}")
    print(f"   Result: {result.get('reason', 'N/A')}")
    print(f"   Is Threat: {result['is_threat']}")
    
    print("\n3. Testing email from blacklisted sender...")
    print_separator('-')
    
    blacklisted_email = {
        'sender': 'spam@badactor.com',
        'subject': 'Legitimate looking subject',
        'body': 'This is a normal looking email with no suspicious content.',
        'urls': []
    }
    
    result = addon.analyze_single_email('david', blacklisted_email)
    print(f"   Sender: {blacklisted_email['sender']}")
    print(f"   Result: {result.get('reason', 'N/A')}")
    print(f"   Is Threat: {result['is_threat']}")


def demo_custom_settings():
    """Demonstrate custom settings for different users."""
    print("\n" + "="*80)
    print("GMAIL ADD-ON DEMO - Custom Settings Per User")
    print("="*80)
    
    addon = GmailAddonIntegration()
    
    print("\n1. Setting up users with different threat thresholds...")
    print_separator('-')
    
    # Strict user (low threshold = more sensitive)
    addon.setup_user_profile(
        username='strict_user',
        email='strict@example.com',
        threat_threshold=0.4,  # More sensitive
        auto_flag=True
    )
    print("✓ Strict User - Threshold: 40% (more sensitive)")
    
    # Relaxed user (high threshold = less sensitive)
    addon.setup_user_profile(
        username='relaxed_user',
        email='relaxed@example.com',
        threat_threshold=0.8,  # Less sensitive
        auto_flag=True
    )
    print("✓ Relaxed User - Threshold: 80% (less sensitive)")
    
    print("\n2. Testing same email with both profiles...")
    print_separator('-')
    
    test_email = {
        'sender': 'promotion@deals.com',
        'subject': 'Limited Time Offer - Act Now!',
        'body': 'Special discount! Click here to claim your offer. Limited time only!',
        'urls': ['https://deals.com/offer']
    }
    
    print(f"\n   Test Email: {test_email['subject']}")
    
    strict_result = addon.analyze_single_email('strict_user', test_email)
    print(f"\n   Strict User Result:")
    print(f"      Threat Score: {strict_result['threat_score']:.2%}")
    print(f"      Is Threat (threshold 40%): {strict_result['threat_score'] >= 0.4}")
    
    relaxed_result = addon.analyze_single_email('relaxed_user', test_email)
    print(f"\n   Relaxed User Result:")
    print(f"      Threat Score: {relaxed_result['threat_score']:.2%}")
    print(f"      Is Threat (threshold 80%): {relaxed_result['threat_score'] >= 0.8}")
    
    print("\n   💡 Same email, different results based on user preferences!")


def main():
    """Run all demonstrations."""
    print("\n" + "="*80)
    print("  GMAIL EMAIL THREAT DETECTION ADD-ON")
    print("  Modular ML/NLP System for Multiple User Profiles")
    print("="*80)
    
    try:
        # Run demonstrations
        demo_basic_usage()
        print("\n")
        demo_single_email_analysis()
        print("\n")
        demo_whitelist_blacklist()
        print("\n")
        demo_custom_settings()
        
        print("\n" + "="*80)
        print("✓ DEMO COMPLETE!")
        print("="*80)
        print("\nThe add-on is now configured for multiple users.")
        print("Each user has their own profile with custom settings.")
        print("\nKey Features Demonstrated:")
        print("  ✓ Multi-user profile support")
        print("  ✓ Automatic threat detection and flagging")
        print("  ✓ Customizable threat thresholds")
        print("  ✓ Whitelist/Blacklist management")
        print("  ✓ Real-time email analysis")
        print("  ✓ Detailed threat reports")
        print("  ✓ User statistics and dashboards")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
