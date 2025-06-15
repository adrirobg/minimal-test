'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { 
  Bold, Italic, Underline, List, ListOrdered, Link2, 
  Save, X, Eye, Edit3, AlignLeft, AlignCenter, AlignRight,
  Heading1, Heading2, Heading3, Code, Quote, FileText
} from 'lucide-react';
import { Note, NoteCreate, NoteUpdate, NoteCreateSchema, NoteUpdateSchema } from '@/types/note';
import { Project } from '@/types/project';

interface NoteEditorProps {
  mode: 'create' | 'edit' | 'view';
  note?: Note;
  projects?: Project[];
  defaultProjectId?: string;
  onSave?: (data: NoteCreate | NoteUpdate) => void;
  onCancel?: () => void;
  onEdit?: () => void;
  isLoading?: boolean;
  className?: string;
}

interface ToolbarButtonProps {
  onClick: () => void;
  icon: React.ComponentType<{ className?: string }>;
  tooltip: string;
  isActive?: boolean;
  disabled?: boolean;
}

const ToolbarButton: React.FC<ToolbarButtonProps> = ({ 
  onClick, icon: Icon, tooltip, isActive = false, disabled = false 
}) => (
  <Button
    type="button"
    variant={isActive ? "default" : "ghost"}
    size="sm"
    onClick={onClick}
    title={tooltip}
    disabled={disabled}
    className="h-8 w-8 p-0"
  >
    <Icon className="h-4 w-4" />
  </Button>
);

export const NoteEditor: React.FC<NoteEditorProps> = ({
  mode,
  note,
  projects = [],
  defaultProjectId,
  onSave,
  onCancel,
  onEdit,
  isLoading = false,
  className = ''
}) => {
  const [isPreviewMode, setIsPreviewMode] = useState(mode === 'view');
  const [content, setContent] = useState(note?.content || '');
  const contentRef = useRef<HTMLTextAreaElement>(null);

  const schema = mode === 'create' ? NoteCreateSchema : NoteUpdateSchema;

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting, isDirty }
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

  const watchedContent = watch('content');

  useEffect(() => {
    setContent(watchedContent || '');
  }, [watchedContent]);

  const insertTextAtCursor = (before: string, after: string = '') => {
    const textarea = contentRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = content.substring(start, end);
    const newText = before + selectedText + after;
    
    const newContent = content.substring(0, start) + newText + content.substring(end);
    setContent(newContent);
    setValue('content', newContent);

    // Set cursor position after the inserted text
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(start + before.length, start + before.length + selectedText.length);
    }, 0);
  };

  const handleToolbarAction = (action: string) => {
    switch (action) {
      case 'bold':
        insertTextAtCursor('**', '**');
        break;
      case 'italic':
        insertTextAtCursor('*', '*');
        break;
      case 'underline':
        insertTextAtCursor('<u>', '</u>');
        break;
      case 'heading1':
        insertTextAtCursor('# ');
        break;
      case 'heading2':
        insertTextAtCursor('## ');
        break;
      case 'heading3':
        insertTextAtCursor('### ');
        break;
      case 'list':
        insertTextAtCursor('- ');
        break;
      case 'orderedList':
        insertTextAtCursor('1. ');
        break;
      case 'link':
        insertTextAtCursor('[', '](url)');
        break;
      case 'code':
        insertTextAtCursor('`', '`');
        break;
      case 'quote':
        insertTextAtCursor('> ');
        break;
      default:
        break;
    }
  };

  const formatMarkdownContent = (text: string): string => {
    return text
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
      .replace(/\*(.*)\*/gim, '<em>$1</em>')
      .replace(/<u>(.*)<\/u>/gim, '<u>$1</u>')
      .replace(/`(.*)`/gim, '<code>$1</code>')
      .replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>')
      .replace(/^- (.*$)/gim, '<li>$1</li>')
      .replace(/^\d+\. (.*$)/gim, '<li>$1</li>')
      .replace(/\[([^\]]+)\]\(([^)]+)\)/gim, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
      .replace(/\n/g, '<br>');
  };

  const handleFormSubmit = (data: NoteCreate | NoteUpdate) => {
    onSave?.(data);
  };

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newContent = e.target.value;
    setContent(newContent);
    setValue('content', newContent);
  };

  if (mode === 'view' && note) {
    return (
      <Card className={`w-full ${className}`}>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-2xl">{note.title}</CardTitle>
            <div className="flex items-center gap-4 text-sm text-gray-500 mt-2">
              <span>Type: {note.note_type}</span>
              <span>Created: {new Date(note.created_at).toLocaleDateString()}</span>
              {note.updated_at !== note.created_at && (
                <span>Updated: {new Date(note.updated_at).toLocaleDateString()}</span>
              )}
            </div>
          </div>
          <Button onClick={onEdit} variant="outline">
            <Edit3 className="h-4 w-4 mr-2" />
            Edit
          </Button>
        </CardHeader>
        <CardContent>
          <div 
            className="prose max-w-none dark:prose-invert"
            dangerouslySetInnerHTML={{ __html: formatMarkdownContent(note.content) }}
          />
          {note.keywords && note.keywords.length > 0 && (
            <div className="mt-6 pt-4 border-t">
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Keywords:</h4>
              <div className="flex flex-wrap gap-2">
                {note.keywords.map((keyword) => (
                  <span
                    key={keyword.id}
                    className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded-md"
                  >
                    {keyword.name}
                  </span>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`w-full ${className}`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          {mode === 'create' ? 'Create New Note' : 'Edit Note'}
        </CardTitle>
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
              value={watch('project_id') || ''}
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
              value={watch('note_type') || 'text'}
              onValueChange={(value) => setValue('note_type', value as 'text' | 'markdown' | 'code' | 'meeting')}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="text">Text</SelectItem>
                <SelectItem value="markdown">Markdown</SelectItem>
                <SelectItem value="code">Code</SelectItem>
                <SelectItem value="meeting">Meeting Notes</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Content Editor */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label>Content *</Label>
              <div className="flex items-center gap-2">
                <Button
                  type="button"
                  variant={isPreviewMode ? "default" : "outline"}
                  size="sm"
                  onClick={() => setIsPreviewMode(!isPreviewMode)}
                >
                  <Eye className="h-4 w-4 mr-2" />
                  {isPreviewMode ? 'Edit' : 'Preview'}
                </Button>
              </div>
            </div>

            {!isPreviewMode && (
              <>
                {/* Toolbar */}
                <div className="flex flex-wrap gap-1 p-2 border border-gray-200 dark:border-gray-700 rounded-t-md bg-gray-50 dark:bg-gray-800">
                  <ToolbarButton onClick={() => handleToolbarAction('heading1')} icon={Heading1} tooltip="Heading 1" />
                  <ToolbarButton onClick={() => handleToolbarAction('heading2')} icon={Heading2} tooltip="Heading 2" />
                  <ToolbarButton onClick={() => handleToolbarAction('heading3')} icon={Heading3} tooltip="Heading 3" />
                  <div className="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-1" />
                  <ToolbarButton onClick={() => handleToolbarAction('bold')} icon={Bold} tooltip="Bold" />
                  <ToolbarButton onClick={() => handleToolbarAction('italic')} icon={Italic} tooltip="Italic" />
                  <ToolbarButton onClick={() => handleToolbarAction('underline')} icon={Underline} tooltip="Underline" />
                  <div className="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-1" />
                  <ToolbarButton onClick={() => handleToolbarAction('list')} icon={List} tooltip="Bullet List" />
                  <ToolbarButton onClick={() => handleToolbarAction('orderedList')} icon={ListOrdered} tooltip="Numbered List" />
                  <ToolbarButton onClick={() => handleToolbarAction('quote')} icon={Quote} tooltip="Quote" />
                  <div className="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-1" />
                  <ToolbarButton onClick={() => handleToolbarAction('link')} icon={Link2} tooltip="Link" />
                  <ToolbarButton onClick={() => handleToolbarAction('code')} icon={Code} tooltip="Code" />
                </div>

                {/* Content Textarea */}
                <Textarea
                  ref={contentRef}
                  placeholder="Start writing your note..."
                  value={content}
                  onChange={handleContentChange}
                  className={`min-h-64 rounded-t-none ${errors.content ? 'border-red-500' : ''}`}
                  rows={12}
                />
              </>
            )}

            {isPreviewMode && (
              <div className="min-h-64 p-4 border border-gray-200 dark:border-gray-700 rounded-md bg-white dark:bg-gray-900">
                <div 
                  className="prose max-w-none dark:prose-invert"
                  dangerouslySetInnerHTML={{ __html: formatMarkdownContent(content || 'No content to preview...') }}
                />
              </div>
            )}

            {errors.content && (
              <p className="text-sm text-red-500">{errors.content.message}</p>
            )}
          </div>

          {/* Save indicator */}
          {isDirty && (
            <div className="flex items-center gap-2 text-sm text-amber-600 dark:text-amber-400">
              <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse" />
              You have unsaved changes
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

export default NoteEditor;