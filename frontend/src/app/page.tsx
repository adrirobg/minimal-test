'use client';

import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import {
  FolderTree,
  FileText,
  Search,
  ArrowRight,
  BookOpen,
  Tags,
  Link as LinkIcon
} from 'lucide-react';

export default function HomePage() {
  const features = [
    {
      title: 'Project Management',
      description: 'Organize your knowledge with hierarchical projects and subprojects',
      icon: FolderTree,
      href: '/projects',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Note Taking',
      description: 'Create and manage notes with rich content and metadata',
      icon: FileText,
      href: '/notes',
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Advanced Search',
      description: 'Find information quickly with semantic search capabilities',
      icon: Search,
      href: '/search',
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: 'Knowledge Linking',
      description: 'Connect ideas and create knowledge networks',
      icon: LinkIcon,
      href: '/notes',
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
    {
      title: 'Source Management',
      description: 'Track and organize your information sources',
      icon: BookOpen,
      href: '/sources',
      color: 'text-teal-600',
      bgColor: 'bg-teal-50',
    },
    {
      title: 'Tagging System',
      description: 'Categorize content with flexible keyword tagging',
      icon: Tags,
      href: '/keywords',
      color: 'text-pink-600',
      bgColor: 'bg-pink-50',
    },
  ];

  const stats = [
    { label: 'Projects', value: '0', icon: FolderTree },
    { label: 'Notes', value: '0', icon: FileText },
    { label: 'Sources', value: '0', icon: BookOpen },
    { label: 'Keywords', value: '0', icon: Tags },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-6 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 dark:text-gray-100 mb-6">
            Personal Knowledge Management
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-8 max-w-3xl mx-auto">
            Organize, connect, and discover your knowledge with our comprehensive PKM system.
            Build your second brain and enhance your learning journey.
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/projects">
              <Button size="lg" className="text-lg px-8">
                Get Started
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button variant="outline" size="lg" className="text-lg px-8">
                View Dashboard
              </Button>
            </Link>
          </div>
        </div>

        {/* Stats Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {stats.map((stat, index) => (
            <Card key={index} className="text-center">
              <CardContent className="p-6">
                <stat.icon className="h-8 w-8 mx-auto mb-3 text-gray-600" />
                <div className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-1">
                  {stat.value}
                </div>
                <div className="text-gray-600 dark:text-gray-400">
                  {stat.label}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Features Grid */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-gray-100 mb-12">
            Powerful Features
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Link key={index} href={feature.href}>
                <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer group">
                  <CardHeader>
                    <div className={`w-12 h-12 rounded-lg ${feature.bgColor} flex items-center justify-center mb-4`}>
                      <feature.icon className={`h-6 w-6 ${feature.color}`} />
                    </div>
                    <CardTitle className="text-xl group-hover:text-blue-600 transition-colors">
                      {feature.title}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-600 dark:text-gray-400">
                      {feature.description}
                    </p>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-8">
            Quick Actions
          </h2>
          <div className="flex flex-wrap gap-4 justify-center">
            <Link href="/projects">
              <Button variant="outline" size="lg">
                <FolderTree className="mr-2 h-5 w-5" />
                Create Project
              </Button>
            </Link>
            <Link href="/notes">
              <Button variant="outline" size="lg">
                <FileText className="mr-2 h-5 w-5" />
                Write Note
              </Button>
            </Link>
            <Link href="/search">
              <Button variant="outline" size="lg">
                <Search className="mr-2 h-5 w-5" />
                Search Knowledge
              </Button>
            </Link>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-20 pt-8 border-t border-gray-200 dark:border-gray-700 text-center">
          <p className="text-gray-600 dark:text-gray-400">
            Personal Knowledge Management System - Built with Next.js, TypeScript, and Tailwind CSS
          </p>
        </footer>
      </div>
    </div>
  );
}
