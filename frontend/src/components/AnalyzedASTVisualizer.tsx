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
    case 'Block':
      return '#6366f1';
    case 'If':
      return '#14b8a6';
    case 'RepeatUntil':
      return '#f97316';
    case 'Read':
      return '#22c55e';
    case 'Write':
      return '#a855f7';
    case 'Error':
      return '#ef4444';
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
      className="px-3 rounded-lg border-2 text-white font-bold text-sm text-center min-w-[80px] relative flex items-center justify-center"
      style={{
        backgroundColor: getNodeColor(data.nodeType),
        borderColor: data.isCoercion ? '#fbbf24' : '#374151',
        borderWidth: data.isCoercion ? '3px' : '2px',
        boxShadow: data.isCoercion ? '0 0 10px rgba(251, 191, 36, 0.5)' : 'none',
        height: '50px',
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
        } else if (child.type === 'Identifier' && 'name' in child) {
          childLabel = child.name as string;
          outputLabel = `${child.name} (Float)`;
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
          height: 50,
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
          height: 50,
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
          label = `${astNode.identifier || 'unknown'} :=`;
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
        case 'Block':
          label = 'Block';
          break;
        case 'If':
          label = 'if';
          break;
        case 'RepeatUntil':
          label = 'repeat-until';
          break;
        case 'Read':
          label = `read ${astNode.identifier || '?'}`;
          break;
        case 'Write':
          label = 'write';
          break;
        case 'Error':
          label = `❌ ${astNode.message || 'Parse Error'}`;
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
        height: 50,
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
      } else if (astNode.type === 'Block' && 'statements' in astNode && Array.isArray(astNode.statements)) {
        (astNode.statements as ASTNode[]).forEach((stmt: ASTNode) => {
          buildFlowNodes(stmt, currentId);
        });
      } else if (astNode.type === 'If') {
        if ('condition' in astNode && astNode.condition) {
          buildFlowNodes(astNode.condition as ASTNode, currentId);
        }
        if ('then_branch' in astNode && astNode.then_branch) {
          buildFlowNodes(astNode.then_branch as ASTNode, currentId);
        }
        if ('else_branch' in astNode && astNode.else_branch) {
          buildFlowNodes(astNode.else_branch as ASTNode, currentId);
        }
      } else if (astNode.type === 'RepeatUntil') {
        if ('body' in astNode && astNode.body) {
          buildFlowNodes(astNode.body as ASTNode, currentId);
        }
        if ('condition' in astNode && astNode.condition) {
          buildFlowNodes(astNode.condition as ASTNode, currentId);
        }
      } else if (astNode.type === 'Write' && 'expression' in astNode && astNode.expression) {
        buildFlowNodes(astNode.expression as ASTNode, currentId);
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
      
      // Calculate required width for each subtree (bottom-up)
      const calculateSubtreeWidth = (nodeId: string): number => {
        const childEdges = edges.filter(e => e.source === nodeId);
        const childCount = childEdges.length;
        
        if (childCount === 0) {
          // Leaf node: return minimum width
          return 150;
        }
        
        // Calculate total width needed for all children
        const childWidths = childEdges.map(edge => calculateSubtreeWidth(edge.target));
        const totalChildWidth = childWidths.reduce((sum, w) => sum + w, 0);
        
        // Use the larger of: sum of child widths OR minimum spacing * child count
        const minSpacingPerChild = 250;
        return Math.max(totalChildWidth, childCount * minSpacingPerChild);
      };
      
      const positionSubtree = (nodeId: string, x: number, y: number, width: number) => {
        const node = layoutedNodes.find(n => n.id === nodeId);
        if (!node) return;
        
        const nodeWidth = node.width || 80;
        node.position = { x: x - (nodeWidth / 2), y };
        
        const childEdges = edges.filter(e => e.source === nodeId);
        const childCount = childEdges.length;
        
        if (childCount > 0) {
          // Calculate width needed for each child based on its subtree
          const childWidths = childEdges.map(edge => calculateSubtreeWidth(edge.target));
          const totalChildWidth = childWidths.reduce((sum, w) => sum + w, 0);
          const requiredWidth = Math.max(width, totalChildWidth);
          
          if (childCount === 1) {
            // Single child: center it
            const childWidth = childWidths[0];
            const childX = x;
            const childY = y + 150;
            positionSubtree(childEdges[0].target, childX, childY, childWidth);
          } else {
            // Multiple children: space them evenly with padding
            const totalGaps = childCount + 1;
            const availableForGaps = requiredWidth - totalChildWidth;
            const gapSize = Math.max(50, availableForGaps / totalGaps);
            
            // Position children left to right with gaps
            let currentX = x - (requiredWidth / 2) + gapSize;
            childEdges.forEach((edge, index) => {
              const childWidth = childWidths[index];
              const childX = currentX + (childWidth / 2);
              const childY = y + 150;
              positionSubtree(edge.target, childX, childY, childWidth);
              currentX += childWidth + gapSize;
            });
          }
        }
      };
      
      // Calculate initial width based on tree complexity
      const rootWidth = calculateSubtreeWidth(rootNode.id);
      const maxWidth = Math.max(1600, rootWidth);
      positionSubtree(rootNode.id, maxWidth / 2, 50, maxWidth);
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
