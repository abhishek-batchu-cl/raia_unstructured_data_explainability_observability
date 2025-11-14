-- ============================================================================
-- RAIA Database Initialization Script
-- ============================================================================
-- This script is automatically run when PostgreSQL container starts
-- It creates the database schema and initial data

-- Create database (if not exists)
-- Note: The database is already created by docker-compose environment variables
-- This file can be used for additional setup

-- Set timezone
SET timezone = 'UTC';

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search

-- Database is ready
SELECT 'RAIA PostgreSQL Database Initialized' AS status;
