from fastapi import FastAPI, Query, HTTPException
import json
from collections import defaultdict

app = FastAPI()

def has_cycle(graph):
    """
    Detect cycles using DFS - simplest correct algorithm.
    Returns True if cycle exists (not a DAG), False if DAG.
    """
    visited = set()
    rec_stack = set()
    
    def dfs(node):
        if node in rec_stack:
            return True  # Cycle detected
        if node in visited:
            return False  # Already processed
        
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in graph.get(node, []):
            if dfs(neighbor):
                return True
        
        rec_stack.remove(node)
        return False
    
    # Check all nodes (handle disconnected components)
    for node in graph:
        if node not in visited:
            if dfs(node):
                return True
    
    return False

def build_graph(edges):
    """
    Build adjacency list from edges.
    Handles different edge formats: {'from': 'A', 'to': 'B'}, ['A', 'B'], or ['A', 'B', ...]
    """
    graph = defaultdict(list)
    
    for edge in edges:
        if isinstance(edge, dict):
            # Format: {'from': 'A', 'to': 'B'} or {'source': 'A', 'target': 'B'}
            from_node = edge.get('from', edge.get('source', edge.get('start')))
            to_node = edge.get('to', edge.get('target', edge.get('end')))
            if from_node is not None and to_node is not None:
                graph[from_node].append(to_node)
        elif isinstance(edge, list) and len(edge) >= 2:
            # Format: ['A', 'B'] or [from, to, ...]
            graph[edge[0]].append(edge[1])
    
    return graph

@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

@app.get('/pipelines/parse')
def parse_pipeline(pipeline: str = Query(...)):
    """
    Parse pipeline data and return deterministic statistics.
    Trust input format and compute node/edge counts with cycle detection.
    """
    try:
        # Parse the JSON string
        pipeline_data = json.loads(pipeline)
        
        # Extract nodes and edges (handle different possible key names)
        nodes = pipeline_data.get('nodes', pipeline_data.get('vertices', pipeline_data.get('node', [])))
        edges = pipeline_data.get('edges', pipeline_data.get('connections', pipeline_data.get('edge', [])))
        
        # Ensure nodes and edges are lists
        if not isinstance(nodes, list):
            nodes = []
        if not isinstance(edges, list):
            edges = []
        
        # Count nodes and edges deterministically
        node_count = len(nodes)
        edge_count = len(edges)
        
        # Build graph and detect cycles
        graph = build_graph(edges)
        has_cycles = has_cycle(graph)
        is_dag = not has_cycles
        
        # Return clean JSON with statistics
        return {
            'node_count': node_count,
            'edge_count': edge_count,
            'is_dag': is_dag
        }
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in pipeline parameter")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing pipeline: {str(e)}")