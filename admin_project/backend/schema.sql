-- DEEPS Database Schema (Reference)

-- 1. Programs
CREATE TABLE programs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name_ar TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 2. Tracks
CREATE TABLE tracks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 3. Labs
CREATE TABLE labs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    track_id UUID REFERENCES tracks(id) ON DELETE CASCADE,
    code TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 4. Students
CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_name_ar TEXT NOT NULL,
    military_number TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 5. Petitions
CREATE TABLE petitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    petition_code TEXT NOT NULL UNIQUE,
    petition_type TEXT NOT NULL DEFAULT 'external', -- 'external' or 'internal'
    student_name_ar TEXT NOT NULL,
    military_number TEXT NOT NULL,
    program_id UUID REFERENCES programs(id),
    track_id UUID REFERENCES tracks(id),
    lab_id UUID REFERENCES labs(id),
    exit_datetime TIMESTAMP WITH TIME ZONE,
    return_datetime TIMESTAMP WITH TIME ZONE,
    submitted_date DATE NOT NULL,
    description TEXT,
    reasons JSONB NOT NULL DEFAULT '[]'::jsonb,
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'approved', 'declined'
    admin_notes TEXT,
    decided_by TEXT,
    decided_at TIMESTAMP WITH TIME ZONE,
    generated_docx_url TEXT,
    generated_pdf_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 6. Petition Attachments
CREATE TABLE petition_attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    petition_id UUID REFERENCES petitions(id) ON DELETE CASCADE,
    original_name TEXT NOT NULL,
    stored_name TEXT NOT NULL,
    file_url TEXT NOT NULL,
    file_size BIGINT,
    mime_type TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 7. Petition History (Log)
CREATE TABLE petition_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    petition_id UUID REFERENCES petitions(id) ON DELETE CASCADE,
    action TEXT NOT NULL, -- 'submitted', 'approved', 'declined', 'printed', etc.
    admin_name TEXT,
    admin_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Index for military number lookups
CREATE INDEX idx_petitions_military_number ON petitions(military_number);
CREATE INDEX idx_students_military_number ON students(military_number);

-- RPC Functions for Sequence Generation (Conceptual)
-- These typically use a sequence table or direct calculation
-- Format: EXT-YYYYMMDD-XXXX or INT-YYYYMMDD-XXXX
