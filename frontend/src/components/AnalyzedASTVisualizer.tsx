'use client';

import React, { useMemo, useEffect } from 'react';
import {
  ReactFlow,
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  ConnectionMode,
  Handle,
  Position,
  useReactFlow,
} from '@xyflow/react';
import { motion } from 'framer-motion';
import { ASTNode } from '@/lib/api';

import '@xyflow/react/dist/style.css';

interface AnalyzedASTVisualizerProps {
  analyzedAst?: ASTNode;
}

interface FlowNode extends Node {
  data: {
    label: string;
    nodeType: string;
    value?: string | number;
    isCoercion: boolean;
  };
}

const getNodeColor = (nodeType: string): string => {
  switch (nodeType) {
    case 'Program':
      return '#3b82f6';
    case 'Assignment':
      return '#10b981';
    case 'BinaryOp':
      return '#f59e0b';
    case 'Number':
    case 'Float':
      return '#8b5cf6';
    case 'Identifier':
      return '#06b6d4';
    case 'Int2Float':
      return '#ec4899';
    default:
      return '#6b7280';
  }
};

const AnalyzedASTNode = ({ data }: { data: FlowNode['data'] }) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className="px-3 py-2 rounded-lg border-2 text-white font-bold text-sm text-center min-w-[80px] relative"
      style={{
        backgroundColor: getNodeColor(data.nodeType),
        borderColor: data.isCoercion ? '#fbbf24' : '#374151',
        borderWidth: data.isCoercion ? '3px' : '2px',
        boxShadow: data.isCoercion ? '0 0 10px rgba(251, 191, 36, 0.5)' : 'none',
      }}
    >
      <Handle
        type="target"
        position={Position.Top}
        style={{ opacity: 0, pointerEvents: 'none' }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        style={{ opacity: 0, pointerEvents: 'none' }}
      />
      {data.label}
    </motion.div>
  );
};

const SimpleMiniMapNode = ({ x, y, width, height, color }: { x: number; y: number; width: number; height: number; color?: string }) => {
  return (
    <rect
      x={x - width/2}
      y={y - height/2}
      width={width || 60}
      height={height || 30}
      fill={color || '#6b7280'}
      stroke="#374151"
      strokeWidth="1"
      rx="3"
    />
  );
};

const nodeTypes = {
  analyzed: AnalyzedASTNode,
};

const FitViewOnChange = ({ nodeCount }: { nodeCount: number }) => {
  const { fitView } = useReactFlow();
  
  useEffect(() => {
    if (nodeCount > 0) {
      const timeout = setTimeout(() => {
        fitView({ padding: 0.1, duration: 500 });
      }, 100);
      
      return () => clearTimeout(timeout);
    }
  }, [nodeCount, fitView]);
  
  return null;
};

export function AnalyzedASTVisualizer({ analyzedAst }: AnalyzedASTVisualizerProps) {
  const { nodes, edges } = useMemo(() => {
    if (!analyzedAst) {
      return { nodes: [], edges: [] };
    }
    
    const flowNodes: FlowNode[] = [];
    const flowEdges: Edge[] = [];
    let nodeId = 0;

    const buildFlowNodes = (astNode: ASTNode, parentId: string | null = null): string => {
      if (astNode.type === 'Int2Float' && 'child' in astNode && astNode.child) {
        const child = astNode.child as ASTNode;
        
        let childLabel = '?';
        let outputLabel = '?.0';
        if (child.type === 'Number') {
          childLabel = `${child.value}`;
          outputLabel = `${child.value}.0`;
        } else if (child.type === 'BinaryOp') {
          childLabel = 'expr';
          outputLabel = 'result';
        }
        
        // Create output node (the float result)
        const outputId = `node-${nodeId++}`;
        flowNodes.push({
          id: outputId,
          type: 'analyzed',
          position: { x: 0, y: 0 },
          data: {
            label: outputLabel,
            nodeType: 'Float',
            value: childLabel !== 'expr' ? childLabel : undefined,
            isCoercion: false,
          },
          draggable: false,
          width: 80,
          height: 40,
        });

        if (parentId) {
          flowEdges.push({
            id: `edge-${parentId}-${outputId}`,
            source: parentId,
            target: outputId,
            type: 'smoothstep',
            animated: false,
          });
        }

        // Create conversion node
        const conversionId = `node-${nodeId++}`;
        flowNodes.push({
          id: conversionId,
          type: 'analyzed',
          position: { x: 0, y: 0 },
          data: {
            label: `int2float(${childLabel})`,
            nodeType: 'Int2Float',
            value: undefined,
            isCoercion: true,
          },
          draggable: false,
          width: childLabel === 'expr' ? 120 : 110,
          height: 40,
        });

        flowEdges.push({
          id: `edge-${outputId}-${conversionId}`,
          source: outputId,
          target: conversionId,
          type: 'straight',
          animated: true,
        });

        // Create/connect child node(s)
        const childId = buildFlowNodes(child, conversionId);
        
        // Make the edge from conversion to child straight and animated
        const conversionToChildEdge = flowEdges.find(e => e.source === conversionId && e.target === childId);
        if (conversionToChildEdge) {
          conversionToChildEdge.type = 'straight';
          conversionToChildEdge.animated = true;
        }
        
        return outputId;
      }

      const currentId = `node-${nodeId++}`;
      
      let label = astNode.type;
      let value: string | number | undefined;
      const isCoercion = false;
      
      switch (astNode.type) {
        case 'Program':
          label = 'Program';
          break;
        case 'Assignment':
          label = `${astNode.identifier || 'unknown'} =`;
          break;
        case 'BinaryOp':
          label = astNode.operator || '?';
          break;
        case 'Number':
          label = `${astNode.value}`;
          value = astNode.value;
          break;
        case 'Float':
          const floatValue = typeof astNode.value === 'number' ? astNode.value : parseFloat(astNode.value as string);
          label = Number.isInteger(floatValue) ? `${floatValue}.0` : `${floatValue}`;
          value = astNode.value;
          break;
        case 'Identifier':
          label = astNode.name || 'unknown';
          value = astNode.name;
          break;
      }

      flowNodes.push({
        id: currentId,
        type: 'analyzed',
        position: { x: 0, y: 0 },
        data: {
          label,
          nodeType: astNode.type,
          value,
          isCoercion,
        },
        draggable: false,
        width: 80,
        height: 40,
      });

      if (parentId) {
        flowEdges.push({
          id: `edge-${parentId}-${currentId}`,
          source: parentId,
          target: currentId,
          type: 'smoothstep',
          animated: isCoercion,
        });
      }

      if (astNode.type === 'Assignment' && 'value' in astNode && astNode.value && typeof astNode.value === 'object') {
        buildFlowNodes(astNode.value as ASTNode, currentId);
      } else if (astNode.type === 'BinaryOp') {
        if ('left' in astNode && astNode.left && typeof astNode.left === 'object') {
          buildFlowNodes(astNode.left as ASTNode, currentId);
        }
        if ('right' in astNode && astNode.right && typeof astNode.right === 'object') {
          buildFlowNodes(astNode.right as ASTNode, currentId);
        }
      } else if (astNode.type === 'Program' && 'statements' in astNode && Array.isArray(astNode.statements)) {
        (astNode.statements as ASTNode[]).forEach((stmt: ASTNode) => {
          buildFlowNodes(stmt, currentId);
        });
      }

      return currentId;
    };

    buildFlowNodes(analyzedAst);

    const layoutNodes = (nodes: FlowNode[], edges: Edge[]): FlowNode[] => {
      const rootNode = nodes.find(node => 
        !edges.some(edge => edge.target === node.id)
      );
      
      if (!rootNode) return nodes;

      const layoutedNodes = [...nodes];
      
      const positionSubtree = (nodeId: string, x: number, y: number, width: number) => {
        const node = layoutedNodes.find(n => n.id === nodeId);
        if (!node) return;
        
        const nodeWidth = node.width || 80;
        node.position = { x: x - (nodeWidth / 2), y };
        
        const childEdges = edges.filter(e => e.source === nodeId);
        const childCount = childEdges.length;
        
        if (childCount > 0) {
          const childWidth = width / childCount;
          childEdges.forEach((edge, index) => {
            const childX = x + (index * childWidth) + (childWidth / 2) - (width / 2);
            const childY = y + 120;
            positionSubtree(edge.target, childX, childY, childWidth);
          });
        }
      };
      
      positionSubtree(rootNode.id, 400, 50, 800);
      return layoutedNodes;
    };

    return { 
      nodes: layoutNodes(flowNodes, flowEdges), 
      edges: flowEdges 
    };
  }, [analyzedAst]);

  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
      <h3 className="font-semibold mb-2 text-gray-900 dark:text-gray-100">
        Analyzed AST (with Type Coercion Nodes)
      </h3>
      
      {nodes.length > 0 ? (
        <div className="w-full h-[500px] bg-gray-50 dark:bg-gray-900 rounded border overflow-hidden">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            connectionMode={ConnectionMode.Loose}
            nodeTypes={nodeTypes}
            fitView
            fitViewOptions={{ padding: 0.1 }}
            className="bg-gray-50 dark:bg-gray-900"
            defaultViewport={{ x: 0, y: 0, zoom: 1 }}
            proOptions={{ hideAttribution: true }}
          >
            <FitViewOnChange nodeCount={nodes.length} />
            <Background color="#6b7280" />
            <Controls 
              style={{
                backgroundColor: '#374151',
                border: '1px solid #6b7280',
              }}
            />
            <MiniMap
              nodeComponent={SimpleMiniMapNode}
              nodeColor={(node: { data?: { nodeType?: string } }) => {
                return getNodeColor(node.data?.nodeType || 'Unknown');
              }}
              nodeStrokeWidth={1}
              nodeBorderRadius={3}
              bgColor="#1f2937"
              maskColor="rgba(255, 255, 255, 0.1)"
              maskStrokeColor="#6b7280"
              maskStrokeWidth={1}
              pannable
              zoomable
            />
          </ReactFlow>
        </div>
      ) : (
        <div className="w-full h-[500px] bg-gray-50 dark:bg-gray-900 rounded border flex items-center justify-center">
          <div className="text-gray-500 dark:text-gray-400 text-center">
            <div className="text-lg font-semibold mb-2">Analyzed AST</div>
            <div className="text-sm">The analyzed AST will appear here after semantic analysis</div>
          </div>
        </div>
      )}
    </div>
  );
}
