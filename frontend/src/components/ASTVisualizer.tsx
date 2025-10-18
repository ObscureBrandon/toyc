'use client';

import React, { useMemo } from 'react';
import {
  ReactFlow,
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  ConnectionMode,
} from '@xyflow/react';
// import dagre from 'dagre';
import type { ASTNode } from '@/lib/api';

import '@xyflow/react/dist/style.css';

interface ASTVisualizerProps {
  ast: ASTNode | null;
  error?: string;
}

interface FlowNode extends Node {
  data: {
    label: string;
    nodeType: string;
    value?: string | number;
  };
}

// Define node colors based on AST node type
const getNodeColor = (nodeType: string): string => {
  switch (nodeType) {
    case 'Program':
      return '#3b82f6'; // blue
    case 'Assignment':
      return '#10b981'; // emerald  
    case 'BinaryOp':
      return '#f59e0b'; // amber
    case 'Number':
    case 'Float':
      return '#8b5cf6'; // violet
    case 'Identifier':
      return '#ef4444'; // red
    default:
      return '#6b7280'; // gray
  }
};

// Convert AST to React Flow nodes and edges
const convertASTToFlow = (ast: ASTNode): { nodes: FlowNode[]; edges: Edge[] } => {
  const nodes: FlowNode[] = [];
  const edges: Edge[] = [];
  let nodeId = 0;

  const traverse = (node: ASTNode, parentId: string | null = null): string => {
    const currentId = `node-${nodeId++}`;
    
    // Create label based on node type
    let label = node.type;
    let value: string | number | undefined;
    
    switch (node.type) {
      case 'Program':
        label = 'Program';
        break;
      case 'Assignment':
        label = `${node.identifier} =`;
        break;
      case 'BinaryOp':
        label = node.operator || 'op';
        break;
      case 'Number':
        label = `${node.value}`;
        value = node.value;
        break;
      case 'Float':
        label = `${node.value}`;
        value = node.value;
        break;
      case 'Identifier':
        label = node.name || 'id';
        value = node.name;
        break;
    }

    // Add node
    nodes.push({
      id: currentId,
      type: 'default',
      position: { x: 0, y: 0 }, // Will be positioned by dagre
      data: {
        label,
        nodeType: node.type,
        value,
      },
      style: {
        background: getNodeColor(node.type),
        color: 'white',
        border: '2px solid #374151',
        borderRadius: '8px',
        padding: '10px',
        fontSize: '14px',
        fontWeight: 'bold',
        minWidth: '80px',
        textAlign: 'center',
      },
    });

    // Add edge from parent
    if (parentId) {
      edges.push({
        id: `edge-${parentId}-${currentId}`,
        source: parentId,
        target: currentId,
        type: 'smoothstep',
        style: { stroke: '#6b7280', strokeWidth: 2 },
      });
    }

    // Recursively process children
    if (node.statements) {
      // Program node
      node.statements.forEach((stmt: ASTNode) => traverse(stmt, currentId));
    } else if (node.left && node.right) {
      // Binary operation
      traverse(node.left, currentId);
      traverse(node.right, currentId);
    } else if (node.value && typeof node.value === 'object') {
      // Assignment value
      traverse(node.value, currentId);
    }

    return currentId;
  };

  traverse(ast);
  return { nodes, edges };
};

// Auto-layout nodes using dagre
const getLayoutedElements = (nodes: FlowNode[], edges: Edge[]) => {
  // Simple fallback layout without dagre for now
  const layoutedNodes = nodes.map((node, index) => {
    return {
      ...node,
      position: {
        x: (index % 3) * 150 + 100, // Simple grid layout
        y: Math.floor(index / 3) * 100 + 50,
      },
    };
  });

  return { nodes: layoutedNodes, edges };
};

export default function ASTVisualizer({ ast, error }: ASTVisualizerProps) {
  const { nodes: flowNodes, edges: flowEdges } = useMemo(() => {
    if (!ast || !ast.data) return { nodes: [], edges: [] };
    
    try {
      const { nodes, edges } = convertASTToFlow(ast);
      return getLayoutedElements(nodes, edges);
    } catch (err) {
      console.error('Error converting AST to flow:', err);
      return { nodes: [], edges: [] };
    }
  }, [ast]);

  const [nodes, setNodes, onNodesChange] = useNodesState(flowNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(flowEdges);

  // Update nodes and edges when AST changes
  React.useEffect(() => {
    setNodes(flowNodes);
    setEdges(flowEdges);
  }, [flowNodes, flowEdges, setNodes, setEdges]);

  if (error) {
    return (
      <div className="w-full h-full bg-gray-900 border border-gray-700 rounded-lg p-6 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-400 text-lg font-medium mb-2">Parser Error</div>
          <div className="text-gray-300 text-sm">{error}</div>
        </div>
      </div>
    );
  }

  if (!ast || nodes.length === 0) {
    return (
      <div className="w-full h-full bg-gray-900 border border-gray-700 rounded-lg p-6 flex items-center justify-center">
        <div className="text-gray-400 text-center">
          <div className="text-lg font-medium mb-2">No AST Generated</div>
          <div className="text-sm">Enter valid code and click &quot;Parse&quot; to see the syntax tree</div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full bg-gray-900 border border-gray-700 rounded-lg overflow-hidden">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        connectionMode={ConnectionMode.Loose}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        className="bg-gray-900"
        defaultViewport={{ x: 0, y: 0, zoom: 1 }}
      >
        <Background color="#374151" />
        <Controls className="bg-gray-800 border-gray-600" />
        <MiniMap
          className="bg-gray-800 border border-gray-600"
          nodeColor={(node) => getNodeColor((node.data as FlowNode['data']).nodeType)}
          maskColor="rgba(17, 24, 39, 0.8)"
        />
      </ReactFlow>
    </div>
  );
}