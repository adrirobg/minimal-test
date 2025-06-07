# PKM Frontend

Personal Knowledge Management system frontend built with Next.js 15, TypeScript, and Tailwind CSS.

## Features

- 🏗️ **Project Management**: Hierarchical project organization with TreeView
- 📝 **Note Taking**: Rich note creation and management system
- 🔍 **Search**: Advanced search capabilities
- 🔗 **Knowledge Linking**: Connect related notes and concepts
- 📚 **Source Management**: Track and organize information sources
- 🏷️ **Tagging System**: Flexible keyword-based categorization
- 🎨 **Modern UI**: Built with ShadCN UI components
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: ShadCN UI
- **State Management**: Zustand
- **Forms**: React Hook Form + Zod validation
- **HTTP Client**: Axios
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running (see main README)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Copy environment variables:
```bash
cp .env.local.example .env.local
```

3. Update environment variables in `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Development

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linting
npm run lint
```

The application will be available at `http://localhost:3000`.

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── (auth)/            # Authentication routes
│   │   ├── dashboard/         # Dashboard page
│   │   ├── projects/          # Projects management
│   │   ├── notes/             # Notes management
│   │   └── search/            # Search functionality
│   ├── components/            # React components
│   │   ├── ui/                # ShadCN UI components
│   │   ├── forms/             # Form components
│   │   ├── navigation/        # Navigation components
│   │   └── pkm/               # PKM-specific components
│   ├── lib/                   # Utilities and configurations
│   │   ├── api/               # API client and services
│   │   ├── auth/              # Authentication utilities
│   │   ├── store/             # Zustand state management
│   │   └── utils/             # General utilities
│   └── types/                 # TypeScript type definitions
├── public/                    # Static assets
└── ...config files
```

## Key Components

### TreeView Component
- Hierarchical display of projects
- Drag & drop support (planned)
- Context menu actions
- Expandable/collapsible nodes

### ProjectForm Component
- Create/edit projects
- Parent project selection
- Form validation with Zod
- Real-time validation feedback

### API Client
- Axios-based HTTP client
- Automatic token refresh
- Request/response interceptors
- Error handling

### State Management
- Zustand stores for different domains
- Persistent state for authentication
- Optimistic updates
- Error state management

## Available Pages

### Home (`/`)
- Landing page with feature overview
- Quick action buttons
- Statistics dashboard

### Projects (`/projects`)
- Project hierarchy visualization
- CRUD operations for projects
- TreeView navigation
- Project details panel

### Notes (`/notes`) - Planned
- Note creation and editing
- Rich text editor
- Note linking system
- Search and filtering

### Search (`/search`) - Planned
- Global search functionality
- Semantic search capabilities
- Filter by content type
- Search history

## API Integration

The frontend communicates with the FastAPI backend through:

- **Authentication**: Token-based auth with automatic refresh
- **Projects API**: Full CRUD operations
- **Notes API**: Note management (planned)
- **Search API**: Search functionality (planned)
- **Sources API**: Source management (planned)
- **Keywords API**: Tag management (planned)

## Development Guidelines

### Code Organization
- Use TypeScript for all code
- Follow Next.js App Router conventions
- Implement responsive design patterns
- Use ShadCN UI components consistently

### State Management
- Use Zustand for client state
- Keep stores focused and domain-specific
- Implement optimistic updates where appropriate
- Handle loading and error states

### Form Handling
- Use React Hook Form + Zod for validation
- Implement proper error messaging
- Provide real-time validation feedback
- Handle form submission states

### API Calls
- Use the centralized API client
- Implement proper error handling
- Show loading states during requests
- Cache responses where appropriate

## Deployment

### Build Process
```bash
npm run build
```

### Environment Variables
- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NEXTAUTH_SECRET`: NextAuth secret (when implemented)
- `NEXTAUTH_URL`: Application URL (when implemented)

### Production Considerations
- Enable compression
- Configure proper caching headers
- Set up monitoring and error tracking
- Implement proper SEO optimization

## Contributing

1. Follow the established code structure
2. Write TypeScript types for all data
3. Test components thoroughly
4. Update documentation as needed
5. Follow the existing naming conventions

## License

This project is part of the PKM system. See the main project LICENSE for details.
