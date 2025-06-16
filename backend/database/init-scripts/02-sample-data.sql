-- Sample data for immediate testing
-- This file is automatically loaded when the database starts

-- Note: This is kept minimal since we have a Python script for more comprehensive sample data
-- These are just basic records to verify the database is working

-- Insert a test user (password is 'test123' hashed)
INSERT INTO users (id, email, username, hashed_password, full_name, is_active, created_at) 
VALUES (
    'test-user-id-123',
    'test@example.com',
    'testuser',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewBDPSLdP8lIXdOO', -- 'test123'
    'Test User',
    true,
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- Insert a test project
INSERT INTO projects (id, name, description, user_id, created_at)
VALUES (
    'test-project-id-123',
    'Test Project',
    'Initial test project for database verification',
    'test-user-id-123',
    NOW()
) ON CONFLICT (id) DO NOTHING;

-- Insert a test note
INSERT INTO notes (id, title, content, note_type, project_id, user_id, created_at)
VALUES (
    'test-note-id-123',
    'Database Connection Test',
    'This note verifies that the database connection is working correctly.',
    'note',
    'test-project-id-123',
    'test-user-id-123',
    NOW()
) ON CONFLICT (id) DO NOTHING;