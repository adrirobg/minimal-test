'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { 
  Home, FileText, Folder, Search, BookOpen, Tags, Settings, 
  Menu, X, ChevronLeft, User, LogOut
} from 'lucide-react';
import { useAuthStore } from '@/lib/store/auth';
import { cn } from '@/lib/utils';

interface SidebarProps {
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
  className?: string;
}

interface NavigationItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string | number;
}

const navigation: NavigationItem[] = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { name: 'Projects', href: '/projects', icon: Folder },
  { name: 'Notes', href: '/notes', icon: FileText },
  { name: 'Search', href: '/search', icon: Search },
  { name: 'Sources', href: '/sources', icon: BookOpen },
  { name: 'Keywords', href: '/keywords', icon: Tags },
];

export const Sidebar: React.FC<SidebarProps> = ({ 
  isCollapsed = false, 
  onToggleCollapse,
  className = '' 
}) => {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const handleLogout = async () => {
    logout();
    window.location.href = '/login';
  };

  const sidebarContent = (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className={cn("flex items-center px-4 py-6 border-b", isCollapsed && "justify-center")}>
        {!isCollapsed ? (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">K</span>
            </div>
            <div>
              <h1 className="font-bold text-lg text-gray-900 dark:text-white">Kairos BCP</h1>
              <p className="text-xs text-gray-500 dark:text-gray-400">PKM System</p>
            </div>
          </div>
        ) : (
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">K</span>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-4 space-y-2 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
          
          return (
            <Link key={item.name} href={item.href}>
              <Button
                variant={isActive ? "default" : "ghost"}
                className={cn(
                  "w-full justify-start gap-3 h-11",
                  isCollapsed && "px-2 justify-center",
                  isActive && "bg-blue-600 text-white hover:bg-blue-700"
                )}
                onClick={() => setIsMobileOpen(false)}
              >
                <item.icon className={cn("h-5 w-5", isCollapsed && "h-4 w-4")} />
                {!isCollapsed && (
                  <>
                    <span className="font-medium">{item.name}</span>
                    {item.badge && (
                      <span className="ml-auto bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded-full">
                        {item.badge}
                      </span>
                    )}
                  </>
                )}
              </Button>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t space-y-2">
        {user && (
          <div className={cn(
            "flex items-center gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-800",
            isCollapsed && "justify-center"
          )}>
            <div className="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center">
              <User className="h-4 w-4 text-gray-600 dark:text-gray-300" />
            </div>
            {!isCollapsed && (
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {user.full_name}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                  {user.email}
                </p>
              </div>
            )}
          </div>
        )}

        <div className="space-y-1">
          <Link href="/settings">
            <Button
              variant="ghost"
              className={cn("w-full justify-start gap-3", isCollapsed && "px-2 justify-center")}
            >
              <Settings className="h-4 w-4" />
              {!isCollapsed && <span>Settings</span>}
            </Button>
          </Link>
          
          <Button
            variant="ghost"
            onClick={handleLogout}
            className={cn("w-full justify-start gap-3 text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20", isCollapsed && "px-2 justify-center")}
          >
            <LogOut className="h-4 w-4" />
            {!isCollapsed && <span>Logout</span>}
          </Button>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile Menu Button */}
      <Button
        variant="ghost"
        size="sm"
        className="lg:hidden fixed top-4 left-4 z-50"
        onClick={() => setIsMobileOpen(true)}
      >
        <Menu className="h-5 w-5" />
      </Button>

      {/* Mobile Sidebar Overlay */}
      {isMobileOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div 
            className="fixed inset-0 bg-black/50" 
            onClick={() => setIsMobileOpen(false)}
          />
          <div className="relative flex w-80 bg-white dark:bg-gray-900 shadow-xl">
            <div className="absolute top-4 right-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsMobileOpen(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            {sidebarContent}
          </div>
        </div>
      )}

      {/* Desktop Sidebar */}
      <aside className={cn(
        "hidden lg:flex flex-col bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 transition-all duration-300",
        isCollapsed ? "w-16" : "w-80",
        className
      )}>
        {/* Collapse Button */}
        <div className="absolute top-6 -right-3 z-10">
          <Button
            variant="outline"
            size="sm"
            className="w-6 h-6 p-0 bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-700 shadow-sm"
            onClick={onToggleCollapse}
          >
            <ChevronLeft className={cn("h-3 w-3 transition-transform", isCollapsed && "rotate-180")} />
          </Button>
        </div>

        {sidebarContent}
      </aside>
    </>
  );
};

export default Sidebar;