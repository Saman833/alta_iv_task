# Research-Based Analytics Agent Example

## 🔍 How the Research-Based Approach Works

The analytics agent now works like a **database researcher** who:

1. **Analyzes what it already knows** from previous queries
2. **Examines metadata and summaries** to understand data structure
3. **Identifies knowledge gaps** - what specific information it still needs
4. **Reasons about additional queries** needed to find missing information
5. **Documents research process** and findings

## 📊 Example Research Process

### **User Question**: "Which product shows high growth and a high share of total sales?"

### **Step 1: Research Analysis**
```json
{
  "research_analysis": {
    "user_question_understanding": "User wants to identify products that have both high growth rates and high market share",
    "current_knowledge": "From previous queries, I know we have sales data with product information, but I need to find growth rates and market share calculations",
    "knowledge_gaps": [
      "Need to find product growth rates over time",
      "Need to calculate market share percentages",
      "Need to identify which products have both high growth AND high share"
    ],
    "research_strategy": "First explore sales data structure, then calculate growth rates and market shares, finally identify products meeting both criteria",
    "expected_outcome": "A list of products with both high growth rates and high market share, with supporting data"
  }
}
```

### **Step 2: Research Queries**
```json
{
  "queries_to_execute": [
    {
      "query": "SELECT COUNT(*) as total_products, COUNT(DISTINCT product_name) as unique_products FROM sales_data",
      "query_purpose": "Understand the scope of product data available",
      "query_rationale": "I need to know how many products we have and if there are duplicates before calculating growth and share",
      "expected_findings": ["Total number of products", "Whether product names are unique"],
      "execution_order": 1,
      "research_phase": "data_exploration"
    },
    {
      "query": "SELECT product_name, SUM(sales_amount) as total_sales, COUNT(*) as sales_count FROM sales_data GROUP BY product_name ORDER BY total_sales DESC LIMIT 10",
      "query_purpose": "Find top products by total sales to understand market share",
      "query_rationale": "Based on previous query showing we have sales data, I need to calculate total sales per product to determine market share",
      "expected_findings": ["Top 10 products by sales volume", "Sales distribution across products"],
      "execution_order": 2,
      "research_phase": "targeted_research"
    },
    {
      "query": "SELECT product_name, DATE(sale_date) as sale_date, SUM(sales_amount) as daily_sales FROM sales_data WHERE sale_date >= date('now', '-90 days') GROUP BY product_name, DATE(sale_date) ORDER BY product_name, sale_date",
      "query_purpose": "Calculate growth rates by analyzing sales trends over time",
      "query_rationale": "I need time-series data to calculate growth rates. Using last 90 days to get meaningful trend data",
      "expected_findings": ["Daily sales trends for each product", "Data to calculate growth rates"],
      "execution_order": 3,
      "research_phase": "targeted_research"
    },
    {
      "query": "WITH product_metrics AS (SELECT product_name, SUM(sales_amount) as total_sales, (SELECT SUM(sales_amount) FROM sales_data) as market_total FROM sales_data GROUP BY product_name) SELECT product_name, total_sales, ROUND((total_sales * 100.0 / market_total), 2) as market_share FROM product_metrics ORDER BY market_share DESC LIMIT 10",
      "query_purpose": "Calculate market share percentages for all products",
      "query_rationale": "Now I can calculate market share by dividing each product's sales by total market sales",
      "expected_findings": ["Market share percentages for top products", "Products with highest market share"],
      "execution_order": 4,
      "research_phase": "targeted_research"
    },
    {
      "query": "WITH growth_rates AS (SELECT product_name, AVG(daily_change) as avg_growth FROM (SELECT product_name, (daily_sales - LAG(daily_sales) OVER (PARTITION BY product_name ORDER BY sale_date)) as daily_change FROM (SELECT product_name, DATE(sale_date) as sale_date, SUM(sales_amount) as daily_sales FROM sales_data WHERE sale_date >= date('now', '-30 days') GROUP BY product_name, DATE(sale_date))) WHERE daily_change IS NOT NULL GROUP BY product_name), market_shares AS (SELECT product_name, ROUND((total_sales * 100.0 / (SELECT SUM(sales_amount) FROM sales_data)), 2) as market_share FROM (SELECT product_name, SUM(sales_amount) as total_sales FROM sales_data GROUP BY product_name)) SELECT g.product_name, g.avg_growth, m.market_share FROM growth_rates g JOIN market_shares m ON g.product_name = m.product_name WHERE g.avg_growth > 0 AND m.market_share > 5 ORDER BY g.avg_growth DESC, m.market_share DESC",
      "query_purpose": "Find products with both high growth and high market share",
      "query_rationale": "Now I can combine growth rates and market shares to find products meeting both criteria - high growth (>0) and high market share (>5%)",
      "expected_findings": ["Products with both high growth and high market share", "Final answer to user's question"],
      "execution_order": 5,
      "research_phase": "comprehensive_analysis"
    }
  ]
}
```

### **Step 3: Research Documentation**
```json
{
  "comprehensive_research": {
    "research_summary": "Conducted systematic database research to find products with both high growth and high market share",
    "research_questions": [
      "What products exist in the database?",
      "What are the total sales for each product?",
      "How do sales trends change over time?",
      "What are the market share percentages?",
      "Which products have both high growth and high share?"
    ],
    "research_requirements": [
      "Explored data structure and scope",
      "Calculated total sales per product",
      "Analyzed sales trends over time",
      "Computed market share percentages",
      "Combined growth and share metrics"
    ],
    "expected_comprehensive_answer": "A ranked list of products that have both high growth rates and high market share, with supporting metrics and trends"
  }
}
```

## 🎯 Key Research Principles

### **1. Analyze Previous Knowledge**
- "From previous queries, I know we have sales data..."
- "Based on the data structure I found..."
- "Given what I learned about product categories..."

### **2. Identify Knowledge Gaps**
- "I need to find growth rates over time"
- "I still need to calculate market share percentages"
- "I need to identify which products meet both criteria"

### **3. Reason About Additional Queries**
- "I need time-series data to calculate growth rates"
- "I need to divide each product's sales by total market sales"
- "I need to combine growth rates and market shares"

### **4. Document Research Process**
- "Query 1: Understanding data scope"
- "Query 2: Calculating total sales per product"
- "Query 3: Analyzing sales trends over time"
- "Query 4: Computing market share percentages"
- "Query 5: Finding products with both high growth and high share"

## 🌍 Multilingual Support

### **English Query**: "Which product shows high growth and a high share of total sales?"
### **Russian Query**: "Какой продукт показывает высокий рост и высокую долю общих продаж?"

The agent conducts the same research process regardless of language!

## 🔍 Research Phases

1. **Research Planning**: Analyze what you know and what you need to find
2. **Data Exploration**: Understand data structure and scope
3. **Targeted Research**: Find specific information based on gaps
4. **Validation Research**: Confirm findings and fill remaining gaps
5. **Comprehensive Analysis**: Synthesize all research into final answer

This research-based approach ensures the agent conducts thorough database investigation to provide complete, accurate answers! 