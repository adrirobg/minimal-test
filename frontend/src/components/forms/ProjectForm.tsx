'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { ProjectCreateSchema, ProjectUpdateSchema, ProjectCreate, ProjectUpdate, Project } from '@/types/project';
import { useProjectsStore } from '@/lib/store/projects';

interface ProjectFormProps {
  mode: 'create' | 'edit';
  project?: Project;
  parentProject?: Project;
  onSubmit?: (data: ProjectCreate | ProjectUpdate) => void;
  onCancel?: () => void;
  isLoading?: boolean;
}

export const ProjectForm: React.FC<ProjectFormProps> = ({
  mode,
  project,
  parentProject,
  onSubmit,
  onCancel,
  isLoading = false,
}) => {
  const { projects } = useProjectsStore();

  const schema = mode === 'create' ? ProjectCreateSchema : ProjectUpdateSchema;

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<ProjectCreate | ProjectUpdate>({
    resolver: zodResolver(schema),
    defaultValues: mode === 'edit' && project ? {
      name: project.name,
      description: project.description || '',
      parent_project_id: project.parent_project_id || undefined,
    } : {
      name: '',
      description: '',
      parent_project_id: parentProject?.id || 'none',
    },
  });

  const selectedParentId = watch('parent_project_id');

  // Filter out the current project and its descendants from parent options
  const getAvailableParents = (): Project[] => {
    if (mode === 'create') {
      return projects;
    }

    // For edit mode, exclude the current project and its descendants
    const getDescendantIds = (projectId: string, allProjects: Project[]): string[] => {
      const descendants: string[] = [projectId];
      const children = allProjects.filter(p => p.parent_project_id === projectId);

      children.forEach(child => {
        descendants.push(...getDescendantIds(child.id, allProjects));
      });

      return descendants;
    };

    const excludeIds = project ? getDescendantIds(project.id, projects) : [];
    return projects.filter(p => !excludeIds.includes(p.id));
  };

  const handleFormSubmit = (data: ProjectCreate | ProjectUpdate) => {
    // Remove parent_project_id if it's empty string
    if (data.parent_project_id === 'none') {
      data.parent_project_id = undefined;
    }

    onSubmit?.(data);
  };

  const availableParents = getAvailableParents();

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>
          {mode === 'create' ? 'Create Project' : 'Edit Project'}
        </CardTitle>
      </CardHeader>

      <form onSubmit={handleSubmit(handleFormSubmit)}>
        <CardContent className="space-y-4">
          {/* Project Name */}
          <div className="space-y-2">
            <Label htmlFor="name">Project Name *</Label>
            <Input
              id="name"
              placeholder="Enter project name"
              {...register('name')}
              className={errors.name ? 'border-red-500' : ''}
            />
            {errors.name && (
              <p className="text-sm text-red-500">{errors.name.message}</p>
            )}
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              placeholder="Enter project description (optional)"
              rows={3}
              {...register('description')}
              className={errors.description ? 'border-red-500' : ''}
            />
            {errors.description && (
              <p className="text-sm text-red-500">{errors.description.message}</p>
            )}
          </div>

          {/* Parent Project */}
          <div className="space-y-2">
            <Label htmlFor="parent_project_id">Parent Project</Label>
            <Select
              value={selectedParentId || ''}
              onValueChange={(value) => setValue('parent_project_id', value || undefined)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select parent project (optional)" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">No parent (root project)</SelectItem>
                {availableParents.map((p) => (
                  <SelectItem key={p.id} value={p.id}>
                    {p.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.parent_project_id && (
              <p className="text-sm text-red-500">{errors.parent_project_id.message}</p>
            )}
          </div>

          {/* Show parent info if creating a subproject */}
          {parentProject && mode === 'create' && (
            <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-md">
              <p className="text-sm text-blue-700 dark:text-blue-300">
                Creating subproject under: <strong>{parentProject.name}</strong>
              </p>
            </div>
          )}
        </CardContent>

        <CardFooter className="flex gap-2">
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={isSubmitting || isLoading}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={isSubmitting || isLoading}
          >
            {isSubmitting || isLoading
              ? mode === 'create'
                ? 'Creating...'
                : 'Updating...'
              : mode === 'create'
                ? 'Create Project'
                : 'Update Project'
            }
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
};

export default ProjectForm;
