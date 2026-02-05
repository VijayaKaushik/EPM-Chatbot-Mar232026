import sqlite3
from datetime import datetime, date
from typing import List, Tuple, Optional

class BankingDatabase:
    """Class to manage SQLite database operations for banking system"""

    def __init__(self, db_name: str = "banking.db"):
        """Initialize database connection"""
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        """Connect to the SQLite database"""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        print(f"Connected to database: {self.db_name}")

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            print("Database connection closed")

    def create_tables(self):
        """Create all three tables with proper schema"""

        # Table 1: Private Bankers
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS private_bankers (
                                                                           banker_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                           first_name TEXT NOT NULL,
                                                                           last_name TEXT NOT NULL,
                                                                           email TEXT UNIQUE NOT NULL,
                                                                           phone TEXT,
                                                                           job_title TEXT NOT NULL,
                                                                           office_location TEXT NOT NULL,
                                                                           city TEXT NOT NULL,
                                                                           state TEXT,
                                                                           country TEXT NOT NULL,
                                                                           hire_date DATE,
                                                                           years_of_experience INTEGER,
                                                                           specialization TEXT,
                                                                           is_active BOOLEAN DEFAULT 1,
                                                                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                                                           updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                            """)

        # Table 2: Clients
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS clients (
                                                                   client_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                   first_name TEXT NOT NULL,
                                                                   last_name TEXT NOT NULL,
                                                                   email TEXT UNIQUE,
                                                                   phone TEXT,
                                                                   date_of_birth DATE,
                                                                   account_opened_date DATE DEFAULT CURRENT_DATE,
                                                                   banker_id INTEGER,
                                                                   net_worth DECIMAL(15, 2),
                                risk_profile TEXT CHECK(risk_profile IN ('Conservative', 'Moderate', 'Aggressive')),
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (banker_id) REFERENCES private_bankers(banker_id)
                                )
                            """)

        # Table 3: Corporate Companies
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS corporate_companies (
                                                                               company_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                               client_id INTEGER NOT NULL,
                                                                               company_name TEXT NOT NULL,
                                                                               industry TEXT,
                                                                               annual_revenue DECIMAL(15, 2),
                                revenue_currency TEXT DEFAULT 'USD',
                                founded_year INTEGER,
                                employee_count INTEGER,
                                headquarters_location TEXT,
                                client_ownership_percentage DECIMAL(5, 2),
                                client_role TEXT,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (client_id) REFERENCES clients(client_id)
                                )
                            """)

        # Create indexes
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_clients_banker ON clients(banker_id)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_clients_email ON clients(email)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_bankers_location ON private_bankers(office_location)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_bankers_job_title ON private_bankers(job_title)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_companies_client ON corporate_companies(client_id)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_companies_revenue ON corporate_companies(annual_revenue)")

        self.conn.commit()
        print("Tables created successfully")

    def insert_private_banker(self, first_name: str, last_name: str, email: str,
                              job_title: str, office_location: str, city: str,
                              country: str, phone: str = None, state: str = None,
                              hire_date: str = None, years_of_experience: int = None,
                              specialization: str = None, is_active: bool = True) -> int:
        """Insert a new private banker and return the banker_id"""

        query = """
                INSERT INTO private_bankers
                (first_name, last_name, email, phone, job_title, office_location,
                 city, state, country, hire_date, years_of_experience, specialization, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) \
                """

        self.cursor.execute(query, (
            first_name, last_name, email, phone, job_title, office_location,
            city, state, country, hire_date, years_of_experience, specialization, is_active
        ))
        self.conn.commit()

        banker_id = self.cursor.lastrowid
        print(f"Inserted private banker: {first_name} {last_name} (ID: {banker_id})")
        return banker_id

    def insert_client(self, first_name: str, last_name: str, email: str,
                      banker_id: int, phone: str = None, date_of_birth: str = None,
                      account_opened_date: str = None, net_worth: float = None,
                      risk_profile: str = 'Moderate') -> int:
        """Insert a new client and return the client_id"""

        query = """
                INSERT INTO clients
                (first_name, last_name, email, phone, date_of_birth,
                 account_opened_date, banker_id, net_worth, risk_profile)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) \
                """

        self.cursor.execute(query, (
            first_name, last_name, email, phone, date_of_birth,
            account_opened_date, banker_id, net_worth, risk_profile
        ))
        self.conn.commit()

        client_id = self.cursor.lastrowid
        print(f"Inserted client: {first_name} {last_name} (ID: {client_id})")
        return client_id

    def insert_corporate_company(self, client_id: int, company_name: str,
                                 industry: str = None, annual_revenue: float = None,
                                 revenue_currency: str = 'USD', founded_year: int = None,
                                 employee_count: int = None, headquarters_location: str = None,
                                 client_ownership_percentage: float = None,
                                 client_role: str = None) -> int:
        """Insert a new corporate company and return the company_id"""

        query = """
                INSERT INTO corporate_companies
                (client_id, company_name, industry, annual_revenue, revenue_currency,
                 founded_year, employee_count, headquarters_location,
                 client_ownership_percentage, client_role)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) \
                """

        self.cursor.execute(query, (
            client_id, company_name, industry, annual_revenue, revenue_currency,
            founded_year, employee_count, headquarters_location,
            client_ownership_percentage, client_role
        ))
        self.conn.commit()

        company_id = self.cursor.lastrowid
        print(f"Inserted company: {company_name} (ID: {company_id})")
        return company_id

    def get_all_bankers(self) -> List[Tuple]:
        """Retrieve all private bankers"""
        self.cursor.execute("SELECT * FROM private_bankers")
        return self.cursor.fetchall()

    def get_all_clients(self) -> List[Tuple]:
        """Retrieve all clients"""
        self.cursor.execute("SELECT * FROM clients")
        return self.cursor.fetchall()

    def get_all_companies(self) -> List[Tuple]:
        """Retrieve all companies"""
        self.cursor.execute("SELECT * FROM corporate_companies")
        return self.cursor.fetchall()

    def get_clients_by_banker(self, banker_id: int) -> List[Tuple]:
        """Get all clients for a specific banker"""
        query = """
                SELECT c.*, pb.first_name || ' ' || pb.last_name as banker_name
                FROM clients c
                         JOIN private_bankers pb ON c.banker_id = pb.banker_id
                WHERE c.banker_id = ? \
                """
        self.cursor.execute(query, (banker_id,))
        return self.cursor.fetchall()

    def get_companies_by_client(self, client_id: int) -> List[Tuple]:
        """Get all companies for a specific client"""
        query = """
                SELECT cc.*, c.first_name || ' ' || c.last_name as client_name
                FROM corporate_companies cc
                         JOIN clients c ON cc.client_id = c.client_id
                WHERE cc.client_id = ? \
                """
        self.cursor.execute(query, (client_id,))
        return self.cursor.fetchall()

    def get_full_client_report(self, client_id: int) -> dict:
        """Get complete information about a client including banker and companies"""
        # Get client info
        self.cursor.execute("""
                            SELECT c.*, pb.first_name || ' ' || pb.last_name as banker_name,
                                   pb.email as banker_email, pb.office_location
                            FROM clients c
                                     LEFT JOIN private_bankers pb ON c.banker_id = pb.banker_id
                            WHERE c.client_id = ?
                            """, (client_id,))
        client = self.cursor.fetchone()

        # Get companies
        companies = self.get_companies_by_client(client_id)

        return {
            'client': client,
            'companies': companies
        }


def main():
    """Example usage of the BankingDatabase class"""

    # Initialize database
    db = BankingDatabase("banking.db")
    db.connect()

    # Create tables
    db.create_tables()

    print("\n" + "="*60)
    print("INSERTING SAMPLE DATA")
    print("="*60 + "\n")

    # Insert private bankers
    banker1_id = db.insert_private_banker(
        first_name="Sarah",
        last_name="Johnson",
        email="sarah.johnson@bank.com",
        phone="+1-555-0101",
        job_title="Senior Private Banker",
        office_location="Manhattan Office",
        city="New York",
        state="NY",
        country="USA",
        hire_date="2015-03-15",
        years_of_experience=10,
        specialization="High Net Worth Individuals"
    )

    banker2_id = db.insert_private_banker(
        first_name="Michael",
        last_name="Chen",
        email="michael.chen@bank.com",
        phone="+1-555-0102",
        job_title="Private Banking Director",
        office_location="Los Angeles Office",
        city="Los Angeles",
        state="CA",
        country="USA",
        hire_date="2012-07-20",
        years_of_experience=13,
        specialization="Investment Management"
    )

    banker3_id = db.insert_private_banker(
        first_name="Emma",
        last_name="Williams",
        email="emma.williams@bank.com",
        phone="+44-20-5550103",
        job_title="Private Banker",
        office_location="London Office",
        city="London",
        country="UK",
        hire_date="2018-09-10",
        years_of_experience=6,
        specialization="Estate Planning"
    )

    print("\n" + "-"*60 + "\n")

    # Insert clients
    client1_id = db.insert_client(
        first_name="Robert",
        last_name="Anderson",
        email="robert.anderson@email.com",
        phone="+1-555-1001",
        date_of_birth="1975-05-12",
        account_opened_date="2020-01-15",
        banker_id=banker1_id,
        net_worth=15000000.00,
        risk_profile="Moderate"
    )

    client2_id = db.insert_client(
        first_name="Jennifer",
        last_name="Martinez",
        email="jennifer.martinez@email.com",
        phone="+1-555-1002",
        date_of_birth="1982-11-23",
        account_opened_date="2019-06-20",
        banker_id=banker1_id,
        net_worth=8500000.00,
        risk_profile="Conservative"
    )

    client3_id = db.insert_client(
        first_name="David",
        last_name="Taylor",
        email="david.taylor@email.com",
        phone="+1-555-1003",
        date_of_birth="1968-03-08",
        account_opened_date="2021-03-10",
        banker_id=banker2_id,
        net_worth=25000000.00,
        risk_profile="Aggressive"
    )

    print("\n" + "-"*60 + "\n")

    # Insert corporate companies
    db.insert_corporate_company(
        client_id=client1_id,
        company_name="Anderson Tech Solutions",
        industry="Technology",
        annual_revenue=50000000.00,
        founded_year=2005,
        employee_count=250,
        headquarters_location="San Francisco, CA",
        client_ownership_percentage=65.00,
        client_role="CEO & Founder"
    )

    db.insert_corporate_company(
        client_id=client1_id,
        company_name="CloudServe Inc",
        industry="Cloud Services",
        annual_revenue=12000000.00,
        founded_year=2015,
        employee_count=45,
        headquarters_location="Austin, TX",
        client_ownership_percentage=30.00,
        client_role="Co-Founder"
    )

    db.insert_corporate_company(
        client_id=client2_id,
        company_name="Martinez Consulting Group",
        industry="Business Consulting",
        annual_revenue=8500000.00,
        founded_year=2010,
        employee_count=85,
        headquarters_location="Chicago, IL",
        client_ownership_percentage=100.00,
        client_role="Owner"
    )

    db.insert_corporate_company(
        client_id=client3_id,
        company_name="Taylor Industries",
        industry="Manufacturing",
        annual_revenue=150000000.00,
        founded_year=1998,
        employee_count=850,
        headquarters_location="Detroit, MI",
        client_ownership_percentage=75.00,
        client_role="Chairman & CEO"
    )

    print("\n" + "="*60)
    print("QUERYING DATA")
    print("="*60 + "\n")

    # Query examples
    print("All Private Bankers:")
    bankers = db.get_all_bankers()
    for banker in bankers:
        print(f"  - {banker[1]} {banker[2]}, {banker[5]} at {banker[6]}")

    print(f"\nClients of Banker ID {banker1_id}:")
    clients = db.get_clients_by_banker(banker1_id)
    for client in clients:
        print(f"  - {client[1]} {client[2]}, Net Worth: ${client[8]:,.2f}")

    print(f"\nCompanies owned by Client ID {client1_id}:")
    companies = db.get_companies_by_client(client1_id)
    for company in companies:
        print(f"  - {company[2]}, Revenue: ${company[4]:,.2f}, Ownership: {company[9]}%")

    print(f"\nFull Report for Client ID {client1_id}:")
    report = db.get_full_client_report(client1_id)
    print(f"  Client: {report['client'][1]} {report['client'][2]}")
    print(f"  Banker: {report['client'][-3]}")
    print(f"  Companies:")
    for company in report['companies']:
        print(f"    - {company[2]} (${company[4]:,.2f} revenue)")

    # Close connection
    db.close()
    print("\n" + "="*60)
    print("DONE!")
    print("="*60)


if __name__ == "__main__":
    main()