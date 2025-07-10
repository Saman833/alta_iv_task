from sqlalchemy.orm import Session


from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

class SQLiteQueryService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def query(self, query: str):
        """
        Execute a SQL query with proper error handling
        
        Args:
            query (str): SQL query string
            
        Returns:
            dict: Query results with status and data
        """
        try:
            # Validate query is not empty
            if not query or not query.strip():
                return {
                    "success": False,
                    "error": "Query cannot be empty",
                    "data": None
                }
            
            # Execute query
            result = self.db.execute(text(query))
            
            # Handle different query types
            if query.strip().upper().startswith(('SELECT', 'PRAGMA')):
                # For SELECT queries, fetch results
                rows = result.fetchall()
                columns = result.keys() if hasattr(result, 'keys') else []
                
                return {
                    "success": True,
                    "error": None,
                    "data": {
                        "rows": [dict(zip(columns, row)) for row in rows],
                        "row_count": len(rows),
                        "columns": list(columns)
                    }
                }
            else:
                # For INSERT, UPDATE, DELETE queries
                self.db.commit()
                return {
                    "success": True,
                    "error": None,
                    "data": {
                        "rows_affected": result.rowcount,
                        "message": "Query executed successfully"
                    }
                }
                
        except SQLAlchemyError as e:
            self.logger.error(f"SQLAlchemy error executing query: {str(e)}")
            self.db.rollback()
            return {
                "success": False,
                "error": f"Database error: {str(e)}",
                "data": None
            }
        except Exception as e:
            self.logger.error(f"Unexpected error executing query: {str(e)}")
            self.db.rollback()
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "data": None
            }

