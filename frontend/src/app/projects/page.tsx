'use client';

import React, { useEffect, useState } from 'react';
import { Plus, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { TreeView } from '@/components/pkm/TreeView';
import { ProjectForm } from '@/components/forms/ProjectForm';
import { useProjectsStore } from '@/lib/store/projects';
import { Project, ProjectNode, ProjectCreate, ProjectUpdate } from '@/types/project';

export default function ProjectsPage() {
  const {
    projectHierarchy,
    isLoading,
    error,
    fetchProjects,
    createProject,
    updateProject,
    deleteProject,
    setCurrentProject,
    clearError,
  } = useProjectsStore();

  const [selectedNode, setSelectedNode] = useState<ProjectNode | null>(null);
  const [formMode, setFormMode] = useState<'create' | 'edit'>('create');
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [parentForNewProject, setParentForNewProject] = useState<Project | null>(null);
  const [projectToDelete, setProjectToDelete] = useState<ProjectNode | null>(null);

  // Load projects on component mount
  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  // Clear error when component unmounts
  useEffect(() => {
    return () => clearError();
  }, [clearError]);

  const handleSelectNode = (node: ProjectNode) => {
    setSelectedNode(node);
    setCurrentProject(node);
  };

  const handleCreateProject = (parentNode?: ProjectNode) => {
    setFormMode('create');
    setParentForNewProject(parentNode || null);
    setIsFormOpen(true);
  };

  const handleEditProject = (node: ProjectNode) => {
    setSelectedNode(node);
    setFormMode('edit');
    setParentForNewProject(null);
    setIsFormOpen(true);
  };

  const handleDeleteProject = (node: ProjectNode) => {
    setProjectToDelete(node);
  };

  const handleFormSubmit = async (data: ProjectCreate | ProjectUpdate) => {
    try {
      if (formMode === 'create') {
        await createProject(data as ProjectCreate);
      } else if (selectedNode) {
        await updateProject(selectedNode.id, data as ProjectUpdate);
      }
      setIsFormOpen(false);
      setSelectedNode(null);
      setParentForNewProject(null);
    } catch (error) {
      // Error is handled in the store
      console.error('Form submission error:', error);
    }
  };

  const handleFormCancel = () => {
    setIsFormOpen(false);
    setSelectedNode(null);
    setParentForNewProject(null);
  };

  const confirmDelete = async () => {
    if (projectToDelete) {
      try {
        await deleteProject(projectToDelete.id);
        setProjectToDelete(null);
        if (selectedNode?.id === projectToDelete.id) {
          setSelectedNode(null);
          setCurrentProject(null);
        }
      } catch (error) {
        // Error is handled in the store
        console.error('Delete error:', error);
      }
    }
  };

  const handleRefresh = () => {
    fetchProjects();
  };

  return (
    <div className="container mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
            Projects
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Manage your project hierarchy and organization
          </p>
        </div>

        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={handleRefresh}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>

          <Dialog open={isFormOpen} onOpenChange={setIsFormOpen}>
            <DialogTrigger asChild>
              <Button onClick={() => handleCreateProject()}>
                <Plus className="h-4 w-4 mr-2" />
                New Project
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>
                  {formMode === 'create' ? 'Create New Project' : 'Edit Project'}
                </DialogTitle>
              </DialogHeader>
              <ProjectForm
                mode={formMode}
                project={selectedNode || undefined}
                parentProject={parentForNewProject || undefined}
                onSubmit={handleFormSubmit}
                onCancel={handleFormCancel}
                isLoading={isLoading}
              />
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
          <p className="text-red-700 dark:text-red-300 text-sm">{error}</p>
          <Button
            variant="ghost"
            size="sm"
            onClick={clearError}
            className="mt-2"
          >
            Dismiss
          </Button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Project Tree */}
        <div className="lg:col-span-2">
          <TreeView
            nodes={projectHierarchy}
            onSelectNode={handleSelectNode}
            onCreateChild={handleCreateProject}
            onEdit={handleEditProject}
            onDelete={handleDeleteProject}
            selectedNodeId={selectedNode?.id}
            className="h-fit"
          />
        </div>

        {/* Project Details */}
        <div className="lg:col-span-1">
          {selectedNode ? (
            <div className="bg-white dark:bg-gray-800 rounded-lg border p-6">
              <h3 className="text-xl font-semibold mb-4">{selectedNode.name}</h3>

              {selectedNode.description && (
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Description
                  </h4>
                  <p className="text-gray-600 dark:text-gray-400 text-sm">
                    {selectedNode.description}
                  </p>
                </div>
              )}

              <div className="space-y-3 text-sm">
                <div>
                  <span className="font-medium text-gray-700 dark:text-gray-300">ID:</span>
                  <span className="ml-2 font-mono text-gray-600 dark:text-gray-400">
                    {selectedNode.id}
                  </span>
                </div>

                <div>
                  <span className="font-medium text-gray-700 dark:text-gray-300">Created:</span>
                  <span className="ml-2 text-gray-600 dark:text-gray-400">
                    {new Date(selectedNode.created_at).toLocaleDateString()}
                  </span>
                </div>

                <div>
                  <span className="font-medium text-gray-700 dark:text-gray-300">Updated:</span>
                  <span className="ml-2 text-gray-600 dark:text-gray-400">
                    {new Date(selectedNode.updated_at).toLocaleDateString()}
                  </span>
                </div>

                {selectedNode.children && selectedNode.children.length > 0 && (
                  <div>
                    <span className="font-medium text-gray-700 dark:text-gray-300">
                      Subprojects:
                    </span>
                    <span className="ml-2 text-gray-600 dark:text-gray-400">
                      {selectedNode.children.length}
                    </span>
                  </div>
                )}
              </div>

              <div className="mt-6 flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleEditProject(selectedNode)}
                >
                  Edit
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleCreateProject(selectedNode)}
                >
                  Add Subproject
                </Button>
              </div>
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-lg border p-6 text-center">
              <p className="text-gray-500 dark:text-gray-400">
                Select a project to view details
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={!!projectToDelete} onOpenChange={() => setProjectToDelete(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Project</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete &quot;{projectToDelete?.name}&quot;? This action cannot be undone.
              {projectToDelete?.children && projectToDelete.children.length > 0 && (
                <span className="block mt-2 text-orange-600 dark:text-orange-400">
                  Warning: This project has {projectToDelete.children.length} subproject(s) that will also be deleted.
                </span>
              )}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={confirmDelete}
              className="bg-red-600 hover:bg-red-700"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
