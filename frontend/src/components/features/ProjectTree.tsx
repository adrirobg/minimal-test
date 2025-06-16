'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogTrigger } from '@/components/ui/dialog';
import { 
  Search, Plus, Folder, FolderOpen, FileText, Edit, Trash2, 
  ChevronRight, ChevronDown, MoreHorizontal, Filter, SortAsc
} from 'lucide-react';
import { TreeView } from '@/components/pkm/TreeView';
import { ProjectForm } from '@/components/forms/ProjectForm';
import { NoteEditor } from '@/components/features/NoteEditor';
import { Project, ProjectNode, ProjectCreate, ProjectUpdate } from '@/types/project';
import { Note, NoteCreate } from '@/types/note';
import { useProjectsStore } from '@/lib/store/projects';
import { apiClient } from '@/lib/api/client';

interface ProjectTreeProps {
  onSelectProject?: (project: Project) => void;
  onSelectNote?: (note: Note) => void;
  selectedProjectId?: string;
  selectedNoteId?: string;
  showNotes?: boolean;
  className?: string;
}

interface ProjectTreeItemProps {
  project: Project;
  level: number;
  isExpanded: boolean;
  onToggleExpand: (projectId: string) => void;
  onSelectProject: (project: Project) => void;
  onEditProject: (project: Project) => void;
  onDeleteProject: (project: Project) => void;
  onCreateSubproject: (parentProject: Project) => void;
  onCreateNote: (project: Project) => void;
  selectedProjectId?: string;
  selectedNoteId?: string;
  showNotes: boolean;
  notes: Note[];
  onSelectNote: (note: Note) => void;
}

const ProjectTreeItem: React.FC<ProjectTreeItemProps> = ({
  project,
  level,
  isExpanded,
  onToggleExpand,
  onSelectProject,
  onEditProject,
  onDeleteProject,
  onCreateSubproject,
  onCreateNote,
  selectedProjectId,
  selectedNoteId,
  showNotes,
  notes,
  onSelectNote
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const projectNotes = notes.filter(note => note.project_id === project.id);
  const hasSubprojects = project.children && project.children.length > 0;
  const hasContent = hasSubprojects || (showNotes && projectNotes.length > 0);
  const isSelected = selectedProjectId === project.id;

  const handleToggle = () => {
    if (hasContent) {
      onToggleExpand(project.id);
    }
  };

  return (
    <div className="select-none">
      {/* Project Item */}
      <div
        className={`
          flex items-center py-2 px-2 rounded-md cursor-pointer group
          hover:bg-gray-100 dark:hover:bg-gray-800
          ${isSelected ? 'bg-blue-100 dark:bg-blue-900 border-l-4 border-blue-500' : ''}
        `}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        onClick={() => onSelectProject(project)}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {/* Expand/Collapse Button */}
        <Button
          variant="ghost"
          size="sm"
          className="h-6 w-6 p-0 mr-2"
          onClick={(e) => {
            e.stopPropagation();
            handleToggle();
          }}
        >
          {hasContent ? (
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
          {hasSubprojects ? (
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
        <span className="flex-1 text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
          {project.name}
        </span>

        {/* Note Count */}
        {showNotes && projectNotes.length > 0 && (
          <span className="text-xs text-gray-500 bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded-full mr-2">
            {projectNotes.length}
          </span>
        )}

        {/* Action Buttons */}
        {(isHovered || isSelected) && (
          <div className="flex items-center space-x-1 opacity-100 group-hover:opacity-100">
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={(e) => {
                e.stopPropagation();
                onCreateNote(project);
              }}
              title="Add note"
            >
              <FileText className="h-3 w-3" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={(e) => {
                e.stopPropagation();
                onCreateSubproject(project);
              }}
              title="Add subproject"
            >
              <Plus className="h-3 w-3" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={(e) => {
                e.stopPropagation();
                onEditProject(project);
              }}
              title="Edit project"
            >
              <Edit className="h-3 w-3" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0 text-red-600 hover:text-red-700"
              onClick={(e) => {
                e.stopPropagation();
                onDeleteProject(project);
              }}
              title="Delete project"
            >
              <Trash2 className="h-3 w-3" />
            </Button>
          </div>
        )}
      </div>

      {/* Expanded Content */}
      {isExpanded && hasContent && (
        <div>
          {/* Subprojects */}
          {project.children?.map((child) => (
            <ProjectTreeItem
              key={child.id}
              project={child}
              level={level + 1}
              isExpanded={isExpanded}
              onToggleExpand={onToggleExpand}
              onSelectProject={onSelectProject}
              onEditProject={onEditProject}
              onDeleteProject={onDeleteProject}
              onCreateSubproject={onCreateSubproject}
              onCreateNote={onCreateNote}
              selectedProjectId={selectedProjectId}
              selectedNoteId={selectedNoteId}
              showNotes={showNotes}
              notes={notes}
              onSelectNote={onSelectNote}
            />
          ))}

          {/* Project Notes */}
          {showNotes && projectNotes.map((note) => (
            <div
              key={note.id}
              className={`
                flex items-center py-2 px-2 rounded-md cursor-pointer
                hover:bg-gray-50 dark:hover:bg-gray-700
                ${selectedNoteId === note.id ? 'bg-green-100 dark:bg-green-900 border-l-4 border-green-500' : ''}
              `}
              style={{ paddingLeft: `${(level + 1) * 16 + 32}px` }}
              onClick={() => onSelectNote(note)}
            >
              <FileText className="h-4 w-4 text-green-600 mr-2" />
              <span className="flex-1 text-sm text-gray-700 dark:text-gray-300 truncate">
                {note.title || 'Untitled Note'}
              </span>
              <span className="text-xs text-gray-400 ml-2">
                {note.note_type}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export const ProjectTree: React.FC<ProjectTreeProps> = ({
  onSelectProject,
  onSelectNote,
  selectedProjectId,
  selectedNoteId,
  showNotes = true,
  className = ''
}) => {
  const { projects, isLoading, fetchProjects } = useProjectsStore();
  const [expandedProjects, setExpandedProjects] = useState<Set<string>>(new Set());
  const [searchTerm, setSearchTerm] = useState('');
  const [notes, setNotes] = useState<Note[]>([]);
  const [isCreateProjectOpen, setIsCreateProjectOpen] = useState(false);
  const [isCreateNoteOpen, setIsCreateNoteOpen] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [parentForNewProject, setParentForNewProject] = useState<Project | null>(null);
  const [projectForNewNote, setProjectForNewNote] = useState<Project | null>(null);

  useEffect(() => {
    fetchProjects();
    if (showNotes) {
      loadNotes();
    }
  }, [fetchProjects, showNotes]);

  const loadNotes = async () => {
    try {
      const response = await apiClient.get('/v1/notes/?limit=1000');
      setNotes(response.items || []);
    } catch (error) {
      console.error('Failed to load notes:', error);
    }
  };

  const handleToggleExpand = (projectId: string) => {
    setExpandedProjects(prev => {
      const newSet = new Set(prev);
      if (newSet.has(projectId)) {
        newSet.delete(projectId);
      } else {
        newSet.add(projectId);
      }
      return newSet;
    });
  };

  const handleCreateProject = async (data: ProjectCreate) => {
    try {
      await apiClient.post('/v1/projects/', data);
      await fetchProjects();
      setIsCreateProjectOpen(false);
      setParentForNewProject(null);
    } catch (error) {
      console.error('Failed to create project:', error);
    }
  };

  const handleUpdateProject = async (data: ProjectUpdate) => {
    if (!editingProject) return;
    
    try {
      await apiClient.put(`/v1/projects/${editingProject.id}`, data);
      await fetchProjects();
      setEditingProject(null);
    } catch (error) {
      console.error('Failed to update project:', error);
    }
  };

  const handleDeleteProject = async (project: Project) => {
    if (window.confirm(`Are you sure you want to delete "${project.name}"? This action cannot be undone.`)) {
      try {
        await apiClient.delete(`/v1/projects/${project.id}`);
        await fetchProjects();
      } catch (error) {
        console.error('Failed to delete project:', error);
      }
    }
  };

  const handleCreateNote = async (data: NoteCreate) => {
    try {
      await apiClient.post('/v1/notes/', data);
      await loadNotes();
      setIsCreateNoteOpen(false);
      setProjectForNewNote(null);
    } catch (error) {
      console.error('Failed to create note:', error);
    }
  };

  const buildProjectTree = (projects: Project[]): Project[] => {
    const projectMap = new Map<string, Project>();
    const rootProjects: Project[] = [];

    // First pass: create map and initialize children arrays
    projects.forEach(project => {
      projectMap.set(project.id, { ...project, children: [] });
    });

    // Second pass: build tree structure
    projects.forEach(project => {
      const projectWithChildren = projectMap.get(project.id)!;
      
      if (project.parent_project_id && projectMap.has(project.parent_project_id)) {
        const parent = projectMap.get(project.parent_project_id)!;
        parent.children!.push(projectWithChildren);
      } else {
        rootProjects.push(projectWithChildren);
      }
    });

    return rootProjects;
  };

  const filterProjects = (projects: Project[], searchTerm: string): Project[] => {
    if (!searchTerm) return projects;

    const filtered: Project[] = [];
    const searchLower = searchTerm.toLowerCase();

    const checkProject = (project: Project): boolean => {
      const matchesName = project.name.toLowerCase().includes(searchLower);
      const matchesDescription = project.description?.toLowerCase().includes(searchLower) || false;
      const childrenMatch = project.children?.some(checkProject) || false;

      if (matchesName || matchesDescription || childrenMatch) {
        const filteredChildren = project.children?.filter(checkProject) || [];
        filtered.push({ ...project, children: filteredChildren });
        return true;
      }

      return false;
    };

    projects.forEach(checkProject);
    return filtered;
  };

  const projectTree = buildProjectTree(projects);
  const filteredProjects = filterProjects(projectTree, searchTerm);

  if (isLoading) {
    return (
      <Card className={className}>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Folder className="h-5 w-5" />
            Projects
          </CardTitle>
          <Button
            size="sm"
            onClick={() => setIsCreateProjectOpen(true)}
          >
            <Plus className="h-4 w-4 mr-2" />
            New Project
          </Button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search projects..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        {filteredProjects.length === 0 ? (
          <div className="text-center py-8">
            <Folder className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400">
              {searchTerm ? 'No projects match your search' : 'No projects found'}
            </p>
            {!searchTerm && (
              <Button
                className="mt-4"
                onClick={() => setIsCreateProjectOpen(true)}
              >
                <Plus className="mr-2 h-4 w-4" />
                Create Your First Project
              </Button>
            )}
          </div>
        ) : (
          <div className="space-y-1">
            {filteredProjects.map((project) => (
              <ProjectTreeItem
                key={project.id}
                project={project}
                level={0}
                isExpanded={expandedProjects.has(project.id)}
                onToggleExpand={handleToggleExpand}
                onSelectProject={(p) => onSelectProject?.(p)}
                onEditProject={setEditingProject}
                onDeleteProject={handleDeleteProject}
                onCreateSubproject={(parent) => {
                  setParentForNewProject(parent);
                  setIsCreateProjectOpen(true);
                }}
                onCreateNote={(project) => {
                  setProjectForNewNote(project);
                  setIsCreateNoteOpen(true);
                }}
                selectedProjectId={selectedProjectId}
                selectedNoteId={selectedNoteId}
                showNotes={showNotes}
                notes={notes}
                onSelectNote={(note) => onSelectNote?.(note)}
              />
            ))}
          </div>
        )}
      </CardContent>

      {/* Create Project Dialog */}
      <Dialog open={isCreateProjectOpen} onOpenChange={setIsCreateProjectOpen}>
        <DialogContent>
          <ProjectForm
            mode="create"
            parentProject={parentForNewProject || undefined}
            onSubmit={handleCreateProject}
            onCancel={() => {
              setIsCreateProjectOpen(false);
              setParentForNewProject(null);
            }}
          />
        </DialogContent>
      </Dialog>

      {/* Edit Project Dialog */}
      <Dialog open={!!editingProject} onOpenChange={(open) => !open && setEditingProject(null)}>
        <DialogContent>
          {editingProject && (
            <ProjectForm
              mode="edit"
              project={editingProject}
              onSubmit={handleUpdateProject}
              onCancel={() => setEditingProject(null)}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Create Note Dialog */}
      <Dialog open={isCreateNoteOpen} onOpenChange={setIsCreateNoteOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          {projectForNewNote && (
            <NoteEditor
              mode="create"
              projects={projects}
              defaultProjectId={projectForNewNote.id}
              onSave={handleCreateNote}
              onCancel={() => {
                setIsCreateNoteOpen(false);
                setProjectForNewNote(null);
              }}
            />
          )}
        </DialogContent>
      </Dialog>
    </Card>
  );
};

export default ProjectTree;