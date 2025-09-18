# Credit Transfer Analysis System

A comprehensive Python system for analyzing credit transfer possibilities between VET (Vocational Education and Training) qualifications and University courses using advanced skill extraction and intelligent mapping.

## Features

- **Advanced Skill Extraction**: Uses both GenAI and pattern-based extraction to identify skills from course descriptions
- **Intelligent Skill Mapping**: Semantic similarity matching using embeddings
- **Edge Case Handling**: Comprehensive handling of special cases including:
  - Multiple VET units to single university course mapping
  - Single VET unit to multiple university courses
  - Practical vs theoretical content imbalance
  - Outdated technology/version mismatches
  - Composite skill decomposition
  - Prerequisite chain analysis
- **Multiple Report Formats**: JSON, HTML, CSV, and detailed text reports
- **Configurable Analysis**: Extensive configuration options for fine-tuning

## Installation

### Prerequisites

- Python 3.8+
- (Optional) Local GenAI model endpoint
- (Optional) Local embedding model or API

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd credit_transfer_system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables (optional):
```bash
export GENAI_ENDPOINT="http://localhost:8080"
export GENAI_API_KEY="your-api-key"
export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
```

## Usage

### Basic Usage

```bash
python main.py vet_data.json uni_data.json -o output/recommendations.json
```

### Advanced Usage

```bash
# Analyze specific courses only
python main.py vet_data.json uni_data.json -c COMP1234 COMP2345 -o output/analysis.json

# Generate HTML report
python main.py vet_data.json uni_data.json -f html -o output/report.html

# Use custom configuration
python main.py vet_data.json uni_data.json --config custom_config.json

# Verbose output
python main.py vet_data.json uni_data.json -v
```

### Command Line Options

- `vet_file`: Path to VET qualification JSON file
- `uni_file`: Path to university qualification JSON file
- `-o, --output`: Output file path (default: output/recommendations.json)
- `-f, --format`: Output format - json, html, csv, text (default: json)
- `-c, --courses`: Specific course codes to analyze
- `--config`: Path to configuration file
- `--save-config`: Save current configuration
- `-v, --verbose`: Enable verbose output

## Data Format

### VET Qualification Format

```json
{
  "code": "ICT50220",
  "name": "Diploma of Information Technology",
  "level": "Diploma",
  "units": [
    {
      "code": "ICTICT517",
      "name": "Match IT needs with the strategic direction",
      "description": "This unit covers...",
      "learning_outcomes": [
        "Identify organizational IT requirements",
        "Develop IT strategic plans"
      ],
      "assessment_requirements": "Assessment must include...",
      "nominal_hours": 60,
      "prerequisites": []
    }
  ]
}
```

### University Qualification Format

```json
{
  "code": "BIT",
  "name": "Bachelor of Information Technology",
  "courses": [
    {
      "code": "COMP1234",
      "name": "Introduction to Programming",
      "description": "This course introduces...",
      "year": 1,
      "learning_outcomes": [
        "Understand programming fundamentals",
        "Apply problem-solving techniques"
      ],
      "prerequisites": [],
      "credit_points": 6,
      "topics": [
        "Variables and data types",
        "Control structures"
      ],
      "assessment": "Exam 50%, Assignments 50%"
    }
  ]
}
```

## Configuration

Key configuration options in `config.py`:

- `MIN_ALIGNMENT_SCORE`: Minimum score for recommendations (default: 0.5)
- `MAX_UNIT_COMBINATION`: Maximum VET units in combination (default: 3)
- `SIMILARITY_THRESHOLD`: Threshold for direct skill matches (default: 0.8)
- `PARTIAL_THRESHOLD`: Threshold for partial matches (default: 0.6)

### Scoring Weights
- `COVERAGE_WEIGHT`: Weight for skill coverage (default: 0.4)
- `DEPTH_WEIGHT`: Weight for cognitive depth (default: 0.2)
- `CONTEXT_WEIGHT`: Weight for context alignment (default: 0.2)

## Output

### Recommendation Structure

Each recommendation includes:
- **VET Units**: Units being mapped
- **University Course**: Target course
- **Alignment Score**: Overall match quality (0-100%)
- **Confidence**: System confidence in recommendation
- **Recommendation Type**: Full, Conditional, Partial, or None
- **Skill Coverage**: Breakdown by skill category
- **Gaps**: Missing skills that need bridging
- **Conditions**: Requirements for credit transfer
- **Evidence**: Supporting evidence for the recommendation

### Report Types

1. **JSON**: Structured data for further processing
2. **HTML**: Interactive web report with visualizations
3. **CSV**: Spreadsheet-compatible format
4. **Text**: Detailed narrative report

## Architecture

```
├── models/              # Data models and enums
├── extraction/          # Skill extraction engine
├── mapping/            # Skill mapping and edge cases
├── analysis/           # Main analyzer
├── interfaces/         # GenAI and embedding interfaces
├── reporting/          # Report generation
└── utils/              # Utilities
```

## API Integration

### GenAI Integration

The system can integrate with local GenAI models for enhanced skill extraction:

```python
genai = GenAIInterface(
    model_endpoint="http://localhost:8080",
    api_key="your-api-key"
)
```

### Embedding Models

Supports both local and API-based embedding models:

```python
embeddings = EmbeddingInterface(
    model_path="sentence-transformers/all-MiniLM-L6-v2",
    use_api=False
)
```

## Edge Cases Handled

1. **Split-to-Single Mapping**: Multiple VET units → Single university course
2. **Single-to-Multiple**: Single VET unit → Multiple university courses
3. **Context Imbalance**: Practical vs theoretical content mismatch
4. **Outdated Content**: Technology version differences
5. **Depth vs Breadth**: Comprehensive vs focused skill coverage
6. **Composite Skills**: Breaking down complex skills
7. **Implicit Skills**: Inferring unstated requirements
8. **Version Mismatch**: Handling technology updates
9. **Prerequisite Chains**: Managing dependencies
10. **Credit Hour Alignment**: Nominal hours vs credit points

## Performance Considerations

- **Caching**: Extraction and mapping results are cached
- **Batch Processing**: Embeddings computed in batches
- **Parallel Processing**: Can be extended for parallel analysis
- **Memory Management**: Streaming for large datasets

## Troubleshooting

### Common Issues

1. **No embeddings available**: Install sentence-transformers or configure API
2. **GenAI timeout**: Increase GENAI_TIMEOUT or disable USE_GENAI
3. **Low confidence scores**: Review skill extraction quality
4. **No recommendations**: Lower MIN_ALIGNMENT_SCORE threshold

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Your License Here]

## Contact

[Your Contact Information]

## Acknowledgments

- Sentence Transformers for embedding models
- OpenAI/Anthropic for GenAI capabilities
- Educational institutions for qualification frameworks