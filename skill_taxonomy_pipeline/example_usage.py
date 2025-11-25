"""
Example usage of the Skill Taxonomy Pipeline
Demonstrates how to use the pipeline with a DataFrame input
"""
import pandas as pd
import numpy as np
import os
from pathlib import Path

# Add parent directory to path
import sys
sys.path.append(str(Path(__file__).parent))

from src.skill_taxonomy_pipeline import SkillTaxonomyPipeline
from config.settings import CONFIG


def prepare_sample_data():
    """
    Prepare sample data for demonstration
    In production, this would be your actual 200K skills DataFrame
    """
    # Example data structure matching your requirements
    sample_data = {
        'name': [
            'active listening questioning',
            'project management planning', 
            'python programming',
            'data analysis visualization',
            'team leadership coaching'
        ],
        'code': ['BSBCRT511', 'MGMT001', 'IT002', 'DATA003', 'LEAD004'],
        'description': [
            'Engages in discussions, actively listens and asks targeted questions',
            'Plans and manages projects using established methodologies',
            'Develops software applications using Python programming language',
            'Analyzes data and creates visualizations for insights',
            'Leads teams and provides coaching for performance improvement'
        ],
        'category': ['interpersonal', 'technical', 'technical', 'cognitive', 'interpersonal'],
        'level': ['ENSURE_ADVISE', 'APPLY', 'PERFORM', 'ANALYZE', 'LEAD'],
        'context': ['practical', 'hybrid', 'practical', 'theoretical', 'practical'],
        'keywords': [
            ['communication', 'listening', 'questioning'],
            ['planning', 'management', 'projects'],
            ['programming', 'python', 'development'],
            ['data', 'analysis', 'visualization'],
            ['leadership', 'coaching', 'teams']
        ],
        'confidence': [0.88, 0.92, 0.95, 0.90, 0.87],
        'evidence': [
            'Participates in verbal exchange and elicits views',
            'Manages project lifecycle from initiation to closure',
            'Writes clean and efficient Python code',
            'Transforms raw data into meaningful insights',
            'Guides team members towards achieving goals'
        ]
    }
    
    return pd.DataFrame(sample_data)


def run_pipeline_example():
    """
    Example of running the complete pipeline
    """
    print("="*80)
    print("SKILL TAXONOMY PIPELINE - EXAMPLE USAGE")
    print("="*80)
    
    # 1. Prepare your data
    print("\n1. Loading skill data...")
    # In production, load your actual data:
    # df = pd.read_csv('your_skills_file.csv')
    # or
    # df = pd.read_parquet('your_skills_file.parquet')
    
    # For this example, using sample data
    df = prepare_sample_data()
    print(f"   Loaded {len(df)} skills")
    
    # 2. Configure the pipeline (optional - uses defaults if not specified)
    print("\n2. Configuring pipeline...")
    
    # You can modify config as needed
    custom_config = CONFIG.copy()
    
    # Example: Adjust parameters for your data size
    if len(df) > 100000:
        custom_config['embedding']['batch_size'] = 512
        custom_config['clustering']['min_cluster_size'] = 50
    
    # Set OpenAI API key if available
    # custom_config['llm']['api_key'] = os.environ.get('OPENAI_API_KEY')
    
    # 3. Initialize the pipeline
    print("\n3. Initializing pipeline...")
    pipeline = SkillTaxonomyPipeline(custom_config)
    
    # 4. Run the pipeline
    print("\n4. Running pipeline...")
    print("   This will:")
    print("   - Process and clean the data")
    print("   - Generate embeddings for all skills")
    print("   - Deduplicate similar skills")
    print("   - Cluster skills hierarchically")
    print("   - Generate meaningful cluster names (using LLM if configured)")
    print("   - Build the hierarchical taxonomy")
    print("   - Validate and export results")
    
    results = pipeline.run(
        input_df=df,
        output_dir='output/example_run'
    )
    
    # 5. Check results
    print("\n5. Pipeline Results:")
    print("-"*40)
    if results['success']:
        print(f"✓ Success!")
        print(f"  - Input skills: {results['input_skills']}")
        print(f"  - Unique skills after dedup: {results['unique_skills']}")
        print(f"  - Number of clusters: {results['clusters']}")
        print(f"  - Taxonomy nodes: {results['taxonomy_nodes']}")
        print(f"  - Output directory: {results['output_dir']}")
        print(f"  - Total time: {results['total_time']/60:.2f} minutes")
    else:
        print(f"✗ Failed: {results['error']}")
    
    return results


def load_and_use_taxonomy():
    """
    Example of loading and using the generated taxonomy
    """
    print("\n" + "="*80)
    print("USING THE GENERATED TAXONOMY")
    print("="*80)
    
    output_dir = Path('output/example_run')
    
    # 1. Load the taxonomy JSON
    import json
    
    if (output_dir / 'taxonomy/taxonomy.json').exists():
        with open(output_dir / 'taxonomy/taxonomy.json', 'r') as f:
            taxonomy = json.load(f)
        
        print("\n1. Taxonomy Structure:")
        print(f"   Root: {taxonomy['name']}")
        print(f"   Total nodes: {count_nodes(taxonomy)}")
        print(f"   Max depth: {get_max_depth(taxonomy)}")
        
        # 2. Load the flat CSV for analysis
        flat_taxonomy = pd.read_csv(output_dir / 'taxonomy/taxonomy_flat.csv')
        
        print("\n2. Taxonomy Statistics:")
        print(f"   Categories: {flat_taxonomy[flat_taxonomy['type'] == 'category']['name'].tolist()}")
        print(f"   Average skills per cluster: {flat_taxonomy[flat_taxonomy['type'] == 'cluster']['num_skills'].mean():.1f}")
        
        # 3. Load clustered skills
        clustered_skills = pd.read_csv(output_dir / 'clustered_skills.csv')
        
        print("\n3. Skill Distribution:")
        print(clustered_skills['category'].value_counts())
        
    else:
        print("Taxonomy files not found. Run the pipeline first.")


def count_nodes(node):
    """Helper function to count nodes in taxonomy"""
    count = 1
    for child in node.get('children', []):
        count += count_nodes(child)
    return count


def get_max_depth(node, current_depth=0):
    """Helper function to get max depth of taxonomy"""
    if not node.get('children'):
        return current_depth
    
    max_child_depth = 0
    for child in node['children']:
        child_depth = get_max_depth(child, current_depth + 1)
        max_child_depth = max(max_child_depth, child_depth)
    
    return max_child_depth


def process_large_dataset_tips():
    """
    Tips for processing 200K skills efficiently
    """
    print("\n" + "="*80)
    print("TIPS FOR PROCESSING 200K SKILLS")
    print("="*80)
    
    print("""
    1. MEMORY MANAGEMENT:
       - Process in batches (already implemented)
       - Use dtype optimization in pandas
       - Clear cache periodically
    
    2. PERFORMANCE OPTIMIZATION:
       - Use GPU for embeddings if available (set CUDA_AVAILABLE=1)
       - Increase batch sizes for embedding generation
       - Use FAISS for similarity search (already implemented)
    
    3. CONFIGURATION ADJUSTMENTS for 200K skills:
       ```python
       custom_config = CONFIG.copy()
       custom_config['embedding']['batch_size'] = 512
       custom_config['clustering']['min_cluster_size'] = 50
       custom_config['clustering']['use_umap_reduction'] = True
       custom_config['dedup']['similarity_threshold'] = 0.90
       ```
    
    4. INCREMENTAL PROCESSING:
       - Process categories separately if needed
       - Save intermediate results (embeddings, clusters)
       - Use caching (already implemented)
    
    5. QUALITY vs SPEED TRADEOFFS:
       - Reduce UMAP components for faster clustering
       - Limit LLM calls to representative samples
       - Use simpler similarity metrics if needed
    
    6. MONITORING:
       - Check logs regularly (taxonomy_pipeline.log)
       - Monitor memory usage
       - Track processing time per step
    
    7. EXPECTED RUNTIME for 200K skills:
       - Data processing: ~5-10 minutes
       - Embedding generation: ~20-40 minutes (CPU) / ~5-10 minutes (GPU)
       - Deduplication: ~10-20 minutes  
       - Clustering: ~15-30 minutes
       - LLM refinement: ~30-60 minutes (if enabled)
       - Taxonomy building: ~5-10 minutes
       - TOTAL: ~1.5-3 hours (CPU) / ~1-2 hours (GPU)
    """)


if __name__ == "__main__":
    # Run the example pipeline
    results = run_pipeline_example()
    
    # Show how to use the generated taxonomy
    if results['success']:
        load_and_use_taxonomy()
    
    # Show tips for large datasets
    process_large_dataset_tips()
