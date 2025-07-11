import csv
import io
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text, MetaData, Table as SQLTable, Column, String, Text, DateTime, Integer, Float, Boolean
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import json

class CSVImportServiceFast:
    def __init__(self, db: Session):
        self.db = db
        self.metadata = MetaData()
    
    def create_dynamic_table(self, table_name: str, csv_content: str) -> str:
        """
        Create a dynamic table based on CSV structure and import data
        FAST VERSION: No AI agent calls, uses simple type detection
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
                
                # FAST: Use simple type detection instead of AI agent
                column_type = self._determine_column_type_fast(field, field_sample_data)
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
    
    def _determine_column_type_fast(self, field_name: str, sample_data: List[str]) -> Any:
        """
        FAST: Determine column type using simple heuristics instead of AI agent
        """
        if not sample_data:
            return String(500)
        
        # Remove empty values
        non_empty_values = [str(v).strip() for v in sample_data if v and str(v).strip()]
        if not non_empty_values:
            return String(500)
        
        # Simple type detection
        try:
            # Check if all values are integers
            all_integers = all(self._is_integer(v) for v in non_empty_values)
            if all_integers:
                return Integer
            
            # Check if all values are floats
            all_floats = all(self._is_float(v) for v in non_empty_values)
            if all_floats:
                return Float
            
            # Check if all values are booleans
            all_booleans = all(self._is_boolean(v) for v in non_empty_values)
            if all_booleans:
                return Boolean
            
            # Check if all values are dates
            all_dates = all(self._is_date(v) for v in non_empty_values)
            if all_dates:
                return DateTime
            
            # Default to String
            return String(500)
            
        except Exception:
            # Fallback to String if any error
            return String(500)
    
    def _is_integer(self, value: str) -> bool:
        """Check if value is an integer"""
        try:
            int(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def _is_float(self, value: str) -> bool:
        """Check if value is a float"""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def _is_boolean(self, value: str) -> bool:
        """Check if value is a boolean"""
        value_lower = value.lower().strip()
        return value_lower in ['true', 'false', '1', '0', 'yes', 'no', 'y', 'n']
    
    def _is_date(self, value: str) -> bool:
        """Check if value is a date"""
        try:
            datetime.fromisoformat(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def _convert_value_for_column_type(self, value: str, field_name: str) -> Any:
        """
        Convert CSV value to appropriate type based on column type
        """
        if not value or value.strip() == '':
            return None
        
        try:
            # Get column type for this field (simplified)
            if self._is_integer(value):
                return int(value)
            elif self._is_float(value):
                return float(value)
            elif self._is_boolean(value):
                value_lower = value.lower().strip()
                if value_lower in ['true', '1', 'yes', 'y']:
                    return True
                elif value_lower in ['false', '0', 'no', 'n']:
                    return False
                else:
                    return None
            elif self._is_date(value):
                try:
                    return datetime.fromisoformat(value)
                except:
                    return value  # Keep as string if parsing fails
            else:
                # String type
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