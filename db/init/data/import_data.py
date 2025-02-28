#!/usr/bin/env python3
"""
Script to parse Stampli JSON data and populate the database.
This script is designed to run in the PostgreSQL container
during initialization.
Refactored to use pandas and pydantic for simpler data handling.
"""

import json
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from pydantic import BaseModel, Field
from typing import Any, List, Dict, Optional
import argparse
import logging
import sys
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Define Pydantic models for our data structures
class DataItem(BaseModel):
    type: str
    value: str

class DataField(BaseModel):
    data: List[DataItem] = []
    
    def get_value(self) -> Optional[str]:
        """Extract the first value from the data list."""
        if not self.data:
            return None
        for item in self.data:
            if item.value:
                return item.value
        return None

class CompanyInfo(BaseModel):
    """Model for company information."""
    company_name: Optional[DataField] = Field(None, alias="Company Name")
    company_website: Optional[DataField] = Field(None, alias="Company Website")
    company_description: Optional[DataField] = Field(None, alias="Company Description")
    official_overview: Optional[DataField] = Field(None, alias="Official Overview ")  # Note the space
    product_overview: Optional[DataField] = Field(None, alias="Product Overview")
    differentiators: Optional[DataField] = Field(None, alias="Stampli differentiators")
    ap_automation_url: Optional[DataField] = Field(None, alias="AP Automation")
    
    class Config:
        allow_population_by_field_name = True
        extra = "ignore"
    
    def to_df(self) -> pd.DataFrame:
        """Convert to DataFrame."""
        return pd.DataFrame([{
            "company_name": self.company_name.get_value() if self.company_name else None,
            "company_website": self.company_website.get_value() if self.company_website else None,
            "company_description": self.company_description.get_value() if self.company_description else None,
            "official_overview": self.official_overview.get_value() if self.official_overview else None,
            "product_overview": self.product_overview.get_value() if self.product_overview else None,
            "differentiators": self.differentiators.get_value() if self.differentiators else None,
            "ap_automation_url": self.ap_automation_url.get_value() if self.ap_automation_url else None,
        }])

class EntityInfo(BaseModel):
    """Model for entities like Personas, Industries, etc."""
    name: str
    info: DataField
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.info.get_value(),
            "url": self.info.get_value(),  # Same value for both fields
        }

class AccountInfo(BaseModel):
    """Model for account entities."""
    name: str
    info: DataField
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "url": self.info.get_value(),
        }

class TargetInfo(BaseModel):
    """Model for target information."""
    Personas: Dict[str, DataField] = {}
    Industries: Dict[str, DataField] = {}
    Accounts: Dict[str, DataField] = {}
    Healthcare_Subverticals: Dict[str, DataField] = Field({}, alias="Healthcare Subverticals")
    
    class Config:
        allow_population_by_field_name = True
        extra = "ignore"
    
    def to_dfs(self) -> Dict[str, pd.DataFrame]:
        """Convert to DataFrames."""
        result = {}
        
        # Process Personas
        personas = [
            EntityInfo(name=name, info=info).to_dict()
            for name, info in self.Personas.items()
            if name != "meta"
        ]
        result["personas"] = pd.DataFrame(personas) if personas else pd.DataFrame(columns=["name", "description", "url"])
        
        # Process Industries
        industries = [
            EntityInfo(name=name, info=info).to_dict()
            for name, info in self.Industries.items()
            if name != "meta"
        ]
        result["industries"] = pd.DataFrame(industries) if industries else pd.DataFrame(columns=["name", "description", "url"])
        
        # Process Healthcare Subverticals
        subverticals = [
            EntityInfo(name=name, info=info).to_dict()
            for name, info in self.Healthcare_Subverticals.items()
            if name != "meta"
        ]
        result["healthcare_subverticals"] = pd.DataFrame(subverticals) if subverticals else pd.DataFrame(columns=["name", "description", "url"])
        
        # Process Accounts
        accounts = [
            AccountInfo(name=name, info=info).to_dict()
            for name, info in self.Accounts.items()
            if name != "meta"
        ]
        result["accounts"] = pd.DataFrame(accounts) if accounts else pd.DataFrame(columns=["name", "url"])
        
        return result

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Parse JSON data and populate PostgreSQL database')
    parser.add_argument('--host', default='localhost', help='Database host')
    parser.add_argument('--port', default='5432', help='Database port')
    parser.add_argument('--dbname', required=True, help='Database name')
    parser.add_argument('--user', required=True, help='Database user')
    parser.add_argument('--password', help='Database password')
    parser.add_argument('--company_file', default='company_info.json', help='Path to company info JSON file')
    parser.add_argument('--target_file', default='target_info.json', help='Path to target info JSON file')
    parser.add_argument('--clean', action='store_true', help='Clean existing data before import')
    parser.add_argument('--summary', action='store_true', help='Print summary after import')
    
    return parser.parse_args()

def get_connection_string(args):
    """Create a SQLAlchemy connection string."""
    password_part = f":{args.password}" if args.password else ""
    return f"postgresql://{args.user}{password_part}@{args.host}:{args.port}/{args.dbname}"

def connect_to_db(args):
    """Connect to the PostgreSQL database."""
    conn_params = {
        'host': args.host,
        'port': args.port,
        'dbname': args.dbname,
        'user': args.user,
    }
    
    if args.password:
        conn_params['password'] = args.password
        
    logger.info(f"Connecting to database {args.dbname} on {args.host}:{args.port}")
    return psycopg2.connect(**conn_params)

def clean_database(conn):
    """Clean existing data from the database."""
    logger.info("Cleaning existing data from database")
    
    with conn.cursor() as cur:
        # Delete data in reverse order of dependencies
        cur.execute("DELETE FROM healthcare_subverticals")
        cur.execute("DELETE FROM accounts")
        cur.execute("DELETE FROM industries")
        cur.execute("DELETE FROM personas")
        cur.execute("DELETE FROM company_info")
    
    conn.commit()
    logger.info("Database cleaned successfully")

def load_json_from_file(filepath):
    """Load JSON data from a file that contains a variable assignment."""
    with open(filepath, 'r') as f:
        content = f.read()
        # Extract just the JSON object part
        json_str = content.split('=', 1)[1].strip()
        return json.loads(json_str)



def print_summary(conn_string):
    """Print a summary of the data in the database using pandas."""
    logger.info("Generating data summary")
    
    engine = create_engine(conn_string)
    
    # Count records in each table
    tables = ['company_info', 'personas', 'industries', 'accounts', 
              'healthcare_subverticals']
    
    counts = {}
    for table in tables:
        query = f"SELECT COUNT(*) as count FROM {table}"
        count = pd.read_sql(query, engine).iloc[0]['count']
        counts[table] = count
    
    # Print summary
    print("\n" + "="*50)
    print("DATA IMPORT SUMMARY")
    print("="*50)
    print(f"Company Info Records:        {counts['company_info']}")
    print(f"Personas:                    {counts['personas']}")
    print(f"Industries:                  {counts['industries']}")
    print(f"Accounts:                    {counts['accounts']}")
    print(f"Healthcare Subverticals:     {counts['healthcare_subverticals']}")
    print("="*50)
    print(f"Import completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50 + "\n")

def main():
    """Main function to parse JSON data and populate the database."""
    args = parse_args()
    
    try:
        # Get connection string
        conn_string = get_connection_string(args)
        
        # Connect to the database
        conn = connect_to_db(args)
        conn.autocommit = False
        
        try:
            # Clean database if requested
            if args.clean:
                clean_database(conn)
            
            # Load and parse JSON files using pydantic
            logger.info("Loading and parsing data files")
            company_json = load_json_from_file(args.company_file)
            target_json = load_json_from_file(args.target_file)
            
            # Convert to pydantic models
            company_model = CompanyInfo.parse_obj(company_json)
            target_model = TargetInfo.parse_obj(target_json)
            
            # Convert to pandas DataFrames
            company_df = company_model.to_df()
            target_dfs = target_model.to_dfs()
            
            # Create SQLAlchemy engine
            engine = create_engine(conn_string)
            
            # Insert company info
            company_df.to_sql('company_info', engine, if_exists='append', index=False)
            company_id = pd.read_sql("SELECT id FROM company_info ORDER BY id DESC LIMIT 1", engine).iloc[0]['id']
            
            # Insert other entities
            for table_name, df in target_dfs.items():
                if not df.empty:
                    df.to_sql(table_name, engine, if_exists='append', index=False)
            
            # Commit changes
            conn.commit()
            logger.info("Database population completed successfully")
            
            # Print summary if requested
            if args.summary:
                print_summary(conn_string)
        
        except Exception as e:
            conn.rollback()
            logger.error(f"Error populating database: {e}")
            raise
        finally:
            conn.close()
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())