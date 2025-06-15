'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Search, Filter, FileText, Folder, BookOpen, Tags, 
  Calendar, User, SortAsc, SortDesc, X, ArrowRight
} from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { Note } from '@/types/note';
import { Project } from '@/types/project';
import { Source } from '@/types/source';
import { Keyword } from '@/types/keyword';
import Link from 'next/link';

interface SearchFilters {
  query: string;
  type: 'all' | 'notes' | 'projects' | 'sources';
  project_id?: string;
  keyword_id?: string;
  note_type?: string;
  date_from?: string;
  date_to?: string;
}

interface SearchResult {
  type: 'note' | 'project' | 'source';
  id: string;
  title: string;
  content?: string;
  project_name?: string;
  created_at: string;
  updated_at: string;
  keywords?: string[];
  note_type?: string;
  relevance?: number;
}

const ITEMS_PER_PAGE = 20;

export default function SearchPage() {
  const [filters, setFilters] = useState<SearchFilters>({
    query: '',
    type: 'all'
  });
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [totalResults, setTotalResults] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [sortBy, setSortBy] = useState<'relevance' | 'date_desc' | 'date_asc' | 'title'>('relevance');
  
  // Data for filters
  const [projects, setProjects] = useState<Project[]>([]);
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  const [isFiltersExpanded, setIsFiltersExpanded] = useState(false);

  // Load filter data
  useEffect(() => {
    loadFilterData();
  }, []);

  // Perform search when filters change
  useEffect(() => {
    if (filters.query.trim().length >= 2) {
      performSearch();
    } else {
      setResults([]);
      setTotalResults(0);
    }
  }, [filters, currentPage, sortBy]);

  const loadFilterData = async () => {
    try {
      const [projectsRes, keywordsRes] = await Promise.allSettled([
        apiClient.get('/v1/projects/?limit=1000'),
        apiClient.get('/v1/keywords/?limit=1000')
      ]);

      if (projectsRes.status === 'fulfilled') {
        setProjects(projectsRes.value.items || []);
      }
      if (keywordsRes.status === 'fulfilled') {
        setKeywords(keywordsRes.value.items || []);
      }
    } catch (error) {
      console.error('Failed to load filter data:', error);
    }
  };

  const performSearch = async () => {
    setIsLoading(true);
    try {
      const searchParams = new URLSearchParams({
        q: filters.query,
        limit: ITEMS_PER_PAGE.toString(),
        offset: ((currentPage - 1) * ITEMS_PER_PAGE).toString(),
        sort: sortBy
      });

      if (filters.type !== 'all') {
        searchParams.append('type', filters.type);
      }
      if (filters.project_id) {
        searchParams.append('project_id', filters.project_id);
      }
      if (filters.keyword_id) {
        searchParams.append('keyword_id', filters.keyword_id);
      }
      if (filters.note_type) {
        searchParams.append('note_type', filters.note_type);
      }
      if (filters.date_from) {
        searchParams.append('date_from', filters.date_from);
      }
      if (filters.date_to) {
        searchParams.append('date_to', filters.date_to);
      }

      // For now, we'll search across different endpoints
      const searchResults: SearchResult[] = [];
      let total = 0;

      // Search notes
      if (filters.type === 'all' || filters.type === 'notes') {
        try {
          const notesResponse = await apiClient.get(`/v1/notes/search?${searchParams.toString()}`);
          const notes = notesResponse.items || [];
          
          searchResults.push(...notes.map((note: Note) => ({
            type: 'note' as const,
            id: note.id,
            title: note.title,
            content: note.content.substring(0, 200) + (note.content.length > 200 ? '...' : ''),
            project_name: projects.find(p => p.id === note.project_id)?.name,
            created_at: note.created_at,
            updated_at: note.updated_at,
            note_type: note.note_type,
            keywords: note.keywords?.map(k => k.name) || [],
            relevance: calculateRelevance(filters.query, note.title, note.content)
          })));
          
          total += notesResponse.total || 0;
        } catch (error) {
          // Fallback: search all notes and filter locally
          try {
            const allNotesResponse = await apiClient.get('/v1/notes/?limit=1000');
            const notes = (allNotesResponse.items || []).filter((note: Note) =>
              note.title.toLowerCase().includes(filters.query.toLowerCase()) ||
              note.content.toLowerCase().includes(filters.query.toLowerCase())
            );

            searchResults.push(...notes.map((note: Note) => ({
              type: 'note' as const,
              id: note.id,
              title: note.title,
              content: note.content.substring(0, 200) + (note.content.length > 200 ? '...' : ''),
              project_name: projects.find(p => p.id === note.project_id)?.name,
              created_at: note.created_at,
              updated_at: note.updated_at,
              note_type: note.note_type,
              keywords: note.keywords?.map(k => k.name) || [],
              relevance: calculateRelevance(filters.query, note.title, note.content)
            })));

            total += notes.length;
          } catch (fallbackError) {
            console.error('Failed to search notes:', fallbackError);
          }
        }
      }

      // Search projects
      if (filters.type === 'all' || filters.type === 'projects') {
        try {
          const filteredProjects = projects.filter(project =>
            project.name.toLowerCase().includes(filters.query.toLowerCase()) ||
            (project.description && project.description.toLowerCase().includes(filters.query.toLowerCase()))
          );

          searchResults.push(...filteredProjects.map((project: Project) => ({
            type: 'project' as const,
            id: project.id,
            title: project.name,
            content: project.description || '',
            created_at: project.created_at,
            updated_at: project.updated_at,
            relevance: calculateRelevance(filters.query, project.name, project.description || '')
          })));

          total += filteredProjects.length;
        } catch (error) {
          console.error('Failed to search projects:', error);
        }
      }

      // Search sources
      if (filters.type === 'all' || filters.type === 'sources') {
        try {
          const sourcesResponse = await apiClient.get('/v1/sources/?limit=1000');
          const sources = (sourcesResponse.items || []).filter((source: Source) =>
            source.title.toLowerCase().includes(filters.query.toLowerCase()) ||
            (source.description && source.description.toLowerCase().includes(filters.query.toLowerCase()))
          );

          searchResults.push(...sources.map((source: Source) => ({
            type: 'source' as const,
            id: source.id,
            title: source.title,
            content: source.description || '',
            created_at: source.created_at,
            updated_at: source.updated_at,
            relevance: calculateRelevance(filters.query, source.title, source.description || '')
          })));

          total += sources.length;
        } catch (error) {
          console.error('Failed to search sources:', error);
        }
      }

      // Apply sorting
      const sortedResults = sortResults(searchResults, sortBy);
      
      setResults(sortedResults);
      setTotalResults(total);
    } catch (error) {
      console.error('Search failed:', error);
      setResults([]);
      setTotalResults(0);
    } finally {
      setIsLoading(false);
    }
  };

  const calculateRelevance = (query: string, title: string, content: string): number => {
    const queryLower = query.toLowerCase();
    const titleLower = title.toLowerCase();
    const contentLower = content.toLowerCase();

    let score = 0;

    // Title matches are more important
    if (titleLower.includes(queryLower)) {
      score += 10;
      if (titleLower.startsWith(queryLower)) {
        score += 5; // Prefix match bonus
      }
    }

    // Content matches
    const contentMatches = (contentLower.match(new RegExp(queryLower, 'g')) || []).length;
    score += contentMatches * 2;

    // Word boundary matches
    const wordBoundaryRegex = new RegExp(`\\b${queryLower}\\b`, 'gi');
    if (titleLower.match(wordBoundaryRegex)) score += 5;
    if (contentLower.match(wordBoundaryRegex)) score += 3;

    return score;
  };

  const sortResults = (results: SearchResult[], sortBy: string): SearchResult[] => {
    return [...results].sort((a, b) => {
      switch (sortBy) {
        case 'relevance':
          return (b.relevance || 0) - (a.relevance || 0);
        case 'date_desc':
          return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
        case 'date_asc':
          return new Date(a.updated_at).getTime() - new Date(b.updated_at).getTime();
        case 'title':
          return a.title.localeCompare(b.title);
        default:
          return 0;
      }
    });
  };

  const updateFilter = (key: keyof SearchFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setCurrentPage(1); // Reset to first page when filters change
  };

  const clearFilters = () => {
    setFilters({
      query: filters.query, // Keep the search query
      type: 'all'
    });
    setCurrentPage(1);
  };

  const getResultIcon = (type: string) => {
    switch (type) {
      case 'note':
        return FileText;
      case 'project':
        return Folder;
      case 'source':
        return BookOpen;
      default:
        return FileText;
    }
  };

  const getResultLink = (result: SearchResult) => {
    switch (result.type) {
      case 'note':
        return `/notes/${result.id}`;
      case 'project':
        return `/projects/${result.id}`;
      case 'source':
        return `/sources/${result.id}`;
      default:
        return '#';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
    
    if (diffInDays === 0) return 'Today';
    if (diffInDays === 1) return 'Yesterday';
    if (diffInDays < 7) return `${diffInDays} days ago`;
    if (diffInDays < 30) return `${Math.floor(diffInDays / 7)} weeks ago`;
    return date.toLocaleDateString();
  };

  const totalPages = Math.ceil(totalResults / ITEMS_PER_PAGE);

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Search Knowledge Base
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400">
          Find notes, projects, and sources across your knowledge management system
        </p>
      </div>

      {/* Search Bar */}
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search for notes, projects, sources..."
                value={filters.query}
                onChange={(e) => updateFilter('query', e.target.value)}
                className="pl-10 text-lg h-12"
              />
            </div>
            <Button
              variant="outline"
              onClick={() => setIsFiltersExpanded(!isFiltersExpanded)}
              className="h-12"
            >
              <Filter className="h-4 w-4 mr-2" />
              Filters
              {Object.keys(filters).filter(key => key !== 'query' && filters[key as keyof SearchFilters]).length > 0 && (
                <span className="ml-2 bg-blue-600 text-white text-xs rounded-full px-2 py-1">
                  {Object.keys(filters).filter(key => key !== 'query' && filters[key as keyof SearchFilters]).length}
                </span>
              )}
            </Button>
          </div>

          {/* Advanced Filters */}
          {isFiltersExpanded && (
            <div className="mt-6 pt-6 border-t grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Content Type */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Content Type</label>
                <Select value={filters.type} onValueChange={(value) => updateFilter('type', value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    <SelectItem value="notes">Notes</SelectItem>
                    <SelectItem value="projects">Projects</SelectItem>
                    <SelectItem value="sources">Sources</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Project */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Project</label>
                <Select value={filters.project_id || ''} onValueChange={(value) => updateFilter('project_id', value || undefined)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Any project" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Any project</SelectItem>
                    {projects.map((project) => (
                      <SelectItem key={project.id} value={project.id}>
                        {project.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Keyword */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Keyword</label>
                <Select value={filters.keyword_id || ''} onValueChange={(value) => updateFilter('keyword_id', value || undefined)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Any keyword" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Any keyword</SelectItem>
                    {keywords.map((keyword) => (
                      <SelectItem key={keyword.id} value={keyword.id}>
                        {keyword.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Note Type */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Note Type</label>
                <Select value={filters.note_type || ''} onValueChange={(value) => updateFilter('note_type', value || undefined)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Any note type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Any note type</SelectItem>
                    <SelectItem value="text">Text</SelectItem>
                    <SelectItem value="markdown">Markdown</SelectItem>
                    <SelectItem value="code">Code</SelectItem>
                    <SelectItem value="meeting">Meeting</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Clear Filters */}
              <div className="flex items-end">
                <Button variant="outline" onClick={clearFilters} className="w-full">
                  <X className="h-4 w-4 mr-2" />
                  Clear Filters
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Search Results */}
      {filters.query.trim().length >= 2 && (
        <div className="space-y-6">
          {/* Results Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h2 className="text-xl font-semibold">
                {isLoading ? 'Searching...' : `${totalResults} results found`}
              </h2>
              {totalResults > 0 && (
                <Select value={sortBy} onValueChange={(value) => setSortBy(value as any)}>
                  <SelectTrigger className="w-48">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="relevance">Most Relevant</SelectItem>
                    <SelectItem value="date_desc">Newest First</SelectItem>
                    <SelectItem value="date_asc">Oldest First</SelectItem>
                    <SelectItem value="title">Alphabetical</SelectItem>
                  </SelectContent>
                </Select>
              )}
            </div>
          </div>

          {/* Results List */}
          {isLoading ? (
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <Card key={i} className="animate-pulse">
                  <CardContent className="p-6">
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-full"></div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : results.length > 0 ? (
            <div className="space-y-4">
              {results.map((result) => {
                const Icon = getResultIcon(result.type);
                
                return (
                  <Card key={`${result.type}-${result.id}`} className="hover:shadow-lg transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-start gap-4">
                        <div className={`p-2 rounded-lg ${
                          result.type === 'note' ? 'bg-blue-100 text-blue-600' :
                          result.type === 'project' ? 'bg-green-100 text-green-600' :
                          'bg-purple-100 text-purple-600'
                        }`}>
                          <Icon className="h-5 w-5" />
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-2">
                            <Link 
                              href={getResultLink(result)}
                              className="text-lg font-semibold text-gray-900 dark:text-white hover:text-blue-600 transition-colors"
                            >
                              {result.title}
                            </Link>
                            <span className="text-xs bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded capitalize">
                              {result.type}
                            </span>
                            {result.note_type && (
                              <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                                {result.note_type}
                              </span>
                            )}
                          </div>
                          
                          {result.content && (
                            <p className="text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
                              {result.content}
                            </p>
                          )}
                          
                          <div className="flex items-center gap-4 text-sm text-gray-500">
                            {result.project_name && (
                              <span className="flex items-center gap-1">
                                <Folder className="h-3 w-3" />
                                {result.project_name}
                              </span>
                            )}
                            <span className="flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              {formatDate(result.updated_at)}
                            </span>
                            {result.keywords && result.keywords.length > 0 && (
                              <span className="flex items-center gap-1">
                                <Tags className="h-3 w-3" />
                                {result.keywords.slice(0, 3).join(', ')}
                                {result.keywords.length > 3 && '...'}
                              </span>
                            )}
                          </div>
                        </div>
                        
                        <Link href={getResultLink(result)}>
                          <Button variant="ghost" size="sm">
                            <ArrowRight className="h-4 w-4" />
                          </Button>
                        </Link>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          ) : (
            <Card>
              <CardContent className="p-12 text-center">
                <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  No results found
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Try adjusting your search terms or filters to find what you're looking for.
                </p>
              </CardContent>
            </Card>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-8">
              <Button
                variant="outline"
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
              >
                Previous
              </Button>
              
              <div className="flex items-center gap-1">
                {[...Array(Math.min(totalPages, 5))].map((_, i) => {
                  const page = i + 1;
                  return (
                    <Button
                      key={page}
                      variant={currentPage === page ? "default" : "outline"}
                      size="sm"
                      onClick={() => setCurrentPage(page)}
                    >
                      {page}
                    </Button>
                  );
                })}
                {totalPages > 5 && <span>...</span>}
              </div>
              
              <Button
                variant="outline"
                onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
              >
                Next
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {filters.query.trim().length < 2 && (
        <Card>
          <CardContent className="p-12 text-center">
            <Search className="h-16 w-16 text-gray-400 mx-auto mb-6" />
            <h3 className="text-xl font-medium text-gray-900 dark:text-white mb-3">
              Search Your Knowledge Base
            </h3>
            <p className="text-gray-600 dark:text-gray-400 max-w-md mx-auto">
              Enter at least 2 characters to start searching through your notes, projects, and sources.
              Use filters to narrow down your results.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}