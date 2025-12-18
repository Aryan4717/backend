from fastapi import FastAPI, Query, HTTPException
import json

app = FastAPI()

@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

@app.get('/pipelines/parse')
def parse_pipeline(pipeline: str = Query(...)):
    """
    Parse pipeline data and return deterministic statistics.
    Trust input format and compute node/edge counts.
    """
    try:
        # Parse the JSON string
        pipeline_data = json.loads(pipeline)
        
        # Extract nodes and edges (handle different possible key names)
        nodes = pipeline_data.get('nodes', pipeline_data.get('vertices', pipeline_data.get('node', [])))
        edges = pipeline_data.get('edges', pipeline_data.get('connections', pipeline_data.get('edge', [])))
        
        # Count nodes and edges deterministically
        node_count = len(nodes) if isinstance(nodes, list) else 0
        edge_count = len(edges) if isinstance(edges, list) else 0
        
        # Return clean JSON with statistics only
        return {
            'node_count': node_count,
            'edge_count': edge_count
        }
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in pipeline parameter")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing pipeline: {str(e)}")