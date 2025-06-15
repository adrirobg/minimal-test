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
import { FileText, Save, X } from 'lucide-react';
import { Note, NoteCreate, NoteUpdate, NoteCreateSchema, NoteUpdateSchema } from '@/types/note';
import { Project } from '@/types/project';
import { Keyword } from '@/types/keyword';

interface NoteFormProps {
  mode: 'create' | 'edit';
  note?: Note;
  projects?: Project[];
  keywords?: Keyword[];
  defaultProjectId?: string;
  onSubmit?: (data: NoteCreate | NoteUpdate) => void;
  onCancel?: () => void;
  isLoading?: boolean;
  className?: string;
}

export const NoteForm: React.FC<NoteFormProps> = ({
  mode,
  note,
  projects = [],
  keywords = [],
  defaultProjectId,
  onSubmit,
  onCancel,
  isLoading = false,
  className = ''
}) => {
  const schema = mode === 'create' ? NoteCreateSchema : NoteUpdateSchema;

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting }
  } = useForm<NoteCreate | NoteUpdate>({
    resolver: zodResolver(schema),
    defaultValues: mode === 'edit' && note ? {
      title: note.title,
      content: note.content,
      note_type: note.note_type,
      project_id: note.project_id,
      keywords: note.keywords?.map(k => k.id) || []
    } : {
      title: '',
      content: '',
      note_type: 'text',
      project_id: defaultProjectId || '',
      keywords: []
    }
  });

  const selectedProjectId = watch('project_id');
  const selectedNoteType = watch('note_type');
  const selectedKeywords = watch('keywords') || [];

  const handleFormSubmit = (data: NoteCreate | NoteUpdate) => {
    onSubmit?.(data);
  };

  const handleKeywordToggle = (keywordId: string) => {
    const currentKeywords = selectedKeywords || [];
    const newKeywords = currentKeywords.includes(keywordId)
      ? currentKeywords.filter(id => id !== keywordId)
      : [...currentKeywords, keywordId];
    
    setValue('keywords', newKeywords);
  };

  const selectedProject = projects.find(p => p.id === selectedProjectId);

  return (
    <Card className={`w-full max-w-2xl ${className}`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          {mode === 'create' ? 'Create New Note' : 'Edit Note'}
        </CardTitle>
        {selectedProject && (
          <p className="text-sm text-gray-600 dark:text-gray-400">
            in <strong>{selectedProject.name}</strong>
          </p>
        )}
      </CardHeader>

      <form onSubmit={handleSubmit(handleFormSubmit)}>
        <CardContent className="space-y-4">
          {/* Title */}
          <div className="space-y-2">
            <Label htmlFor="title">Title *</Label>
            <Input
              id="title"
              placeholder="Enter note title"
              {...register('title')}
              className={errors.title ? 'border-red-500' : ''}
            />
            {errors.title && (
              <p className="text-sm text-red-500">{errors.title.message}</p>
            )}
          </div>

          {/* Project Selection */}
          <div className="space-y-2">
            <Label htmlFor="project_id">Project *</Label>
            <Select
              value={selectedProjectId || ''}
              onValueChange={(value) => setValue('project_id', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select a project" />
              </SelectTrigger>
              <SelectContent>
                {projects.map((project) => (
                  <SelectItem key={project.id} value={project.id}>
                    {project.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.project_id && (
              <p className="text-sm text-red-500">{errors.project_id.message}</p>
            )}
          </div>

          {/* Note Type */}
          <div className="space-y-2">
            <Label htmlFor="note_type">Note Type</Label>
            <Select
              value={selectedNoteType || 'text'}
              onValueChange={(value) => setValue('note_type', value as 'text' | 'markdown' | 'code' | 'meeting')}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="text">Text Note</SelectItem>
                <SelectItem value="markdown">Markdown</SelectItem>
                <SelectItem value="code">Code Snippet</SelectItem>
                <SelectItem value="meeting">Meeting Notes</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-gray-500">
              {selectedNoteType === 'text' && 'Plain text note with basic formatting'}
              {selectedNoteType === 'markdown' && 'Rich text with Markdown support'}
              {selectedNoteType === 'code' && 'Code snippets with syntax highlighting'}
              {selectedNoteType === 'meeting' && 'Meeting notes with structured format'}
            </p>
          </div>

          {/* Content */}
          <div className="space-y-2">
            <Label htmlFor="content">Content *</Label>
            <Textarea
              id="content"
              placeholder={
                selectedNoteType === 'markdown' 
                  ? 'Write your content using Markdown syntax...'
                  : selectedNoteType === 'code'
                    ? 'Paste your code here...'
                    : selectedNoteType === 'meeting'
                      ? 'Meeting agenda, notes, and action items...'
                      : 'Start writing your note...'
              }
              rows={8}
              {...register('content')}
              className={`resize-y ${errors.content ? 'border-red-500' : ''}`}
            />
            {errors.content && (
              <p className="text-sm text-red-500">{errors.content.message}</p>
            )}
            
            {selectedNoteType === 'markdown' && (
              <p className="text-xs text-gray-500">
                Supports: **bold**, *italic*, # headers, - lists, [links](url), `code`, &gt; quotes
              </p>
            )}
          </div>

          {/* Keywords */}
          {keywords.length > 0 && (
            <div className="space-y-2">
              <Label>Keywords (optional)</Label>
              <div className="grid grid-cols-2 gap-2 max-h-32 overflow-y-auto p-2 border rounded-md">
                {keywords.map((keyword) => (
                  <label
                    key={keyword.id}
                    className="flex items-center space-x-2 cursor-pointer p-2 rounded hover:bg-gray-50 dark:hover:bg-gray-800"
                  >
                    <input
                      type="checkbox"
                      checked={selectedKeywords.includes(keyword.id)}
                      onChange={() => handleKeywordToggle(keyword.id)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm">{keyword.name}</span>
                  </label>
                ))}
              </div>
              <p className="text-xs text-gray-500">
                Select keywords to help organize and find your note later
              </p>
            </div>
          )}

          {/* Preview for current content */}
          {selectedNoteType === 'meeting' && (
            <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-md">
              <p className="text-sm text-blue-700 dark:text-blue-300 font-medium mb-2">
                Meeting Notes Template:
              </p>
              <div className="text-xs text-blue-600 dark:text-blue-400 space-y-1">
                <div># Meeting Title</div>
                <div>**Date:** {new Date().toLocaleDateString()}</div>
                <div>**Attendees:** </div>
                <div>**Agenda:**</div>
                <div>- Item 1</div>
                <div>- Item 2</div>
                <div>**Notes:**</div>
                <div>**Action Items:**</div>
                <div>- [ ] Task 1</div>
                <div>- [ ] Task 2</div>
              </div>
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
            <X className="h-4 w-4 mr-2" />
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={isSubmitting || isLoading}
          >
            <Save className="h-4 w-4 mr-2" />
            {isSubmitting || isLoading
              ? 'Saving...'
              : mode === 'create'
                ? 'Create Note'
                : 'Save Changes'
            }
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
};

export default NoteForm;