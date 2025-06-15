import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Authentication - PKM App',
  description: 'Sign in or create an account for Personal Knowledge Management',
};

export default function AuthLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {children}
    </div>
  );
}