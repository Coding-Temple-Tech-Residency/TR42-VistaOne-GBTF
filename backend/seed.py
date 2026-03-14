from app import create_app
from models import db, Company, User
from datetime import datetime

def seed_database():
    app = create_app()
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        print("🌱 Seeding database...")
        
        # Create companies
        operator_company = Company(
            name="Permian Operations Inc",
            company_type="operator",
            contact_email="admin@permianops.com",
            contact_phone="432-555-0100",
            address="123 Main St, Midland, TX 79701"
        )
        
        vendor_company = Company(
            name="West Texas Field Services",
            company_type="vendor",
            contact_email="dispatch@westtexas.com",
            contact_phone="432-555-0200",
            address="456 Oil Field Rd, Odessa, TX 79760"
        )
        
        db.session.add_all([operator_company, vendor_company])
        db.session.commit()
        print("✅ Companies created")
        
        # Create test users
        test_users = [
            # Field contractors
            {
                'username': 'john_doe',
                'email': 'john.doe@westtexas.com',
                'password': 'password123',
                'first_name': 'John',
                'last_name': 'Doe',
                'role': 'field_contractor',
                'company': vendor_company,
                'phone': '432-555-1001'
            },
            {
                'username': 'jane_smith',
                'email': 'jane.smith@westtexas.com',
                'password': 'password123',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'role': 'field_contractor',
                'company': vendor_company,
                'phone': '432-555-1002'
            },
            {
                'username': 'bob_wilson',
                'email': 'bob.wilson@westtexas.com',
                'password': 'password123',
                'first_name': 'Bob',
                'last_name': 'Wilson',
                'role': 'field_contractor',
                'company': vendor_company,
                'phone': '432-555-1003'
            },
            # Vendor manager
            {
                'username': 'vendor_manager',
                'email': 'vendor.manager@westtexas.com',
                'password': 'password123',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'role': 'vendor_manager',
                'company': vendor_company,
                'phone': '432-555-2001'
            },
            # Operator admin
            {
                'username': 'operator_admin',
                'email': 'operator.admin@permianops.com',
                'password': 'password123',
                'first_name': 'Mike',
                'last_name': 'Thompson',
                'role': 'operator_admin',
                'company': operator_company,
                'phone': '432-555-3001'
            }
        ]
        
        for user_data in test_users:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data['role'],
                company_id=user_data['company'].id,
                phone=user_data.get('phone'),
                is_active=True
            )
            user.set_password(user_data['password'])
            db.session.add(user)
        
        db.session.commit()
        print("✅ Test users created")
        
        print("\n" + "="*50)
        print("📋 SEED DATA SUMMARY")
        print("="*50)
        print(f"Companies: {Company.query.count()}")
        print(f"Users: {User.query.count()}")
        print("\n🔐 TEST CREDENTIALS:")
        print("-" * 30)
        print("Contractors:")
        print("  john_doe / password123")
        print("  jane_smith / password123")
        print("  bob_wilson / password123")
        print("\nVendor Manager:")
        print("  vendor_manager / password123")
        print("\nOperator Admin:")
        print("  operator_admin / password123")
        print("="*50)

if __name__ == '__main__':
    seed_database()