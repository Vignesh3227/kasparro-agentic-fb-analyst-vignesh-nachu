# Agentic Facebook Performance Analyst

A multi-agent system that autonomously diagnoses Facebook Ads performance, identifies ROAS fluctuation drivers, and recommends new creative strategies using quantitative analysis and creative messaging insights.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER QUERY INPUT                            │
│            "Analyze why ROAS declined..."                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
        ╔════════════════════════════════════════════╗
        │   PLANNER AGENT (Query Decomposition)    │
        ║  Breaks query into subtasks              ║
        ║  Defines data requirements               ║
        ║  Sets success criteria                   ║
        ╚════════════════════════════════════════════╝
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
    ╔══════════╗    ╔═════════════╗    ╔═══════════════╗
    │  DATA    │    │   INSIGHT   │    │   EVALUATOR   │
    │ AGENT    │───▶│   AGENT     │───▶│    AGENT      │
    ╚══════════╝    ╚═════════════╝    ╚═══════════════╝
    Loads CSV       Generates 3-5     Validates with
    Aggregates      Hypotheses        Confidence
    Summarizes      (Marketing        Scores
                     Drivers)
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
    ╔═══════════════════════╗    ╔════════════════════════╗
    │ CREATIVE GENERATOR    │    │ REPORT COMPILER        │
    │ AGENT                 │    │                        │
    ║ Finds low-CTR Ads     ║    ║ Combines all insights  ║
    ║ Analyzes Winners      ║    ║ Generates MD Report    ║
    ║ Recommends Messages   ║    ║ Saves JSON outputs     ║
    ╚═══════════════════════╝    ╚════════════════════════╝
                                         │
                                         ▼
                    ┌────────────────────────────────┐
                    │ STRUCTURED OUTPUTS             │
                    ├────────────────────────────────┤
                    │ • insights.json                │
                    │ • creatives.json               │
                    │ • report.md                    │
                    │ • logs/ (execution traces)     │
                    └────────────────────────────────┘
```

## 📊 Data Flow

1. **Planner**: Decomposes user query into 3-4 atomic subtasks
2. **Data Agent**: Loads dataset, generates summaries by campaign/creative/audience
3. **Insight Agent**: Generates marketing-grounded hypotheses (audience fatigue, creative decay, etc.)
4. **Evaluator Agent**: Validates hypotheses with >0.6 confidence using statistical evidence
5. **Creative Generator**: Creates new messaging for low-CTR campaigns based on winners
6. **Report**: Compiles findings into actionable markdown + JSON outputs

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Google Generative AI API Key

### Installation

```bash
# Clone repository
git clone https://github.com/Vignesh3227/kasparro-agentic-fb-analyst-vignesh-nachu.git
cd kasparro-agentic-fb-analyst-vignesh-nachu

# Install dependencies
pip install -r requirements.txt

# Set API key
export GOOGLE_API_KEY="your_api_key_here"
```

### Basic Usage

```bash
# Run analysis with default query
python run.py

# Run with custom query
python run.py "Why did ROAS drop 30% in January?"

# Run with sample data (default)
python run.py "Analyze CTR performance by creative type"

# Check config for sample mode
# config/config.yaml: data.sample_mode = true (uses first 100 rows)
```

## 📁 Project Structure

```
kasparro-agentic-fb-analyst-vignesh-nachu/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── run.py                             # Main entry point
├── config/
│   └── config.yaml                    # Configuration (model, thresholds, paths)
├── data/
│   ├── README                         # Dataset documentation
│   └── synthetic_fb_ads_undergarments.csv  # Sample dataset
├── prompts/
│   ├── planner.md                     # Planner agent prompt
│   ├── data_agent.md                  # Data agent prompt
│   ├── insight_agent.md               # Insight agent prompt
│   ├── evaluator.md                   # Evaluator agent prompt
│   └── creative_generator.md          # Creative generator prompt
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py                    # Base agent class + LLM client
│   │   ├── planner.py                 # Planner agent implementation
│   │   ├── data_agent.py              # Data loading & analysis
│   │   ├── insight_agent.py           # Hypothesis generation
│   │   ├── evaluator.py               # Hypothesis validation
│   │   └── creative_generator.py      # Creative recommendations
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   └── runner.py                  # Agent orchestration pipeline
│   └── utils/
│       ├── __init__.py
│       ├── logging.py                 # Structured JSON logging
│       ├── config.py                  # Configuration loader
│       └── data.py                    # Data utilities
├── reports/
│   ├── insights.json                  # Generated hypotheses + validation
│   ├── creatives.json                 # Generated creative recommendations
│   └── report.md                      # Executive summary report
└── logs/
    └── agentic_analyst_*.jsonl        # Execution traces
```

## 🔧 Configuration

Edit `config/config.yaml` to customize:

```yaml
# Model Configuration
model:
  name: "gemini-2.0-flash"             # LLM model
  temperature: 0.7                     # Model creativity (0-1)
  max_tokens: 2048                     # Max response length

# Data Configuration
data:
  dataset_path: "data/synthetic_fb_ads_undergarments.csv"
  sample_mode: true                    # Use sample or full dataset
  sample_size: 100                     # Rows for sample mode

# Agent Configuration
agents:
  planner:
    temperature: 0.3                   # Lower = more structured
  insight_agent:
    min_confidence: 0.6                # Confidence threshold for hypotheses
  evaluator:
    confidence_threshold: 0.6          # Only report confident findings

# Thresholds
thresholds:
  roas_drop_threshold: 0.2             # 20% = significant drop
  ctr_low_threshold: 0.012             # CTR below 1.2% = low performer
  confidence_high: 0.8                 # High confidence threshold
```

## 📊 Example Outputs

### insights.json

```json
{
  "query_summary": "Analyze why ROAS declined",
  "hypotheses": [
    {
      "id": "h1",
      "title": "Audience Fatigue",
      "description": "Repeated exposure leads to CTR/ROAS decline",
      "confidence": 0.75,
      "testable_prediction": "CTR decreases after day 14"
    }
  ],
  "priority_ranking": [...],
  "recommended_validations": [...]
}
```

### creatives.json

```json
[
  {
    "low_performer_analysis": {
      "campaign_name": "Men ComfortMax Launch",
      "current_ctr": 0.0108,
      "current_messaging": "Original ad copy"
    },
    "creative_recommendations": [
      {
        "id": "rec_1",
        "headline": "No ride-up guarantee or money back",
        "value_prop": "Problem-solution with guarantee",
        "predicted_lift": "20-30%"
      }
    ]
  }
]
```

### report.md

**Executive summary** with:
- Key findings from validated hypotheses
- Recommended actions
- Creative recommendations by campaign
- Execution metadata

## 🧪 Validation & Robustness

### Hypothesis Validation

Each hypothesis is evaluated using:

- **Trend Analysis**: ROAS/CTR changes over time
- **Segment Comparison**: Performance across audience types, creative formats
- **Correlation Analysis**: Spend vs ROAS, audience age vs CTR
- **Cohort Analysis**: Early vs late period performance

### Confidence Scoring

- **0.9-1.0**: Strong statistical evidence across multiple metrics
- **0.7-0.9**: Clear trend with supporting evidence
- **0.5-0.7**: Some evidence, alternative explanations possible
- **<0.5**: Insufficient evidence, more data needed

### Error Handling & Retry Logic

- LLM responses validated against expected JSON schema
- Fallback templates when LLM JSON generation fails
- Configurable retry attempts with exponential backoff
- Structured error logging for debugging

## 🏃 Running the System

### Basic Execution

```bash
# Run with default query
python run.py

# Sample output:
# ╔═══════════════════════════════════════════════════════════╗
# ║   Agentic Facebook Performance Analyst                    ║
# ║   Multi-Agent System for Ad Performance Diagnosis         ║
# ╚═══════════════════════════════════════════════════════════╝
#
# 📋 Step 1: Planning Analysis...
# ✓ Plan created with 4 subtasks
# 
# 📊 Step 2: Loading and Analyzing Data...
# ✓ Data loaded: 100 records
# 
# 💡 Step 3: Generating Hypotheses...
# ✓ Generated 4 hypotheses
# 
# ✅ Step 4: Validating Hypotheses...
# ✓ Validation complete
# 
# 🎨 Step 5: Generating Creative Recommendations...
# ✓ Generated 3 creative recommendations
# 
# 📄 Step 6: Compiling Report...
# ✓ Saved insights to reports/insights.json
# ✓ Saved creatives to reports/creatives.json
# ✓ Saved report to reports/report.md
# 
# ✨ Analysis Complete!
```

### Custom Queries

```bash
# ROAS analysis
python run.py "Why did ROAS drop 25% between Jan and Feb?"

# CTR optimization
python run.py "Identify why video creatives have low CTR and recommend improvements"

# Audience analysis
python run.py "Compare performance across audience types and recommend targeting strategy"

# Holistic diagnosis
python run.py "Provide complete diagnosis of ad performance and strategic recommendations"
```

## 📈 Key Features

### 1. Multi-Agent Reasoning

- **Planner**: Decomposes ambiguous questions into structured analysis
- **Data Agent**: Aggregates metrics intelligently without loading full CSVs
- **Insight Agent**: Generates marketing-grounded hypotheses (not just correlations)
- **Evaluator**: Validates with statistical rigor and confidence scoring
- **Creative Generator**: Mines existing data for winning patterns

### 2. Structured Prompts

Each agent has a `.md` prompt file with:

- Clear role definition
- Output JSON schema specification
- Reasoning framework (Think → Analyze → Conclude)
- Quality standards and examples

### 3. Confidence-Based Analysis

- Every hypothesis has 0.0-1.0 confidence score
- Validation captures supporting/contradicting evidence
- Actions recommended only for >0.6 confidence findings
- Clear documentation of limitations

### 4. Observability & Logs

- Structured JSON logging of all agent executions
- Optional Langfuse integration for traces
- Execution history in reports
- Full debugging trail in logs/

## 🎯 Analysis Framework

### Problem Types Handled

1. **ROAS Fluctuation**
   - Audience fatigue hypothesis
   - Creative decay analysis
   - Budget pacing effects
   - Seasonal trends

2. **CTR Optimization**
   - Messaging relevance
   - Creative format differences
   - Audience-creative fit
   - Urgency/CTA effectiveness

3. **Audience Strategy**
   - Broad vs Lookalike performance
   - Interest-based targeting
   - Geographic variations
   - Platform differences (FB vs IG)

4. **Creative Performance**
   - Type variations (Image/Video/UGC/Carousel)
   - Messaging patterns (benefits, CTAs, urgency)
   - Lifestyle vs problem-solution angles
   - Social proof vs scarcity elements

## 📝 Prompt Design Philosophy

Prompts follow a three-part structure:

1. **Role Definition**: Clear agent responsibilities
2. **Framework**: Thinking process (analysis steps)
3. **Output Format**: Exact JSON schema with examples

Example:

```markdown
# Agent Name

## Your Responsibilities
1. First responsibility
2. Second responsibility

## Analysis Framework
- Step 1: ...
- Step 2: ...

## Output Format
```json
{
  "required_field": "description",
  "another_field": "value"
}
```
```

This ensures:
- Reproducible LLM outputs
- Parseable JSON responses
- Reasoning transparency
- Reusable prompt templates

## 🔄 Iterative Learning (Optional)

System can maintain short-term memory of insights across runs:

```python
# Future enhancement: cross-run learning
# - Store validated hypotheses in memory bank
# - Increase confidence for repeated findings
# - Track recommendation outcomes
```

## 🐛 Troubleshooting

### API Key Issues

```bash
# Verify API key is set
echo $GOOGLE_API_KEY

# Set if needed
export GOOGLE_API_KEY="your_key_here"
```

### Data Loading Errors

```bash
# Check dataset path in config/config.yaml
# Verify CSV exists at: data/synthetic_fb_ads_undergarments.csv
# Ensure columns match expected schema
```

### LLM Response Failures

```bash
# Check logs in logs/ directory
# Review JSON parsing errors
# System falls back to template responses
# Lower max_tokens if timeouts occur
```

## 🚦 Output Validation

All outputs are validated:

- ✅ `insights.json`: Hypothesis structure verified
- ✅ `creatives.json`: Recommendation format checked
- ✅ `report.md`: Markdown syntax validated
- ✅ `logs/`: JSON lines format confirmed

## 📚 Dataset Guide

See `data/README` for:
- Column descriptions
- Data quality notes
- Analysis considerations
- Key insights for testing

**Sample Data**: 100 rows of synthetic Facebook Ads data  
**Full Data Option**: Set `sample_mode: false` in config

## 🎓 Learning Resources

### Agentic AI Concepts

This system demonstrates:
- Multi-agent decomposition
- Tool-using agents
- Reflection and validation loops
- Confidence-based decision making
- Structured reasoning output

### Marketing Analytics Concepts

- ROAS and CTR as key metrics
- Audience fatigue patterns
- Creative performance drivers
- Message-market fit analysis
- Statistical validation of hypotheses

## 📊 Execution Timeline

Typical analysis runtime: **2-5 minutes**

- Planner: ~30 seconds
- Data Loading: ~10 seconds
- Insight Generation: ~60 seconds
- Validation: ~60 seconds
- Creative Generation: ~90 seconds
- Report Compilation: ~10 seconds

## 🤝 Contributing

To extend the system:

1. Add new agent in `src/agents/`
2. Create prompt in `prompts/`
3. Register in `AgentOrchestrator.__init__()`
4. Define execution order in `execute()` method

## 📄 License

Project structure follows Kasparro AI Engineer assignment requirements.

## 📞 Support

For issues or questions:
- Check logs in `logs/` directory
- Review config in `config/config.yaml`
- Examine example outputs in `reports/`

---

**Built with**: Python 3.9+, Google Generative AI, Pandas, PyYAML  
**Architecture**: Multi-agent orchestration with LLM-powered reasoning
