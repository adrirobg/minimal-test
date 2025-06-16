'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import {
  FolderTree,
  FileText,
  Search,
  BookOpen,
  Tags,
  Plus,
  TrendingUp,
  Clock,
  ArrowRight
} from 'lucide-react';
import { useAuthStore } from '@/lib/store/auth';
import { apiClient } from '@/lib/api/client';

interface DashboardStats {
  projects: number;
  notes: number;
  sources: number;
  keywords: number;
}

interface RecentActivity {
  type: 'note' | 'project' | 'source';
  title: string;
  id: string;
  created_at: string;
}

export default function DashboardPage() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState<DashboardStats>({
    projects: 0,
    notes: 0,
    sources: 0,
    keywords: 0,
  });
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      // Load stats from different endpoints
      const [projectsRes, notesRes, sourcesRes, keywordsRes] = await Promise.allSettled([
        apiClient.get('/v1/projects/?limit=1'),
        apiClient.get('/v1/notes/?limit=1'),
        apiClient.get('/v1/sources/?limit=1'),
        apiClient.get('/v1/keywords/?limit=1'),
      ]);

      const newStats: DashboardStats = {
        projects: projectsRes.status === 'fulfilled' ? projectsRes.value.total || 0 : 0,
        notes: notesRes.status === 'fulfilled' ? notesRes.value.total || 0 : 0,
        sources: sourcesRes.status === 'fulfilled' ? sourcesRes.value.total || 0 : 0,
        keywords: keywordsRes.status === 'fulfilled' ? keywordsRes.value.total || 0 : 0,
      };

      setStats(newStats);

      // Load recent notes for activity
      try {
        const recentNotesRes = await apiClient.get('/v1/notes/?limit=5');
        const recentNotes: RecentActivity[] = recentNotesRes.items?.map((note: any) => ({
          type: 'note' as const,
          title: note.title || 'Untitled Note',
          id: note.id,
          created_at: note.created_at,
        })) || [];
        
        setRecentActivity(recentNotes);
      } catch (error) {
        console.error('Failed to load recent activity:', error);
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const quickActions = [
    {
      title: 'Create Project',
      description: 'Start organizing your knowledge',
      icon: FolderTree,
      href: '/projects',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Write Note',
      description: 'Capture your thoughts and ideas',
      icon: FileText,
      href: '/notes',
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Add Source',
      description: 'Track your information sources',
      icon: BookOpen,
      href: '/sources',
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: 'Manage Keywords',
      description: 'Organize with tags and keywords',
      icon: Tags,
      href: '/keywords',
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
  ];

  const statCards = [
    {
      title: 'Projects',
      value: stats.projects,
      icon: FolderTree,
      href: '/projects',
      color: 'text-blue-600',
    },
    {
      title: 'Notes',
      value: stats.notes,
      icon: FileText,
      href: '/notes',
      color: 'text-green-600',
    },
    {
      title: 'Sources',
      value: stats.sources,
      icon: BookOpen,
      href: '/sources',
      color: 'text-purple-600',
    },
    {
      title: 'Keywords',
      value: stats.keywords,
      icon: Tags,
      href: '/keywords',
      color: 'text-orange-600',
    },
  ];

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Welcome back, {user?.full_name?.split(' ')[0] || 'User'}!
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400">
          Here's what's happening with your knowledge management system.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((stat, index) => (
          <Link key={index} href={stat.href}>
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                      {stat.title}
                    </p>
                    <p className="text-3xl font-bold text-gray-900 dark:text-white">
                      {isLoading ? '-' : stat.value}
                    </p>
                  </div>
                  <stat.icon className={`h-8 w-8 ${stat.color}`} />
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
          Quick Actions
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {quickActions.map((action, index) => (
            <Link key={index} href={action.href}>
              <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer group">
                <CardContent className="p-6">
                  <div className={`w-12 h-12 rounded-lg ${action.bgColor} flex items-center justify-center mb-4`}>
                    <action.icon className={`h-6 w-6 ${action.color}`} />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 group-hover:text-blue-600 transition-colors">
                    {action.title}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {action.description}
                  </p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Recent Activity
              </CardTitle>
              <CardDescription>
                Your latest notes and updates
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="space-y-3">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="animate-pulse">
                      <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                      <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                    </div>
                  ))}
                </div>
              ) : recentActivity.length > 0 ? (
                <div className="space-y-4">
                  {recentActivity.map((activity, index) => (
                    <div key={index} className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                      <div className="flex-shrink-0">
                        <FileText className="h-5 w-5 text-blue-600" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {activity.title}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {formatDate(activity.created_at)}
                        </p>
                      </div>
                      <Link href={`/notes/${activity.id}`}>
                        <Button variant="ghost" size="sm">
                          <ArrowRight className="h-4 w-4" />
                        </Button>
                      </Link>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500 dark:text-gray-400">
                    No recent activity. Start by creating your first note!
                  </p>
                  <Link href="/notes">
                    <Button className="mt-4">
                      <Plus className="mr-2 h-4 w-4" />
                      Create Note
                    </Button>
                  </Link>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Quick Stats */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Knowledge Growth
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="text-center">
                  <p className="text-3xl font-bold text-blue-600">
                    {stats.projects + stats.notes + stats.sources + stats.keywords}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Total Items
                  </p>
                </div>
                
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Projects</span>
                    <span className="text-sm font-medium">{stats.projects}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Notes</span>
                    <span className="text-sm font-medium">{stats.notes}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Sources</span>
                    <span className="text-sm font-medium">{stats.sources}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Keywords</span>
                    <span className="text-sm font-medium">{stats.keywords}</span>
                  </div>
                </div>

                <Link href="/search">
                  <Button variant="outline" className="w-full">
                    <Search className="mr-2 h-4 w-4" />
                    Search Knowledge
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}