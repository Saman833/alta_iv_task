import csv
import io
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text, MetaData, Table as SQLTable, Column, String, Text, DateTime, Integer, Float, Boolean
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import json
from services.agent_service import AgentService

class CSVImportService:
    def __init__(self, db: Session):
        self.db = db
        self.metadata = MetaData()
    
    def create_dynamic_table(self, table_name: str, csv_content: str) -> str:
        """
        Create a dynamic table based on CSV structure and import data
        
        Args:
            table_name: Name for the new table
            csv_content: CSV content as string
            
        Returns:
            table_id: The unique ID of the created table
        """
        try:
            # Parse CSV to determine structure
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            fieldnames = csv_reader.fieldnames
            
            if not fieldnames:
                raise ValueError("CSV file has no headers")
            
            # Generate unique table ID
            table_id = str(uuid.uuid4())
            
            # Create table definition - start with system columns if not in CSV
            columns = []
            
            # Add system columns only if they don't exist in CSV
            # For analytics tables, we'll add a row_id as primary key if no id exists
            if 'id' not in fieldnames:
                columns.append(Column('row_id', String(36), primary_key=True, nullable=False))
            else:
                # If CSV has id column, add a unique row_id for primary key
                columns.append(Column('row_id', String(36), primary_key=True, nullable=False))
            
            if 'created_at' not in fieldnames:
                columns.append(Column('created_at', String(50), nullable=True))
            if 'updated_at' not in fieldnames:
                columns.append(Column('updated_at', String(50), nullable=True))
            
            # Get sample data for column type analysis
            csv_reader_for_sample = csv.DictReader(io.StringIO(csv_content))
            sample_data = list(csv_reader_for_sample)
            
            # Add columns based on CSV headers
            for field in fieldnames:
                # Get sample data for this column
                field_sample_data = [row.get(field, '') for row in sample_data[:20]]
                
                # Determine column type based on field name and sample data
                column_type = self._determine_column_type(field, field_sample_data)
                # All CSV columns are nullable for analytics flexibility
                columns.append(Column(field, column_type, nullable=True))
            
            # Create the table
            dynamic_table = SQLTable(
                f"csv_table_{table_id.replace('-', '_')}",
                self.metadata,
                *columns
            )
            
            # Create table in database
            self.metadata.create_all(self.db.bind)
            
            # Import CSV data
            self._import_csv_data(dynamic_table, csv_content, fieldnames)
            
            return table_id
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to create dynamic table: {str(e)}")
    
    def _determine_column_type(self, field_name: str, sample_data: List[str] = None) -> Any:
        """
        Determine the appropriate SQLAlchemy column type using the column type analyzer agent
        """
        try:
            # Use agent service to analyze column type
            agent_service = AgentService()
            
            # Prepare sample data for analysis (first 20 rows)
            sample_rows = sample_data[:20] if sample_data else []
            
            # Call the column type analyzer agent
            result = agent_service.call_agent(
                agent_name="column_type_analyzer_agent",
                input_data={
                    "column_name": field_name,
                    "sample_data": sample_rows
                }
            )
            
            # Parse the agent response to get the recommended type
            if result and "column_type" in result:
                type_name = result["column_type"]
                
                # Map type names to SQLAlchemy types
                type_mapping = {
                    "Integer": Integer,
                    "Float": Float,
                    "String": String(500),
                    "Text": Text,
                    "DateTime": DateTime,
                    "Boolean": Boolean
                }
                
                return type_mapping.get(type_name, String(500))
            
            # Fallback to String if agent fails
            return String(500)
            
        except Exception as e:
            # Fallback to String type if agent analysis fails
            return String(500)
    
    def _convert_value_for_column_type(self, value: str, field_name: str) -> Any:
        """
        Convert CSV value to appropriate type based on column type
        """
        if not value or value.strip() == '':
            return None
        
        try:
            # Get column type for this field
            column_type = self._determine_column_type(field_name)
            
            # Convert based on type
            if column_type == Integer:
                return int(value)
            elif column_type == Float:
                return float(value)
            elif column_type == Boolean:
                # Handle various boolean representations
                value_lower = value.lower().strip()
                if value_lower in ['true', '1', 'yes', 'y']:
                    return True
                elif value_lower in ['false', '0', 'no', 'n']:
                    return False
                else:
                    return None
            elif column_type == DateTime:
                # Try to parse datetime
                try:
                    return datetime.fromisoformat(value)
                except:
                    return value  # Keep as string if parsing fails
            else:
                # String or Text type
                return value
                
        except (ValueError, TypeError):
            # If conversion fails, return as string
            return value
    
    def _import_csv_data(self, table: SQLTable, csv_content: str, fieldnames: List[str]) -> None:
        """
        Import CSV data into the created table using bulk insert
        """
        try:
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            
            # Prepare data for bulk insert
            rows_to_insert = []
            for row in csv_reader:
                # Clean and prepare row data
                cleaned_row = {}
                
                # Add system columns - always add row_id for primary key
                cleaned_row['row_id'] = str(uuid.uuid4())
                if 'created_at' not in fieldnames:
                    cleaned_row['created_at'] = datetime.utcnow().isoformat()
                if 'updated_at' not in fieldnames:
                    cleaned_row['updated_at'] = datetime.utcnow().isoformat()
                
                for field in fieldnames:
                    value = row.get(field, '')
                    # Convert value based on column type
                    cleaned_row[field] = self._convert_value_for_column_type(value, field)
                
                rows_to_insert.append(cleaned_row)
            
            # Bulk insert using raw SQL for better performance
            if rows_to_insert:
                self._bulk_insert_data(table, rows_to_insert, fieldnames)
                
        except Exception as e:
            raise ValueError(f"Failed to import CSV data: {str(e)}")
    
    def _bulk_insert_data(self, table: SQLTable, rows: List[Dict], fieldnames: List[str]) -> None:
        """
        Perform bulk insert using simple insert statements
        """
        try:
            # Determine which columns to include based on the first row
            if not rows:
                return
            
            # Insert rows one by one for SQLite compatibility
            for row in rows:
                insert_stmt = table.insert().values(**row)
                self.db.execute(insert_stmt)
            
            self.db.commit()
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Database error during bulk insert: {str(e)}")
    
    def get_table_data(self, table_id: str, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """
        Retrieve data from a dynamic table
        
        Args:
            table_id: The table ID
            limit: Number of rows to return
            offset: Number of rows to skip
            
        Returns:
            Dictionary containing table metadata and data
        """
        try:
            table_name = f"csv_table_{table_id.replace('-', '_')}"
            
            # Get table structure
            columns_query = text(f"""
                PRAGMA table_info({table_name})
            """)
            columns_result = self.db.execute(columns_query)
            columns = [row[1] for row in columns_result.fetchall()]
            
            # Get data
            data_query = text(f"""
                SELECT * FROM {table_name}
                LIMIT :limit OFFSET :offset
            """)
            data_result = self.db.execute(data_query, {"limit": limit, "offset": offset})
            
            # Convert to list of dictionaries
            rows = []
            for row in data_result.fetchall():
                row_dict = {}
                for i, column in enumerate(columns):
                    value = row[i]
                    # All values are now strings, no need for datetime conversion
                    row_dict[column] = value
                rows.append(row_dict)
            
            # Get total count
            count_query = text(f"SELECT COUNT(*) FROM {table_name}")
            total_count = self.db.execute(count_query).scalar()
            
            return {
                "table_id": table_id,
                "table_name": table_name,
                "columns": columns,
                "data": rows,
                "total_count": total_count,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            raise ValueError(f"Failed to retrieve table data: {str(e)}")
    
    def search_table_data(self, table_id: str, search_term: str, columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Search data in a dynamic table
        
        Args:
            table_id: The table ID
            search_term: Term to search for
            columns: Specific columns to search in (if None, searches all text columns)
            
        Returns:
            Dictionary containing search results
        """
        try:
            table_name = f"csv_table_{table_id.replace('-', '_')}"
            
            # Get table structure
            columns_query = text(f"PRAGMA table_info({table_name})")
            columns_result = self.db.execute(columns_query)
            all_columns = [row[1] for row in columns_result.fetchall()]
            
            # If no specific columns provided, search in all text columns
            if not columns:
                columns = [col for col in all_columns if col not in ['id', 'created_at', 'updated_at']]
            
            # Build search query
            search_conditions = []
            for column in columns:
                search_conditions.append(f"{column} LIKE :search_term")
            
            where_clause = " OR ".join(search_conditions)
            
            search_query = text(f"""
                SELECT * FROM {table_name}
                WHERE {where_clause}
                LIMIT 100
            """)
            
            search_result = self.db.execute(search_query, {"search_term": f"%{search_term}%"})
            
            # Convert to list of dictionaries
            rows = []
            for row in search_result.fetchall():
                row_dict = {}
                for i, column in enumerate(all_columns):
                    value = row[i]
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    row_dict[column] = value
                rows.append(row_dict)
            
            return {
                "table_id": table_id,
                "search_term": search_term,
                "searched_columns": columns,
                "results": rows,
                "result_count": len(rows)
            }
            
        except Exception as e:
            raise ValueError(f"Failed to search table data: {str(e)}")
    
    def delete_table(self, table_id: str) -> bool:
        """
        Delete a dynamic table
        
        Args:
            table_id: The table ID to delete
            
        Returns:
            True if successful
        """
        try:
            table_name = f"csv_table_{table_id.replace('-', '_')}"
            
            # Drop the table
            drop_query = text(f"DROP TABLE IF EXISTS {table_name}")
            self.db.execute(drop_query)
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to delete table: {str(e)}") 