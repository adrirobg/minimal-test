'use client';

import React, { useState } from 'react';
import { ChevronRight, ChevronDown, Folder, FolderOpen, Plus, Edit, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { ProjectNode } from '@/types/project';

interface TreeViewProps {
  nodes: ProjectNode[];
  onSelectNode?: (node: ProjectNode) => void;
  onCreateChild?: (parentNode: ProjectNode) => void;
  onEdit?: (node: ProjectNode) => void;
  onDelete?: (node: ProjectNode) => void;
  selectedNodeId?: string;
  className?: string;
}

interface TreeNodeProps {
  node: ProjectNode;
  level: number;
  onSelectNode?: (node: ProjectNode) => void;
  onCreateChild?: (parentNode: ProjectNode) => void;
  onEdit?: (node: ProjectNode) => void;
  onDelete?: (node: ProjectNode) => void;
  selectedNodeId?: string;
  isExpanded: boolean;
  onToggleExpanded: (nodeId: string) => void;
}

const TreeNode: React.FC<TreeNodeProps> = ({
  node,
  level,
  onSelectNode,
  onCreateChild,
  onEdit,
  onDelete,
  selectedNodeId,
  isExpanded,
  onToggleExpanded,
}) => {
  const hasChildren = node.children && node.children.length > 0;
  const isSelected = selectedNodeId === node.id;
  const [isHovered, setIsHovered] = useState(false);

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (hasChildren) {
      onToggleExpanded(node.id);
    }
  };

  const handleSelect = () => {
    onSelectNode?.(node);
  };

  const handleCreateChild = (e: React.MouseEvent) => {
    e.stopPropagation();
    onCreateChild?.(node);
  };

  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    onEdit?.(node);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDelete?.(node);
  };

  return (
    <div className="select-none">
      <div
        className={`
          flex items-center py-2 px-2 rounded-md cursor-pointer
          hover:bg-gray-100 dark:hover:bg-gray-800
          ${isSelected ? 'bg-blue-100 dark:bg-blue-900 border-l-4 border-blue-500' : ''}
          ${level > 0 ? 'ml-' + (level * 4) : ''}
        `}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        onClick={handleSelect}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {/* Expand/Collapse Icon */}
        <Button
          variant="ghost"
          size="sm"
          className="h-6 w-6 p-0 mr-2"
          onClick={handleToggle}
        >
          {hasChildren ? (
            isExpanded ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )
          ) : (
            <div className="h-4 w-4" />
          )}
        </Button>

        {/* Folder Icon */}
        <div className="mr-2">
          {hasChildren ? (
            isExpanded ? (
              <FolderOpen className="h-4 w-4 text-blue-600" />
            ) : (
              <Folder className="h-4 w-4 text-blue-600" />
            )
          ) : (
            <Folder className="h-4 w-4 text-gray-500" />
          )}
        </div>

        {/* Project Name */}
        <span className="flex-1 text-sm font-medium text-gray-900 dark:text-gray-100">
          {node.name}
        </span>

        {/* Action Buttons */}
        {isHovered && (
          <div className="flex items-center space-x-1">
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={handleCreateChild}
              title="Add subproject"
            >
              <Plus className="h-3 w-3" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={handleEdit}
              title="Edit project"
            >
              <Edit className="h-3 w-3" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0 text-red-600 hover:text-red-700"
              onClick={handleDelete}
              title="Delete project"
            >
              <Trash2 className="h-3 w-3" />
            </Button>
          </div>
        )}
      </div>

      {/* Children */}
      {hasChildren && isExpanded && (
        <div>
          {node.children!.map((child) => (
            <TreeNode
              key={child.id}
              node={child}
              level={level + 1}
              onSelectNode={onSelectNode}
              onCreateChild={onCreateChild}
              onEdit={onEdit}
              onDelete={onDelete}
              selectedNodeId={selectedNodeId}
              isExpanded={isExpanded}
              onToggleExpanded={onToggleExpanded}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export const TreeView: React.FC<TreeViewProps> = ({
  nodes,
  onSelectNode,
  onCreateChild,
  onEdit,
  onDelete,
  selectedNodeId,
  className = '',
}) => {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

  const handleToggleExpanded = (nodeId: string) => {
    setExpandedNodes(prev => {
      const newSet = new Set(prev);
      if (newSet.has(nodeId)) {
        newSet.delete(nodeId);
      } else {
        newSet.add(nodeId);
      }
      return newSet;
    });
  };

  if (nodes.length === 0) {
    return (
      <Card className={`p-6 ${className}`}>
        <div className="text-center text-gray-500 dark:text-gray-400">
          <Folder className="h-12 w-12 mx-auto mb-3 opacity-50" />
          <p className="text-sm">No projects found</p>
          <p className="text-xs mt-1">Create your first project to get started</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className={`p-4 ${className}`}>
      <div className="space-y-1">
        {nodes.map((node) => (
          <TreeNode
            key={node.id}
            node={node}
            level={0}
            onSelectNode={onSelectNode}
            onCreateChild={onCreateChild}
            onEdit={onEdit}
            onDelete={onDelete}
            selectedNodeId={selectedNodeId}
            isExpanded={expandedNodes.has(node.id)}
            onToggleExpanded={handleToggleExpanded}
          />
        ))}
      </div>
    </Card>
  );
};

export default TreeView;
