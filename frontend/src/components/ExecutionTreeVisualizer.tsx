'use client';

import React, { useMemo, useCallback } from 'react';
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
import { ExecutedASTNode } from '@/lib/api';

import '@xyflow/react/dist/style.css';

interface ExecutionTreeVisualizerProps {
  executedAst?: ExecutedASTNode;
  identifierMapping?: Record<string, string>;
}

interface FlowNode extends Node {
  data: {
    label: string;
    nodeType: string;
    result?: number | string | boolean;
    resultType?: string;
    error?: string;
    value?: string | number;
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

const getResultBadgeColor = (resultType?: string): string => {
  switch (resultType) {
    case 'int':
      return 'bg-purple-600 text-white';
    case 'float':
      return 'bg-pink-600 text-white';
    case 'bool':
      return 'bg-green-600 text-white';
    default:
      return 'bg-gray-600 text-white';
  }
};

const formatResult = (result: number | string | boolean | undefined): string => {
  if (result === undefined || result === null) return '';
  if (typeof result === 'boolean') return result ? 'true' : 'false';
  if (typeof result === 'number') {
    if (!Number.isFinite(result)) return 'Infinity';
    if (!Number.isInteger(result)) return result.toFixed(2);
  }
  return String(result);
};

const ExecutionNode = ({ data }: { data: FlowNode['data'] }) => {
  const hasResult = data.result !== undefined && data.result !== null && data.nodeType !== 'Program' && data.nodeType !== 'Block';
  
  return (
    <div className="flex flex-col items-center">
      {/* Result badge above node */}
      {hasResult && (
        <motion.div
          initial={{ opacity: 0, y: 10, scale: 0.8 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.3, delay: 0.1 }}
          className={`px-2 py-1 rounded text-xs font-mono mb-1 font-bold shadow-md ${getResultBadgeColor(data.resultType)} ${data.error ? 'ring-2 ring-red-400' : ''}`}
        >
          {formatResult(data.result)}
          {data.error && <span className="ml-1 text-red-200">!</span>}
        </motion.div>
      )}
      
      {/* Node itself */}
      <motion.div
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="px-3 rounded-lg border-2 text-white font-bold text-sm text-center min-w-[80px] relative flex items-center justify-center"
        style={{
          backgroundColor: getNodeColor(data.nodeType),
          borderColor: data.error ? '#ef4444' : '#374151',
          borderWidth: data.error ? '3px' : '2px',
          boxShadow: data.error ? '0 0 10px rgba(239, 68, 68, 0.5)' : 'none',
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
    </div>
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
  execution: ExecutionNode,
};

const FitViewOnChange = ({ nodeCount }: { nodeCount: number }) => {
  const { fitView } = useReactFlow();
  
  React.useEffect(() => {
    if (nodeCount > 0) {
      const timeout = setTimeout(() => {
        fitView({ padding: 0.1, duration: 500 });
      }, 100);
      
      return () => clearTimeout(timeout);
    }
  }, [nodeCount, fitView]);
  
  return null;
};

export function ExecutionTreeVisualizer({ executedAst, identifierMapping }: ExecutionTreeVisualizerProps) {
  // Helper function to get display name with normalized identifier (V1, V2 for hybrid)
  const getDisplayName = useCallback((originalName: string): string => {
    const normalizedName = identifierMapping?.[originalName];
    if (normalizedName) {
      return `${normalizedName} (${originalName.toUpperCase()})`;
    }
    return originalName.toUpperCase();
  }, [identifierMapping]);

  const { nodes, edges } = useMemo(() => {
    if (!executedAst) {
      return { nodes: [], edges: [] };
    }
    
    const flowNodes: FlowNode[] = [];
    const flowEdges: Edge[] = [];
    let nodeId = 0;

    const buildFlowNodes = (astNode: ExecutedASTNode, parentId: string | null = null): string => {
      // Handle Int2Float specially - show conversion with result
      if (astNode.type === 'Int2Float' && 'child' in astNode && astNode.child) {
        const child = astNode.child as ExecutedASTNode;
        
        let childLabel = '?';
        if (child.type === 'Number') {
          childLabel = `${child.value}`;
        } else if (child.type === 'Identifier' && 'name' in child) {
          childLabel = getDisplayName(child.name as string);
        } else if (child.type === 'BinaryOp') {
          childLabel = 'expr';
        }
        
        // Create the Int2Float node with result
        const int2floatId = `node-${nodeId++}`;
        flowNodes.push({
          id: int2floatId,
          type: 'execution',
          position: { x: 0, y: 0 },
          data: {
            label: `int2float(${childLabel})`,
            nodeType: 'Int2Float',
            result: astNode.result,
            resultType: astNode.result_type,
          },
          draggable: false,
          width: childLabel === 'expr' ? 120 : 110,
          height: 50,
        });

        if (parentId) {
          flowEdges.push({
            id: `edge-${parentId}-${int2floatId}`,
            source: parentId,
            target: int2floatId,
            type: 'smoothstep',
            animated: true,
          });
        }

        // Build child node
        buildFlowNodes(child, int2floatId);
        
        return int2floatId;
      }

      const currentId = `node-${nodeId++}`;
      
      let label = astNode.type;
      let value: string | number | undefined;
      
      switch (astNode.type) {
        case 'Program':
          label = 'Program';
          break;
        case 'Assignment':
          label = 'is';
          break;
        case 'BinaryOp':
          label = astNode.operator || '?';
          break;
        case 'Number':
          label = `${astNode.value}`;
          value = astNode.value;
          break;
        case 'Float': {
          const floatValue = typeof astNode.value === 'number' ? astNode.value : parseFloat(astNode.value as string);
          label = Number.isInteger(floatValue) ? `${floatValue}.0` : `${floatValue}`;
          value = astNode.value;
          break;
        }
        case 'Identifier':
          label = getDisplayName(astNode.name || 'unknown');
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
          label = `read ${getDisplayName(astNode.identifier || '?')}`;
          break;
        case 'Write':
          label = 'write';
          break;
        case 'Error':
          label = `Error`;
          break;
      }

      flowNodes.push({
        id: currentId,
        type: 'execution',
        position: { x: 0, y: 0 },
        data: {
          label,
          nodeType: astNode.type,
          result: astNode.result,
          resultType: astNode.result_type,
          error: astNode.error,
          value,
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
          animated: false,
        });
      }

      // Recursively build children
      if (astNode.type === 'Assignment') {
        if ('left' in astNode && astNode.left && typeof astNode.left === 'object') {
          buildFlowNodes(astNode.left as ExecutedASTNode, currentId);
        }
        if ('right' in astNode && astNode.right && typeof astNode.right === 'object') {
          buildFlowNodes(astNode.right as ExecutedASTNode, currentId);
        }
      } else if (astNode.type === 'BinaryOp') {
        if ('left' in astNode && astNode.left && typeof astNode.left === 'object') {
          buildFlowNodes(astNode.left as ExecutedASTNode, currentId);
        }
        if ('right' in astNode && astNode.right && typeof astNode.right === 'object') {
          buildFlowNodes(astNode.right as ExecutedASTNode, currentId);
        }
      } else if (astNode.type === 'Program' && 'statements' in astNode && Array.isArray(astNode.statements)) {
        (astNode.statements as ExecutedASTNode[]).forEach((stmt) => {
          buildFlowNodes(stmt, currentId);
        });
      } else if (astNode.type === 'Block' && 'statements' in astNode && Array.isArray(astNode.statements)) {
        (astNode.statements as ExecutedASTNode[]).forEach((stmt) => {
          buildFlowNodes(stmt, currentId);
        });
      } else if (astNode.type === 'If') {
        if ('condition' in astNode && astNode.condition) {
          buildFlowNodes(astNode.condition as ExecutedASTNode, currentId);
        }
        if ('then_branch' in astNode && astNode.then_branch) {
          buildFlowNodes(astNode.then_branch as ExecutedASTNode, currentId);
        }
        if ('else_branch' in astNode && astNode.else_branch) {
          buildFlowNodes(astNode.else_branch as ExecutedASTNode, currentId);
        }
      } else if (astNode.type === 'RepeatUntil') {
        if ('body' in astNode && astNode.body) {
          buildFlowNodes(astNode.body as ExecutedASTNode, currentId);
        }
        if ('condition' in astNode && astNode.condition) {
          buildFlowNodes(astNode.condition as ExecutedASTNode, currentId);
        }
      } else if (astNode.type === 'Write' && 'expression' in astNode && astNode.expression) {
        buildFlowNodes(astNode.expression as ExecutedASTNode, currentId);
      } else if (astNode.type === 'Int2Float' && 'child' in astNode && astNode.child) {
        buildFlowNodes(astNode.child as ExecutedASTNode, currentId);
      }

      return currentId;
    };

    buildFlowNodes(executedAst);

    // Layout nodes (same algorithm as AnalyzedASTVisualizer)
    const layoutNodes = (nodes: FlowNode[], edges: Edge[]): FlowNode[] => {
      const rootNode = nodes.find(node => 
        !edges.some(edge => edge.target === node.id)
      );
      
      if (!rootNode) return nodes;

      const layoutedNodes = [...nodes];
      
      const calculateSubtreeWidth = (nodeId: string): number => {
        const childEdges = edges.filter(e => e.source === nodeId);
        const childCount = childEdges.length;
        
        if (childCount === 0) {
          return 150;
        }
        
        const childWidths = childEdges.map(edge => calculateSubtreeWidth(edge.target));
        const totalChildWidth = childWidths.reduce((sum, w) => sum + w, 0);
        
        const minGap = 80;
        const gapSpace = (childCount + 1) * minGap;
        
        return totalChildWidth + gapSpace;
      };
      
      const positionSubtree = (nodeId: string, x: number, y: number, width: number) => {
        const node = layoutedNodes.find(n => n.id === nodeId);
        if (!node) return;
        
        const nodeWidth = node.width || 80;
        node.position = { x: x - (nodeWidth / 2), y };
        
        const childEdges = edges.filter(e => e.source === nodeId);
        const childCount = childEdges.length;
        
        if (childCount > 0) {
          const childWidths = childEdges.map(edge => calculateSubtreeWidth(edge.target));
          const totalChildWidth = childWidths.reduce((sum, w) => sum + w, 0);
          
          if (childCount === 1) {
            const childWidth = childWidths[0];
            const childX = x;
            const childY = y + 150;
            positionSubtree(childEdges[0].target, childX, childY, childWidth);
          } else {
            const minGap = 80;
            const totalGapSpace = width - totalChildWidth;
            const actualGap = Math.max(minGap, totalGapSpace / (childCount + 1));
            
            let currentX = x - (width / 2) + actualGap;
            childEdges.forEach((edge, index) => {
              const childWidth = childWidths[index];
              const childX = currentX + (childWidth / 2);
              const childY = y + 150;
              positionSubtree(edge.target, childX, childY, childWidth);
              currentX += childWidth + actualGap;
            });
          }
        }
      };
      
      const rootWidth = calculateSubtreeWidth(rootNode.id);
      const maxWidth = Math.max(1600, rootWidth);
      positionSubtree(rootNode.id, maxWidth / 2, 50, maxWidth);
      return layoutedNodes;
    };

    return { 
      nodes: layoutNodes(flowNodes, flowEdges), 
      edges: flowEdges 
    };
  }, [executedAst, getDisplayName]);

  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
      <h3 className="font-semibold mb-2 text-gray-900 dark:text-gray-100">
        Execution Tree (with Computed Results)
      </h3>
      
      {/* Legend */}
      <div className="flex flex-wrap gap-3 mb-3 text-xs">
        <div className="flex items-center gap-1">
          <div className="w-4 h-4 rounded bg-purple-600"></div>
          <span className="text-gray-600 dark:text-gray-400">int</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-4 h-4 rounded bg-pink-600"></div>
          <span className="text-gray-600 dark:text-gray-400">float</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-4 h-4 rounded bg-green-600"></div>
          <span className="text-gray-600 dark:text-gray-400">bool</span>
        </div>
      </div>
      
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
            <div className="text-lg font-semibold mb-2">Execution Tree</div>
            <div className="text-sm">The execution tree will appear here after direct execution</div>
          </div>
        </div>
      )}
    </div>
  );
}
