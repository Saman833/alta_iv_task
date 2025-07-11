from services.agent_service import AgentService
from services.sqlite_query_service import SQLiteQueryService
from repository.table_respository import TableRepository
from repository.file_repository import FileRepository
from models.file import FileType
from sqlalchemy.orm import Session
import json
import time

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.agent_service = AgentService()
        self.query_service = SQLiteQueryService(db)
        self.table_repository = TableRepository(db)
        self.file_repository = FileRepository(db)
    
    def analyze_user_request(self, user_input: str, context_info: dict = None):
        file_summaries = self._get_all_file_summaries()
        
        enhanced_prompt = self._enhance_user_prompt(user_input, file_summaries, context_info)
        
        query_response = self._generate_analytics_query(user_input, enhanced_prompt, file_summaries)
        
        query_result = self._execute_query(query_response["analysis_response"]["query"])
        
        return {
            "original_input": user_input,
            "enhanced_prompt": enhanced_prompt,
            "generated_query": query_response["analysis_response"]["query"],
            "query_purpose": query_response["analysis_response"]["query_purpose"],
            "query_result": query_result,
            "next_steps": query_response["analysis_response"]["anticipated_next_steps"]
        }
    
    def _get_all_file_summaries(self):
        """
        Retrieve ONLY CSV tables that start with csv_table_ and generate/return their summaries
        ONLY PROCESSES EXISTING TABLES: First gets list of existing tables, then filters
        """
        try:
            # FIRST: Get list of existing tables from database
            existing_tables_query = self.query_service.query("SELECT name FROM sqlite_master WHERE type='table'")
            if not existing_tables_query["success"]:
                print("❌ Could not get existing tables from database")
                return []
            
            existing_tables = [row["name"] for row in existing_tables_query["data"]["rows"]]
            csv_tables = [table for table in existing_tables if table.startswith("csv_table_")]
            
            print(f"📋 Found {len(existing_tables)} total tables, {len(csv_tables)} CSV tables")
            
            if not csv_tables:
                print("ℹ️  No CSV tables found in database")
                return []
            
            file_summaries = []
            
            # Process only existing CSV tables
            for csv_table_name in csv_tables:
                print(f"✅ Processing existing CSV table: {csv_table_name}")
                
                # Extract table ID from csv_table_name
                table_id = csv_table_name.replace("csv_table_", "").replace("_", "-")
                
                # Get the table record from repository
                table = self.table_repository.get_table_by_id(table_id)
                if not table:
                    print(f"⚠️  No table record found for {csv_table_name}, creating basic summary")
                    # Create basic summary for existing table without repository record
                    file_summary = self._generate_file_summary_for_existing_table(csv_table_name)
                    file_summaries.append({
                        "table_name": csv_table_name,
                        "original_file_name": f"{csv_table_name}.csv",
                        "file_summary": file_summary
                    })
                    continue
                
                # Get the file associated with this table
                files = self.file_repository.get_folder_files(table.folder_id)
                csv_files = [f for f in files if f.file_type == FileType.CSV and f.file_name == table.table_name]
                
                if not csv_files:
                    print(f"⚠️  No CSV file found for table {table.table_name}, creating basic summary")
                    # Create basic summary for existing table without file record
                    file_summary = self._generate_file_summary_for_existing_table(csv_table_name)
                    file_summaries.append({
                        "table_name": csv_table_name,
                        "original_file_name": f"{csv_table_name}.csv",
                        "file_summary": file_summary
                    })
                    continue
                    
                file = csv_files[0]  # Get the first matching CSV file
                
                # Check if we already have a detailed summary (not just the default)
                has_detailed_summary = (
                    file.detail_summary and 
                    file.detail_summary != f"File created from {file.file_type.value}" and
                    not file.detail_summary.startswith("File") and
                    "summary generation failed" not in file.detail_summary
                )
                
                if has_detailed_summary:
                    try:
                        # Try to parse existing summary as JSON
                        file_summary = json.loads(file.detail_summary)
                        print(f"✅ Using cached summary for {file.file_name}")
                    except json.JSONDecodeError:
                        # If not valid JSON, generate new summary
                        print(f"🔄 Regenerating summary for {file.file_name} (invalid cached JSON)")
                        file_summary = self._generate_file_summary(table.id, file.file_name)
                        # Update file with new summary
                        self._update_file_summary(file.id, file_summary)
                else:
                    # Generate new summary
                    print(f"🔄 Generating new summary for {file.file_name}")
                    file_summary = self._generate_file_summary(table.id, file.file_name)
                    # Update file with new summary
                    self._update_file_summary(file.id, file_summary)
                
                file_summaries.append({
                    "table_name": csv_table_name,  # This is already in csv_table_ format
                    "original_file_name": file.file_name,
                    "file_summary": file_summary
                })
            
            print(f"📊 Processed {len(file_summaries)} CSV tables starting with csv_table_")
            return file_summaries
            
        except Exception as e:
            print(f"Error getting file summaries: {e}")
            # Return empty list if error occurs
            return []
    
    def _generate_file_summary_for_existing_table(self, csv_table_name: str):
        """
        Generate file summary for existing CSV table without file record
        """
        try:
            print(f"📊 Generating summary for existing table: {csv_table_name}")
            
            # Get sample data from the table (first 100 rows)
            query_result = self.query_service.query(
                f'SELECT * FROM "{csv_table_name}" LIMIT 100'
            )
            
            if not query_result["success"] or not query_result.get("data") or not query_result["data"].get("rows"):
                print(f"⚠️  No data found in table {csv_table_name}")
                return self._create_fallback_summary(f"{csv_table_name}.csv", "Empty table")
            
            # Format data for file_summary_agent
            data = query_result["data"]
            sample_data = data["rows"][:100]
            columns = data["columns"]
            
            print(f"📋 Found {len(sample_data)} rows with {len(columns)} columns")
            
            # Create a robust fallback summary first
            fallback_summary = self._create_smart_fallback_summary(f"{csv_table_name}.csv", columns, sample_data)
            
            # Try to call the AI agent with timeout
            try:
                print(f"🤖 Calling file_summary_agent for existing table...")
                start_time = time.time()
                
                # Prepare enhanced input for file_summary_agent with actual schema
                agent_input = {
                    "file_name": f"{csv_table_name}.csv",
                    "sample_data": sample_data,
                    "column_info": {
                        "column_names": columns,
                        "total_rows": data["row_count"] if data.get("row_count") else len(sample_data),
                        "total_columns": len(columns),
                        "actual_schema": self._get_detailed_column_info(columns, sample_data),
                        "sample_values": self._get_sample_values_per_column(columns, sample_data)
                    }
                }
                
                # Call file_summary_agent
                summary_response = self.agent_service.run_agent("file_summary_agent", agent_input)
                
                end_time = time.time()
                print(f"✅ AI agent completed in {end_time - start_time:.2f} seconds")
                
                if summary_response and "file_summary" in summary_response:
                    ai_summary = summary_response["file_summary"]
                    # Enhance AI summary with actual column information
                    ai_summary["database_schema"] = {
                        "table_name": csv_table_name,
                        "available_columns": columns,
                        "column_details": self._get_detailed_column_info(columns, sample_data),
                        "sample_values": self._get_sample_values_per_column(columns, sample_data)
                    }
                    print(f"🎯 AI summary generated successfully with schema info")
                    return ai_summary
                else:
                    print(f"⚠️  AI agent returned unexpected format, using enhanced fallback")
                    return self._enhance_fallback_with_schema(fallback_summary, csv_table_name, columns, sample_data)
                    
            except Exception as ai_error:
                print(f"❌ AI agent failed: {ai_error}")
                print(f"🔄 Using enhanced fallback summary with schema")
                return self._enhance_fallback_with_schema(fallback_summary, csv_table_name, columns, sample_data)
                
        except Exception as e:
            print(f"Error generating file summary for existing table {csv_table_name}: {e}")
            # Return minimal fallback summary
            return self._create_fallback_summary(f"{csv_table_name}.csv", "Generation error")
    
    def _generate_file_summary(self, table_name: str, file_name: str):
        """
        Generate file summary using file_summary_agent with timeout and fallback
        """
        try:
            # Convert table ID to actual CSV table name format
            csv_table_name = f"csv_table_{table_name.replace('-', '_')}"
            
            print(f"📊 Querying table: {csv_table_name}")
            
            # Get sample data from the table (first 100 rows)
            query_result = self.query_service.query(
                f'SELECT * FROM "{csv_table_name}" LIMIT 100'
            )
            
            if not query_result["success"] or not query_result.get("data") or not query_result["data"].get("rows"):
                print(f"⚠️  No data found in table {csv_table_name}")
                return self._create_fallback_summary(file_name, "Empty table")
            
            # Format data for file_summary_agent
            data = query_result["data"]
            sample_data = data["rows"][:100]  # SQLiteQueryService already returns dict rows
            columns = data["columns"]
            
            print(f"📋 Found {len(sample_data)} rows with {len(columns)} columns")
            
            # Create a robust fallback summary first
            fallback_summary = self._create_smart_fallback_summary(file_name, columns, sample_data)
            
            # Try to call the AI agent with timeout
            try:
                print(f"🤖 Calling file_summary_agent...")
                start_time = time.time()
                
                # Prepare enhanced input for file_summary_agent with actual schema
                agent_input = {
                    "file_name": file_name,
                    "sample_data": sample_data,
                    "column_info": {
                        "column_names": columns,
                        "total_rows": data["row_count"] if data.get("row_count") else len(sample_data),
                        "total_columns": len(columns),
                        "actual_schema": self._get_detailed_column_info(columns, sample_data),
                        "sample_values": self._get_sample_values_per_column(columns, sample_data)
                    }
                }
                
                # Call file_summary_agent
                summary_response = self.agent_service.run_agent("file_summary_agent", agent_input)
                
                end_time = time.time()
                print(f"✅ AI agent completed in {end_time - start_time:.2f} seconds")
                
                if summary_response and "file_summary" in summary_response:
                    ai_summary = summary_response["file_summary"]
                    # Enhance AI summary with actual column information
                    ai_summary["database_schema"] = {
                        "table_name": csv_table_name,
                        "available_columns": columns,
                        "column_details": self._get_detailed_column_info(columns, sample_data),
                        "sample_values": self._get_sample_values_per_column(columns, sample_data)
                    }
                    print(f"🎯 AI summary generated successfully with schema info")
                    return ai_summary
                else:
                    print(f"⚠️  AI agent returned unexpected format, using enhanced fallback")
                    return self._enhance_fallback_with_schema(fallback_summary, csv_table_name, columns, sample_data)
                    
            except Exception as ai_error:
                print(f"❌ AI agent failed: {ai_error}")
                print(f"🔄 Using enhanced fallback summary with schema")
                return self._enhance_fallback_with_schema(fallback_summary, csv_table_name, columns, sample_data)
                
        except Exception as e:
            print(f"Error generating file summary for {file_name}: {e}")
            # Return minimal fallback summary
            return self._create_fallback_summary(file_name, "Generation error")
    
    def _create_smart_fallback_summary(self, file_name: str, columns: list, sample_data: list):
        """
        Create an intelligent fallback summary based on data analysis
        """
        try:
            # Analyze the data to create a better summary
            data_insights = self._analyze_sample_data(columns, sample_data)
            
            return {
                "file_name": file_name,
                "overview": f"CSV file '{file_name}' containing {len(columns)} columns and data analysis shows {data_insights['data_type']} patterns",
                "business_domain": data_insights['inferred_domain'],
                "data_structure": {
                    "total_columns": len(columns),
                    "total_rows_analyzed": len(sample_data),
                    "estimated_total_rows": len(sample_data),
                    "key_columns": [
                        {
                            "name": col,
                            "inferred_type": self._infer_column_type(col, sample_data),
                            "description": f"Column containing {col.replace('_', ' ')} data"
                        }
                        for col in columns[:5]  # First 5 columns
                    ]
                },
                "content_analysis": {
                    "data_quality": "Sample data available for analysis",
                    "patterns": data_insights['patterns']
                },
                "insights": {
                    "key_findings": data_insights['key_findings'],
                    "potential_use_cases": data_insights['use_cases'],
                    "analysis_opportunities": [
                        "Data exploration and trend analysis",
                        "Statistical analysis and reporting",
                        "Data visualization and dashboards"
                    ]
                },
                "recommendations": {
                    "immediate_actions": [
                        "Examine data distribution across key columns",
                        "Check for data quality issues or missing values",
                        "Identify primary keys and relationships"
                    ],
                    "analysis_approaches": [
                        "Descriptive statistics for numerical columns",
                        "Frequency analysis for categorical data",
                        "Time series analysis if date columns present"
                    ]
                }
            }
        except Exception as e:
            print(f"Error creating smart fallback: {e}")
            return self._create_fallback_summary(file_name, "Smart analysis failed")
    
    def _analyze_sample_data(self, columns: list, sample_data: list):
        """
        Analyze sample data to infer patterns and domain
        """
        try:
            # Analyze column names for domain hints
            column_keywords = ' '.join(columns).lower()
            
            # Infer business domain based on column names
            if any(word in column_keywords for word in ['customer', 'user', 'client']):
                domain = 'Customer/User Management'
                data_type = 'customer interaction'
            elif any(word in column_keywords for word in ['transaction', 'payment', 'order', 'purchase']):
                domain = 'E-commerce/Sales'
                data_type = 'transaction'
            elif any(word in column_keywords for word in ['session', 'visit', 'page', 'click']):
                domain = 'Web Analytics'
                data_type = 'user behavior'
            elif any(word in column_keywords for word in ['email', 'message', 'content']):
                domain = 'Communications'
                data_type = 'message/communication'
            elif any(word in column_keywords for word in ['timestamp', 'date', 'time']):
                domain = 'Time Series Data'
                data_type = 'temporal'
            else:
                domain = 'General Business Data'
                data_type = 'business'
            
            # Analyze patterns
            patterns = []
            if 'id' in column_keywords:
                patterns.append("Contains identifier columns")
            if any(word in column_keywords for word in ['date', 'time', 'timestamp']):
                patterns.append("Contains temporal data")
            if len(columns) > 10:
                patterns.append("Wide dataset with many attributes")
            elif len(columns) < 5:
                patterns.append("Narrow dataset with focused attributes")
            
            # Generate key findings
            key_findings = [
                f"Dataset has {len(columns)} columns indicating {'comprehensive' if len(columns) > 8 else 'focused'} data collection",
                f"Sample contains {len(sample_data)} rows for analysis"
            ]
            
            # Generate use cases
            use_cases = [
                f"{domain} analysis and reporting",
                "Data-driven decision making",
                "Business intelligence and insights"
            ]
            
            return {
                'inferred_domain': domain,
                'data_type': data_type,
                'patterns': patterns,
                'key_findings': key_findings,
                'use_cases': use_cases
            }
        except Exception as e:
            return {
                'inferred_domain': 'General Data',
                'data_type': 'business',
                'patterns': ["Standard tabular data"],
                'key_findings': ["Data available for analysis"],
                'use_cases': ["Data analysis", "Reporting"]
            }
    
    def _infer_column_type(self, column_name: str, sample_data: list):
        """
        Infer column type based on name and sample data
        """
        col_lower = column_name.lower()
        
        if 'id' in col_lower:
            return 'Identifier'
        elif any(word in col_lower for word in ['date', 'time', 'timestamp', 'created', 'updated']):
            return 'Date/Time'
        elif any(word in col_lower for word in ['amount', 'price', 'cost', 'value', 'number', 'count']):
            return 'Numeric'
        elif any(word in col_lower for word in ['email', 'mail']):
            return 'Email'
        elif any(word in col_lower for word in ['name', 'title', 'description']):
            return 'Text'
        elif any(word in col_lower for word in ['category', 'type', 'status', 'source']):
            return 'Category'
        else:
            return 'String'
    
    def _create_fallback_summary(self, file_name: str, reason: str):
        """
        Create a minimal fallback summary
        """
        return {
            "file_name": file_name,
            "overview": f"CSV file '{file_name}' - {reason}",
            "business_domain": "Unknown",
            "data_structure": {"total_columns": 0, "key_columns": []},
            "insights": {"potential_use_cases": ["Data analysis (pending successful processing)"]}
        }
    
    def _update_file_summary(self, file_id: str, file_summary: dict):
        """
        Update file record with generated summary
        """
        try:
            file = self.file_repository.get_file(file_id)
            if file:
                file.detail_summary = json.dumps(file_summary)
                self.db.commit()
                print(f"💾 Saved summary for file {file_id}")
        except Exception as e:
            print(f"Error updating file summary: {e}")
            self.db.rollback()
    
    def _enhance_user_prompt(self, user_input: str, file_summaries: list, context_info: dict):
        input_data = {
            "original_user_prompt": user_input,
            "file_summaries": file_summaries
        }
        
        if context_info:
            input_data["context_information"] = context_info
        
        result = self.agent_service.run_agent("enhanced_user_prompt_agent", input_data)
        return result["enhanced_prompt"]
    
    def _generate_analytics_query(self, original_input: str, enhanced_prompt: dict, file_summaries: list):
        input_data = {
            "original_user_input": original_input,
            "enhanced_user_prompt": enhanced_prompt,
            "file_summaries": file_summaries,
            "previous_queries": [],
            "analysis_context": {
                "analysis_goal": "exploration",
                "constraints": {"max_rows": 100}
            }
        }
        
        return self.agent_service.run_agent("analytics_agent", input_data)
    
    def _execute_query(self, query: str):
        return self.query_service.query(query) 

    def _get_detailed_column_info(self, columns: list, sample_data: list):
        """
        Analyze columns and their actual data types based on sample values
        """
        column_details = []
        for col in columns:
            # Analyze sample values for this column
            values = [row.get(col) for row in sample_data if row.get(col) is not None]
            
            detail = {
                "name": col,
                "actual_type": self._infer_actual_data_type(values),
                "has_nulls": any(row.get(col) is None or row.get(col) == '' for row in sample_data),
                "unique_values": len(set(str(v) for v in values if v is not None)) if values else 0,
                "description": self._generate_column_description(col, values)
            }
            column_details.append(detail)
        
        return column_details
    
    def _infer_actual_data_type(self, values: list):
        """
        Infer the actual data type based on sample values
        """
        if not values:
            return "Empty"
        
        # Check if all values are numeric
        try:
            numeric_values = [float(v) for v in values if str(v).replace('.', '').replace('-', '').isdigit()]
            if len(numeric_values) > len(values) * 0.8:  # 80% numeric
                return "Numeric"
        except:
            pass
        
        # Check for date patterns
        date_patterns = ['2015-', '2024-', '2025-', 'T', 'Z']
        if any(pattern in str(v) for v in values[:5] for pattern in date_patterns):
            return "DateTime"
        
        # Check for categorical data (limited unique values)
        unique_count = len(set(str(v) for v in values))
        if unique_count <= 10 and len(values) > 10:
            return "Categorical"
        
        # Check for ID patterns
        if any('id' in str(values[0]).lower() if values else False for _ in [1]):
            return "Identifier"
        
        return "Text"
    
    def _generate_column_description(self, column_name: str, values: list):
        """
        Generate a description for the column based on name and values
        """
        col_lower = column_name.lower()
        
        if 'id' in col_lower:
            return f"Unique identifier for {col_lower.replace('_id', '').replace('id_', '')}"
        elif any(word in col_lower for word in ['time', 'date', 'created', 'updated']):
            return f"Timestamp or date information for {col_lower.replace('_', ' ')}"
        elif any(word in col_lower for word in ['category', 'type', 'status']):
            unique_vals = list(set(str(v) for v in values[:10] if v))[:3]
            return f"Category field with values like: {', '.join(unique_vals)}"
        elif any(word in col_lower for word in ['content', 'data', 'message']):
            return f"Text content or data field"
        elif any(word in col_lower for word in ['count', 'number', 'amount']):
            return f"Numeric field for {col_lower.replace('_', ' ')}"
        else:
            return f"Data field for {col_lower.replace('_', ' ')}"
    
    def _get_sample_values_per_column(self, columns: list, sample_data: list):
        """
        Get sample values for each column to help AI understand the data
        """
        sample_values = {}
        for col in columns:
            values = []
            for row in sample_data[:5]:  # First 5 rows
                val = row.get(col)
                if val is not None and val != '':
                    # Truncate long values
                    val_str = str(val)
                    if len(val_str) > 50:
                        val_str = val_str[:50] + "..."
                    values.append(val_str)
                if len(values) >= 3:  # Max 3 sample values per column
                    break
            sample_values[col] = values
        return sample_values
    
    def _enhance_fallback_with_schema(self, fallback_summary: dict, table_name: str, columns: list, sample_data: list):
        """
        Enhance fallback summary with accurate schema information
        """
        enhanced_summary = fallback_summary.copy()
        enhanced_summary["database_schema"] = {
            "table_name": table_name,
            "available_columns": columns,
            "column_details": self._get_detailed_column_info(columns, sample_data),
            "sample_values": self._get_sample_values_per_column(columns, sample_data)
        }
        
        # Update the data structure with actual column info
        enhanced_summary["data_structure"]["key_columns"] = [
            {
                "name": col,
                "inferred_type": self._infer_column_type(col, sample_data),
                "description": self._generate_column_description(col, [row.get(col) for row in sample_data])
            }
            for col in columns[:10]  # First 10 columns
        ]
        
        return enhanced_summary 