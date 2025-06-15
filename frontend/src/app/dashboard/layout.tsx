'use client';

import React, { useState } from 'react';
import { ProjectTree } from '@/components/features/ProjectTree';
import { TwoColumnLayout } from '@/components/layout/ResizablePanels';
import { Note } from '@/types/note';
import { Project } from '@/types/project';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);

  const handleSelectProject = (project: Project) => {
    setSelectedProject(project);
    setSelectedNote(null); // Clear note selection when project changes
  };

  const handleSelectNote = (note: Note) => {
    setSelectedNote(note);
  };

  return (
    <div className="h-full">
      <TwoColumnLayout
        left={
          <div className="h-full p-4">
            <ProjectTree
              onSelectProject={handleSelectProject}
              onSelectNote={handleSelectNote}
              selectedProjectId={selectedProject?.id}
              selectedNoteId={selectedNote?.id}
              showNotes={true}
              className="h-full"
            />
          </div>
        }
        right={
          <div className="h-full p-4">
            {children}
          </div>
        }
        defaultSizes={[30, 70]}
        className="h-full"
      />
    </div>
  );
}