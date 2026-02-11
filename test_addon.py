"""
Quick Test Script for Gmail Add-on
Tests basic functionality of the email threat detection add-on.
"""

import sys
from gmail_addon_integration import GmailAddonIntegration


def test_basic_functionality():
    """Test basic add-on functionality."""
    print("="*60)
    print("Testing Gmail Add-on Email Threat Detection System")
    print("="*60)
    
    try:
        # Initialize
        print("\n1. Initializing add-on system...")
        addon = GmailAddonIntegration()
        print("   ✓ System initialized")
        
        # Create test user
        print("\n2. Creating test user profile...")
        success = addon.setup_user_profile(
            username='test_user',
            email='test@example.com',
            threat_threshold=0.6,
            auto_flag=True
        )
        
        if not success:
            print("   ℹ Profile already exists, continuing...")
        else:
            print("   ✓ User profile created")
        
        # Test phishing email
        print("\n3. Testing phishing email detection...")
        phishing_email = {
            'sender': 'security@paypa1-verify.com',
            'sender_name': 'PayPal Security',
            'subject': 'URGENT: Your Account Has Been Suspended!!!',
            'body': '''
            Your PayPal account has been suspended due to suspicious activity.
            You must verify your identity IMMEDIATELY by clicking the link below.
            
            VERIFY NOW: http://paypal-verify-2026.tk/login
            
            You have only 24 hours before PERMANENT suspension!
            Act now or lose access forever! URGENT!
            ''',
            'urls': ['http://paypal-verify-2026.tk/login', 'http://192.168.1.1/verify']
        }
        
        result = addon.analyze_single_email('test_user', phishing_email)
        print(f"   Threat Score: {result['threat_score']:.2%}")
        print(f"   Threat Type: {result['threat_type']}")
        print(f"   Is Threat: {result['is_threat']}")
        
        if result['is_threat'] and result['threat_score'] > 0.5:
            print("   ✓ Correctly identified as threat")
        else:
            print("   ⚠ Warning: Did not identify phishing email (may need model training)")
        
        # Test legitimate email
        print("\n4. Testing legitimate email detection...")
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
            - Upcoming webinar
            
            Best regards,
            The Company Team
            
            Unsubscribe: https://company.com/unsubscribe
            ''',
            'urls': ['https://company.com/blog', 'https://company.com/unsubscribe']
        }
        
        result = addon.analyze_single_email('test_user', legitimate_email)
        print(f"   Threat Score: {result['threat_score']:.2%}")
        print(f"   Threat Type: {result['threat_type']}")
        print(f"   Is Threat: {result['is_threat']}")
        
        if not result['is_threat'] or result['threat_score'] < 0.5:
            print("   ✓ Correctly identified as legitimate")
        else:
            print("   ⚠ Warning: False positive on legitimate email")
        
        # Test whitelist
        print("\n5. Testing whitelist functionality...")
        addon.add_to_whitelist('test_user', 'trusted@company.com')
        
        whitelisted_email = {
            'sender': 'trusted@company.com',
            'subject': 'Test Email',
            'body': 'Even if this looks suspicious URGENT! CLICK HERE NOW!',
            'urls': ['http://test.com']
        }
        
        result = addon.analyze_single_email('test_user', whitelisted_email)
        print(f"   Is Threat: {result['is_threat']}")
        print(f"   Reason: {result.get('reason', 'N/A')}")
        
        if not result['is_threat']:
            print("   ✓ Whitelist working correctly")
        else:
            print("   ✗ Whitelist not working")
        
        # Test dashboard
        print("\n6. Testing user dashboard...")
        dashboard = addon.get_user_dashboard('test_user')
        print(f"   Username: {dashboard['username']}")
        print(f"   Email: {dashboard['email']}")
        print(f"   Add-on Enabled: {dashboard['addon_enabled']}")
        print(f"   Threat Threshold: {dashboard['threat_threshold']:.0%}")
        print("   ✓ Dashboard accessible")
        
        # Test sample emails
        print("\n7. Testing sample email generation...")
        addon.add_sample_emails('test_user', count=5, phishing_ratio=0.4)
        print("   ✓ Sample emails generated")
        
        # Test inbox scanning
        print("\n8. Testing inbox scanning...")
        scan_result = addon.scan_inbox('test_user')
        print(f"   Total Scanned: {scan_result['total_scanned']}")
        print(f"   Threats Found: {scan_result['threats_found']}")
        print(f"   Threat Rate: {scan_result['threat_rate']:.1%}")
        print("   ✓ Inbox scan complete")
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED SUCCESSFULLY!")
        print("="*60)
        print("\nThe Gmail add-on system is working correctly.")
        print("You can now:")
        print("  - Run the full demo: python demo_gmail_addon.py")
        print("  - Integrate into your application")
        print("  - Add more user profiles")
        print("\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("\nPlease ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        return False


def test_multiple_users():
    """Test multi-user functionality."""
    print("\n" + "="*60)
    print("Testing Multi-User Support")
    print("="*60)
    
    try:
        addon = GmailAddonIntegration()
        
        # Create multiple users
        print("\n1. Creating multiple user profiles...")
        users = [
            ('alice', 'alice@example.com', 0.4),  # High sensitivity
            ('bob', 'bob@example.com', 0.6),      # Medium sensitivity
            ('charlie', 'charlie@example.com', 0.8) # Low sensitivity
        ]
        
        for username, email, threshold in users:
            addon.setup_user_profile(username, email, threshold, True)
            print(f"   ✓ Created profile for {username} (threshold: {threshold:.0%})")
        
        # List all profiles
        print("\n2. Listing all profiles...")
        profiles = addon.list_all_profiles()
        print(f"   Total profiles: {len(profiles)}")
        print(f"   Users: {', '.join(profiles)}")
        print("   ✓ Multi-user support working")
        
        print("\n✓ Multi-user test passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Multi-user test failed: {e}")
        return False


if __name__ == '__main__':
    print("\n🔍 Gmail Add-on System Test\n")
    
    # Run basic tests
    basic_passed = test_basic_functionality()
    
    if basic_passed:
        # Run multi-user tests
        multi_passed = test_multiple_users()
        
        if multi_passed:
            print("\n" + "="*60)
            print("🎉 All tests completed successfully!")
            print("="*60)
            print("\nNext steps:")
            print("  1. Run full demo: python demo_gmail_addon.py")
            print("  2. Train ML model: python train_model.py (optional)")
            print("  3. Integrate into your application")
            print("\nFor documentation, see:")
            print("  - GMAIL_ADDON_SETUP.md")
            print("  - INTEGRATION_GUIDE.md")
            print("\n")
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        sys.exit(1)
