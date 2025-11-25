# Skill Taxonomy Pipeline

A comprehensive pipeline for building hierarchical skill taxonomies from large datasets (200K+ skills) using embeddings, clustering, and LLM refinement.

## Features

- **Scalable Processing**: Handles 200K+ skills efficiently using batch processing and caching
- **Embedding-based Deduplication**: Uses sentence transformers and FAISS for similarity-based deduplication
- **Hierarchical Clustering**: HDBSCAN with UMAP for meaningful skill grouping at scale
- **LLM Integration**: Optional OpenAI integration for intelligent naming and validation
- **Multi-level Taxonomy**: Creates 4-5 level hierarchical structure automatically
- **Quality Metrics**: Built-in validation and quality assessment

## Quick Start

### 1. Installation

```bash
# Clone or download the project
cd skill_taxonomy_pipeline

# Run setup
python setup.py

# Or manually install dependencies
pip install -r requirements.txt
```

### 2. Prepare Your Data

Your input DataFrame should have these columns:
- `name`: Skill name
- `code`: Unit/skill code  
- `description`: Skill description
- `category`: One of (technical, cognitive, interpersonal, domain knowledge)
- `level`: Skill level
- `context`: One of (practical, theoretical, hybrid)
- `keywords`: List of keywords
- `confidence`: Confidence score (0-1)
- `evidence`: Source text

### 3. Run the Pipeline

```python
import pandas as pd
from main import SkillTaxonomyPipeline

# Load your data
df = pd.read_csv('your_skills.csv')

# Initialize and run pipeline
pipeline = SkillTaxonomyPipeline()
results = pipeline.run(df, output_dir='output')
```

Or use command line:

```bash
python main.py your_skills.csv -o output_directory
```

## Configuration

Key parameters in `config/settings.py`:

```python
# For 200K skills, recommended settings:
DATA_CONFIG = {
    "confidence_threshold": 0.7,
    "batch_size": 1000,
}

EMBEDDING_CONFIG = {
    "model_name": "sentence-transformers/all-mpnet-base-v2",
    "batch_size": 512,  # Increase for GPU
}

CLUSTERING_CONFIG = {
    "min_cluster_size": 50,  # Adjust based on data
    "use_umap_reduction": True,  # Essential for 200K skills
}
```

## Pipeline Steps

1. **Data Processing** (~5-10 min)
   - Cleans and standardizes skill data
   - Filters by confidence threshold
   - Creates unique identifiers

2. **Embedding Generation** (~20-40 min CPU / 5-10 min GPU)
   - Generates semantic embeddings for each skill
   - Caches results for reuse

3. **Deduplication** (~10-20 min)
   - Identifies similar skills using FAISS
   - Merges duplicates intelligently

4. **Clustering** (~15-30 min)
   - Performs HDBSCAN clustering within categories
   - Creates meaningful skill groups

5. **LLM Refinement** (~30-60 min, optional)
   - Generates meaningful cluster names
   - Validates taxonomy structure
   - Suggests improvements

6. **Taxonomy Building** (~5-10 min)
   - Creates hierarchical structure
   - Balances tree for usability
   - Adds metadata

7. **Export** (~1 min)
   - Saves multiple output formats
   - Generates quality reports

## Output Files

```
output/
├── processed_skills.csv       # Cleaned data
├── deduplicated_skills.csv    # After deduplication
├── clustered_skills.csv       # With cluster assignments
├── taxonomy/
│   ├── taxonomy.json          # Hierarchical structure
│   ├── taxonomy_flat.csv      # Flattened for analysis
│   └── taxonomy.pkl           # Python object
├── cluster_representatives.json
├── clustering_metrics.json
└── pipeline_report.json
```

## Performance Tips for 200K Skills

### Memory Management
- Process runs in ~16-32GB RAM
- Use GPU if available (set CUDA_AVAILABLE=1)
- Increase swap if needed

### Speed Optimization
```python
# Adjust batch sizes
config['embedding']['batch_size'] = 1024  # For GPU
config['clustering']['min_cluster_size'] = 100  # Fewer, larger clusters
```

### Quality vs Speed Tradeoffs
- Reduce UMAP components: `umap_n_components = 30` (faster, less accurate)
- Increase similarity threshold: `similarity_threshold = 0.90` (more aggressive dedup)
- Limit LLM calls: Process samples only

## Expected Runtime

For 200K skills:
- **CPU Only**: 1.5-3 hours total
- **With GPU**: 1-2 hours total
- **With LLM**: Add 30-60 minutes

## Using the Generated Taxonomy

```python
import json
import pandas as pd

# Load taxonomy
with open('output/taxonomy/taxonomy.json', 'r') as f:
    taxonomy = json.load(f)

# Load flat structure for analysis
flat = pd.read_csv('output/taxonomy/taxonomy_flat.csv')

# Access clustered skills
skills = pd.read_csv('output/clustered_skills.csv')
```

## Troubleshooting

### Out of Memory
- Reduce batch sizes
- Enable disk caching
- Process categories separately

### Slow Processing
- Use GPU for embeddings
- Increase batch sizes
- Skip LLM refinement initially

### Poor Clustering
- Adjust min_cluster_size
- Try different UMAP parameters
- Check data quality

## Architecture

```
Pipeline Architecture:
┌─────────────┐
│   Raw Data  │ (200K skills DataFrame)
└──────┬──────┘
       │
┌──────▼──────┐
│ Processing  │ → Clean, validate, standardize
└──────┬──────┘
       │
┌──────▼──────┐
│ Embeddings  │ → Semantic vectors (768-dim)
└──────┬──────┘
       │
┌──────▼──────┐
│Deduplication│ → FAISS similarity search
└──────┬──────┘
       │
┌──────▼──────┐
│ Clustering  │ → HDBSCAN + UMAP
└──────┬──────┘
       │
┌──────▼──────┐
│LLM Refine   │ → OpenAI naming/validation
└──────┬──────┘
       │
┌──────▼──────┐
│  Taxonomy   │ → Hierarchical structure
└──────┬──────┘
       │
┌──────▼──────┐
│   Output    │ → JSON, CSV, Reports
└─────────────┘
```

## Requirements

- Python 3.8+
- 16GB+ RAM (32GB recommended for 200K skills)
- OpenAI API key (optional, for LLM features)
- CUDA-capable GPU (optional, for faster processing)

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check the logs in `taxonomy_pipeline.log`
2. Review the validation report in output
3. Adjust configuration parameters as needed

## Citation

If you use this pipeline in your research, please cite:
```
Skill Taxonomy Pipeline (2024)
A scalable approach to building hierarchical skill taxonomies
```
