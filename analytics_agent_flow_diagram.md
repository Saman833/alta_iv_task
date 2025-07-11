# Analytics Agent Flow and Loop Diagram

## 🔄 Complete Analytics Pipeline Flow

```
User Input → Enhanced User Prompt Agent → Analytics Agent → Query Execution → Question Answering Agent → Final Response Agent
```

## 📍 Agent Call Locations

### 1. **Enhanced User Prompt Agent** 
**Location**: `services/analytics_service.py` line 373-384
```python
def _enhance_user_prompt(self, user_input: str, file_summaries: list, context_info: dict):
    input_data = {
        "original_user_prompt": user_input,
        "file_summaries": file_summaries
    }
    
    if context_info:
        input_data["context_information"] = context_info
    
    result = self.agent_service.run_agent("enhanced_user_prompt_agent", input_data)
    return result["enhanced_prompt"]
```

### 2. **Analytics Agent**
**Location**: `services/analytics_service.py` line 385-398
```python
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
```

### 3. **File Summary Agent**
**Location**: `services/analytics_service.py` line 123-176
```python
# Call file_summary_agent
summary_response = self.agent_service.run_agent("file_summary_agent", agent_input)
```

### 4. **Question Answering Agent**
**Location**: `services/question_answering_service.py` line 45-66
```python
# Call the question answering agent
agent_response = self.agent_service.run_agent(
    agent_name="question_answering_agent",
    input_data=agent_input
)
```

### 5. **Final Response Agent** (NEW)
**Location**: To be integrated in the pipeline
```python
# This will be called after question answering to synthesize final response
final_response = self.agent_service.run_agent("final_response_agent", {
    "original_user_question": user_input,
    "analytics_work": analytics_data,
    "question_analysis": qa_results
})
```

## 🔄 Iterative Analytics Loop

### **IterativeAnalyticsService** (`services/iterative_analytics_service.py`)

#### Loop Structure:
```python
# 1. Start Conversation
result = analytics_service.start_analytics_conversation(user_input)

# 2. Continue Loop
for iteration in range(max_iterations):
    result = analytics_service.continue_analytics_conversation(follow_up_input)
    
    # Store query in history
    self._add_sql_query_to_history(query, result, purpose)
    
    # Update conversation context
    self.conversation_context["total_queries"] += 1
```

#### Agent Calls in Loop:
1. **Enhanced User Prompt Agent** (line 150-160)
2. **Analytics Agent** (line 162-196)

## 📊 Complete Pipeline Examples

### **Single Analytics Request** (`run_complete_analytics.py`)
```python
# 1. Enhanced User Prompt Agent
enhanced_prompt = self._enhance_user_prompt(user_input, file_summaries, context_info)

# 2. Analytics Agent  
query_response = self._generate_analytics_query(user_input, enhanced_prompt, file_summaries)

# 3. Execute Query
query_result = self._execute_query(query_response["analysis_response"]["query"])
```

### **Iterative Analytics** (`complete_pipeline.py`)
```python
# Step 1: Run Analytics
result1 = analytics_service.start_analytics_conversation(user_input)
result2 = analytics_service.continue_analytics_conversation("Show me detailed breakdowns")
result3 = analytics_service.continue_analytics_conversation("What are the key insights?")

# Step 2: Question Answering
qa_results = qa_service.answer_multiple_questions(client_questions, analytics_data)

# Step 3: Final Response (NEW)
final_response = final_response_service.synthesize_response(user_input, analytics_data, qa_results)
```

## 🎯 Agent Input/Output Flow

### **Enhanced User Prompt Agent**
- **Input**: `{"original_user_prompt": str, "file_summaries": list}`
- **Output**: `{"enhanced_prompt": dict}`

### **Analytics Agent** 
- **Input**: `{"original_user_input": str, "enhanced_user_prompt": dict, "file_summaries": list, "previous_queries": list}`
- **Output**: `{"analysis_response": {"query": str, "query_purpose": str, "anticipated_next_steps": list}}`

### **Question Answering Agent**
- **Input**: `{"client_question": str, "analytics_history": list, "file_summaries": list}`
- **Output**: `{"answer_response": {"direct_answer": str, "supporting_evidence": list, "confidence_level": str}}`

### **Final Response Agent** (NEW)
- **Input**: `{"original_user_question": str, "analytics_work": dict, "question_analysis": dict}`
- **Output**: `{"final_response": {"executive_summary": str, "actionable_recommendations": list, "next_steps": dict}}`

## 🔧 Integration Points

### **Main Entry Points**:
1. **API Route**: `routes/analytics_router.py` → `AnalyticsService.analyze_user_request()`
2. **Demo Scripts**: `run_complete_analytics.py`, `complete_pipeline.py`
3. **Autonomous Analytics**: `demo_autonomous_analytics.py`

### **Agent Service** (`services/agent_service.py`):
- **Central Hub**: All agent calls go through `AgentService.run_agent()`
- **Agent Management**: Handles prompt creation, API calls, response parsing
- **Error Handling**: Provides fallbacks when agents fail

## 🚀 Next Steps for Final Response Agent Integration

1. **Add to Analytics Service**:
```python
def synthesize_final_response(self, user_input: str, analytics_data: dict, qa_results: dict):
    return self.agent_service.run_agent("final_response_agent", {
        "original_user_question": user_input,
        "analytics_work": analytics_data,
        "question_analysis": qa_results
    })
```

2. **Update Pipeline**:
```python
# After question answering
final_response = analytics_service.synthesize_final_response(user_input, analytics_data, qa_results)
```

3. **Add to API Routes**:
```python
@router.post("/synthesize")
async def synthesize_response(request: SynthesisRequest, db: SessionDep):
    return analytics_service.synthesize_final_response(request.user_input, request.analytics_data, request.qa_results)
```

This shows the complete flow of where agents are called in the analytics pipeline and loop! 