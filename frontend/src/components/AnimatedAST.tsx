'use client';

import React, { useMemo, useEffect, useCallback } from 'react';
import {
  ReactFlow,
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  ConnectionMode,
  EdgeProps,
  getSmoothStepPath,
  Handle,
  Position,
  useReactFlow,
} from '@xyflow/react';
import { motion } from 'framer-motion';
import { TraceStep, ASTNode } from '@/lib/api';

import '@xyflow/react/dist/style.css';

interface AnimatedASTProps {
  visibleSteps: TraceStep[];
  currentStep: TraceStep | null;
  identifierMapping?: Record<string, string>;
}

interface FlowNode extends Node {
  data: {
    label: string;
    nodeType: string;
    value?: string | number;
    stepIndex: number;
    highlighted: boolean;
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
      return '#06b6d4'; // cyan
    case 'Int2Float':
      return '#ec4899'; // pink/magenta
    case 'Block':
      return '#6366f1'; // indigo
    case 'If':
      return '#14b8a6'; // teal
    case 'RepeatUntil':
      return '#f97316'; // orange
    case 'Read':
      return '#22c55e'; // green
    case 'Write':
      return '#a855f7'; // purple
    case 'Error':
      return '#ef4444'; // red
    default:
      return '#6b7280'; // gray
  }
};

// Custom animated node component
const AnimatedNode = ({ data }: { data: FlowNode['data'] }) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0 }}
      animate={{ 
        opacity: 1, 
        scale: data.highlighted ? 1.1 : 1,
      }}
      transition={{ 
        duration: 0.5,
        delay: data.stepIndex * 0.2 
      }}
      className="px-3 py-2 rounded-lg border-2 text-white font-bold text-sm text-center min-w-[80px] relative flex items-center justify-center whitespace-nowrap"
      style={{
        backgroundColor: getNodeColor(data.nodeType),
        borderColor: data.highlighted ? '#fbbf24' : '#374151',
        borderWidth: data.highlighted ? '3px' : '2px',
        minHeight: '50px',
        width: 'auto',
      }}
    >
      {/* Invisible handles for React Flow connections */}
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

// Simple MiniMap node component that just renders a colored rectangle
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

// Custom animated edge component
const AnimatedEdge = ({ id, sourceX, sourceY, targetX, targetY, data }: EdgeProps) => {
  const [edgePath] = getSmoothStepPath({
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition: Position.Bottom,
    targetPosition: Position.Top,
  });

  const delay = typeof data?.delay === 'number' ? data.delay : 0;

  return (
    <motion.path
      id={id}
      d={edgePath}
      stroke="#6b7280"
      strokeWidth={2}
      fill="none"
      initial={{ pathLength: 0 }}
      animate={{ pathLength: 1 }}
      transition={{ 
        duration: 0.8,
        delay,
        ease: "easeInOut"
      }}
    />
  );
};

// Node types for React Flow
const nodeTypes = {
  animated: AnimatedNode,
};

const edgeTypes = {
  animated: AnimatedEdge,
};

// Component to handle automatic fit view when nodes change
const FitViewOnChange = ({ nodeCount }: { nodeCount: number }) => {
  const { fitView } = useReactFlow();
  
  useEffect(() => {
    if (nodeCount > 0) {
      // Small delay to ensure nodes are rendered before fitting view
      const timeout = setTimeout(() => {
        fitView({ padding: 0.1, duration: 500 });
      }, 100);
      
      return () => clearTimeout(timeout);
    }
  }, [nodeCount, fitView]);
  
  return null;
};

export function AnimatedAST({ visibleSteps, currentStep, identifierMapping }: AnimatedASTProps) {
  // Helper function to get display name with normalized identifier
  const getDisplayName = useCallback((originalName: string): string => {
    const normalizedName = identifierMapping?.[originalName];
    if (normalizedName) {
      return `${normalizedName} (${originalName})`;
    }
    return originalName;
  }, [identifierMapping]);

  // Filter to AST node creation steps
  const astSteps = visibleSteps.filter(step => 
    step.phase === 'parsing' && 
    step.state.action === 'create_ast_node' &&
    step.state.ast_node
  );

  // Build incremental nodes and edges based on visible steps
  const { incrementalNodes, incrementalEdges } = useMemo(() => {
    if (astSteps.length === 0) {
      return { incrementalNodes: [], incrementalEdges: [] };
    }
    
    // Find the Program node (the true root of the AST)
    const programStep = astSteps.find(step => {
      const node = step.state.ast_node;
      return node && typeof node === 'object' && 'type' in node && node.type === 'Program';
    });
    const rootAstNode = programStep?.state.ast_node || astSteps[astSteps.length - 1]?.state.ast_node;
    
    if (!rootAstNode) {
      return { incrementalNodes: [], incrementalEdges: [] };
    }
    
    // Create a map to track step indices for each node
    const stepMap = new Map<string, number>();
    const nodeIdToStepIndex = new Map<string, number>();
    astSteps.forEach((step, index) => {
      const astNode = step.state.ast_node;
      if (astNode && typeof astNode === 'object' && 'type' in astNode) {
        // Create a unique key for this node
        let key = astNode.type;
        if (astNode.type === 'Number' || astNode.type === 'Float') {
          key += `_${astNode.value}`;
        } else if (astNode.type === 'Identifier') {
          key += `_${astNode.name}`;
        } else if (astNode.type === 'BinaryOp') {
          key += `_${astNode.operator}`;
        } else if (astNode.type === 'Assignment') {
          key += `_${astNode.identifier}`;
        }
        stepMap.set(key, index);
      }
    });
    
    const nodes: FlowNode[] = [];
    const edges: Edge[] = [];
    let nodeId = 0;

    // Recursively build nodes and edges from AST structure
    const buildFlowNodes = (astNode: ASTNode, parentId: string | null = null, depth: number = 0): string => {
      const currentId = `node-${nodeId++}`;
      
      // Create unique key for step index lookup
      let key = astNode.type;
      if (astNode.type === 'Number' || astNode.type === 'Float') {
        key += `_${astNode.value}`;
      } else if (astNode.type === 'Identifier') {
        key += `_${astNode.name}`;
      } else if (astNode.type === 'BinaryOp') {
        key += `_${astNode.operator}`;
      } else if (astNode.type === 'Assignment') {
        key += `_${astNode.identifier}`;
      } else if (astNode.type === 'Int2Float') {
        key += `_${JSON.stringify(astNode)}`;
      }
      
      const stepIndex = stepMap.get(key) ?? 0;
      const stepId = astSteps[stepIndex]?.step_id;
      
      // Track this node ID to step index mapping
      nodeIdToStepIndex.set(currentId, stepIndex);
      
      // Create label based on node type
      let label = astNode.type;
      let value: string | number | undefined;
      
      switch (astNode.type) {
        case 'Program':
          label = 'Program';
          break;
        case 'Assignment':
          label = `${getDisplayName(astNode.identifier || 'unknown')} =`;
          break;
        case 'BinaryOp':
          label = astNode.operator || '?';
          break;
        case 'Number':
          label = `${astNode.value}`;
          value = astNode.value;
          break;
        case 'Float':
          label = `${astNode.value}`;
          value = astNode.value;
          break;
        case 'Identifier':
          label = getDisplayName(astNode.name || 'unknown');
          value = astNode.name;
          break;
        case 'Int2Float':
          label = 'Int2Float';
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
          label = `❌ ${astNode.message || 'Parse Error'}`;
          break;
      }

       // Calculate position based on tree layout
       const x = depth === 0 ? 250 : (depth === 1 ? 250 : (parentId?.includes('left') ? 150 : 350));
       const y = depth * 120 + 50;

        // Calculate node width based on label length
        const labelLength = label.length;
        const nodeWidth = Math.max(80, labelLength * 8 + 24); // 8px per char + padding

        // Add node
        nodes.push({
          id: currentId,
          type: 'animated',
          position: { x, y },
          data: {
            label,
            nodeType: astNode.type,
            value,
            stepIndex,
            highlighted: currentStep?.step_id === stepId,
          },
           draggable: false,
           width: nodeWidth,
           height: 50,
         });

       // Add edge from parent (only if parentId is not null)
       if (parentId && parentId !== 'null' && parentId !== null) {
         // Calculate edge delay: appear after both source and target nodes
         const parentStepIndex = nodeIdToStepIndex.get(parentId) ?? 0;
         const currentStepIndex = stepIndex;
         const maxNodeStepIndex = Math.max(parentStepIndex, currentStepIndex);
         const edgeDelay = (maxNodeStepIndex + 1) * 0.2 + 0.3; // Base node delay + extra delay for edge

         const edge = {
           id: `edge-${parentId}-${currentId}`,
           source: String(parentId), // Ensure it's a string
           target: currentId,
           type: 'animated',
           data: { delay: edgeDelay },
           animated: false,
         };
         console.log('Adding edge:', edge, 'delay:', edgeDelay);
         edges.push(edge);
       } else {
         console.log('Skipping edge creation - parentId:', parentId, 'type:', typeof parentId);
       }

      // Build children based on AST node structure
      if (astNode.type === 'Assignment' && 'value' in astNode && astNode.value && typeof astNode.value === 'object') {
        buildFlowNodes(astNode.value as ASTNode, currentId, depth + 1);
      } else if (astNode.type === 'BinaryOp') {
        if ('left' in astNode && astNode.left && typeof astNode.left === 'object') {
          buildFlowNodes(astNode.left as ASTNode, currentId, depth + 1);
        }
        if ('right' in astNode && astNode.right && typeof astNode.right === 'object') {
          buildFlowNodes(astNode.right as ASTNode, currentId, depth + 1);
        }
      } else if (astNode.type === 'Int2Float' && 'child' in astNode && astNode.child && typeof astNode.child === 'object') {
        buildFlowNodes(astNode.child as ASTNode, currentId, depth + 1);
      } else if (astNode.type === 'Program' && 'statements' in astNode && Array.isArray(astNode.statements)) {
        (astNode.statements as ASTNode[]).forEach((stmt: ASTNode) => {
          buildFlowNodes(stmt, currentId, depth + 1);
        });
      } else if (astNode.type === 'Block' && 'statements' in astNode && Array.isArray(astNode.statements)) {
        (astNode.statements as ASTNode[]).forEach((stmt: ASTNode) => {
          buildFlowNodes(stmt, currentId, depth + 1);
        });
      } else if (astNode.type === 'If') {
        if ('condition' in astNode && astNode.condition) {
          buildFlowNodes(astNode.condition as ASTNode, currentId, depth + 1);
        }
        if ('then_branch' in astNode && astNode.then_branch) {
          buildFlowNodes(astNode.then_branch as ASTNode, currentId, depth + 1);
        }
        if ('else_branch' in astNode && astNode.else_branch) {
          buildFlowNodes(astNode.else_branch as ASTNode, currentId, depth + 1);
        }
      } else if (astNode.type === 'RepeatUntil') {
        if ('body' in astNode && astNode.body) {
          buildFlowNodes(astNode.body as ASTNode, currentId, depth + 1);
        }
        if ('condition' in astNode && astNode.condition) {
          buildFlowNodes(astNode.condition as ASTNode, currentId, depth + 1);
        }
      } else if (astNode.type === 'Write' && 'expression' in astNode && astNode.expression) {
        buildFlowNodes(astNode.expression as ASTNode, currentId, depth + 1);
      }

      return currentId;
    };

    if (typeof rootAstNode === 'object' && 'type' in rootAstNode) {
      buildFlowNodes(rootAstNode as ASTNode);
    }

    // Better tree layout positioning
    const layoutNodes = (nodes: FlowNode[]): FlowNode[] => {
      // Find root node (no incoming edges)
      const rootNode = nodes.find(node => 
        !edges.some(edge => edge.target === node.id)
      );
      
      if (!rootNode) return nodes;

      // Simple tree layout algorithm
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
        
        // Add minimum gaps between children (gap before, between, and after each child)
        const minGap = 80;
        const gapSpace = (childCount + 1) * minGap;
        
        // Total width = child widths + gap space
        return totalChildWidth + gapSpace;
      };
      
     const positionSubtree = (nodeId: string, x: number, y: number, width: number) => {
        const node = layoutedNodes.find(n => n.id === nodeId);
        if (!node) return;
        
        // Center the node within its allocated width
        node.position = { x: x - 40, y }; // Offset by half node width for better centering
        
        const childEdges = edges.filter(e => e.source === nodeId);
        const childCount = childEdges.length;
        
        if (childCount > 0) {
          // Calculate width needed for each child based on its subtree
          const childWidths = childEdges.map(edge => calculateSubtreeWidth(edge.target));
          const totalChildWidth = childWidths.reduce((sum, w) => sum + w, 0);
          
          if (childCount === 1) {
            // Single child: center it
            const childWidth = childWidths[0];
            const childX = x;
            const childY = y + 150;
            positionSubtree(childEdges[0].target, childX, childY, childWidth);
          } else {
            // Multiple children: distribute with equal gaps
            const minGap = 80;
            
            // Total space available for gaps (parent width - sum of child widths)
            const totalGapSpace = width - totalChildWidth;
            
            // Divide gap space equally among (childCount + 1) gaps
            const actualGap = Math.max(minGap, totalGapSpace / (childCount + 1));
            
            // Position children left to right with equal gaps
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
      
      // Calculate initial width based on tree complexity
      const rootWidth = calculateSubtreeWidth(rootNode.id);
      const maxWidth = Math.max(1600, rootWidth);
      positionSubtree(rootNode.id, maxWidth / 2, 50, maxWidth);
      return layoutedNodes;
    };

    console.log('Final nodes:', nodes.length, 'Final edges:', edges.length);
    console.log('Edges:', edges);

    console.log('Final nodes:', nodes.length, 'Final edges:', edges.length);
    console.log('Edges:', edges);

    return { 
      incrementalNodes: layoutNodes(nodes), 
      incrementalEdges: edges 
    };
  }, [astSteps, currentStep?.step_id, getDisplayName]);

  // Compute visible nodes and edges based on current step
  const { visibleNodes, visibleEdges } = useMemo(() => {
    console.log('Computing visible nodes, incrementalNodes:', incrementalNodes.length, 'incrementalEdges:', incrementalEdges.length);
    console.log('astSteps step_ids:', astSteps.map(s => s.step_id));
    
    // Only show nodes up to the current step
    let maxStepIndex = astSteps.length - 1; // Default to show all nodes
    
    if (currentStep) {
      const foundIndex = astSteps.findIndex(step => step.step_id === currentStep.step_id);
      if (foundIndex !== -1) {
        maxStepIndex = foundIndex;
      } else {
        // If current step is not in astSteps, find the latest astStep that's <= currentStep
        for (let i = astSteps.length - 1; i >= 0; i--) {
          if (astSteps[i].step_id <= currentStep.step_id) {
            maxStepIndex = i;
            break;
          }
        }
      }
    }

    console.log('Max step index:', maxStepIndex, 'currentStep:', currentStep?.step_id);

    const nodes = incrementalNodes.filter(node => 
      node.data.stepIndex <= maxStepIndex
    );
    
    const edges = incrementalEdges.filter(edge => {
      const sourceNode = incrementalNodes.find(n => n.id === edge.source);
      const targetNode = incrementalNodes.find(n => n.id === edge.target);
      return sourceNode && targetNode && 
             sourceNode.data.stepIndex <= maxStepIndex &&
             targetNode.data.stepIndex <= maxStepIndex;
    });

    console.log('Visible nodes:', nodes.length, 'Visible edges:', edges.length);
    return { visibleNodes: nodes, visibleEdges: edges };
  }, [incrementalNodes, incrementalEdges, currentStep, astSteps]);

  return (
    <div className="space-y-4">
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
        <h3 className="font-semibold mb-2 text-gray-900 dark:text-gray-100">
          AST Construction (React Flow)
        </h3>
        
        {astSteps.length > 0 ? (
          <div className="w-full h-[500px] bg-gray-50 dark:bg-gray-900 rounded border overflow-hidden">
            <ReactFlow
              nodes={visibleNodes}
              edges={visibleEdges}
              connectionMode={ConnectionMode.Loose}
              nodeTypes={nodeTypes}
              edgeTypes={edgeTypes}
              fitView
              fitViewOptions={{ padding: 0.1 }}
              className="bg-gray-50 dark:bg-gray-900"
              defaultViewport={{ x: 0, y: 0, zoom: 1 }}
              proOptions={{ hideAttribution: true }}
              onInit={() => console.log('ReactFlow initialized with nodes:', visibleNodes.length, 'edges:', visibleEdges.length)}
            >
              <FitViewOnChange nodeCount={visibleNodes.length} />
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
                  const color = getNodeColor(node.data?.nodeType || 'Unknown');
                  console.log('MiniMap rendering node:', node.data?.nodeType, 'color:', color);
                  return color;
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
              <div className="text-lg font-semibold mb-2">AST Construction</div>
              <div className="text-sm">Nodes will appear here as the parser builds the AST</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
