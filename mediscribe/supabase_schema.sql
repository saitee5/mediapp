-- ==============================================================================
-- MediScribe AI Consultation, SOAP & Multi-Document Schema for Supabase
-- ==============================================================================

-- 1. Create consultations table with multi-document support
CREATE TABLE IF NOT EXISTS public.consultations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT UNIQUE NOT NULL,
    patient_id TEXT,
    patient_name TEXT,
    doctor_name TEXT,
    encounter_date TEXT,
    transcript TEXT,
    soap_data JSONB,
    patient_visit_summary JSONB,
    case_sheet_summary JSONB,
    discharge_instructions JSONB,
    referral_letter JSONB,
    updated_case_sheet_summary JSONB,
    pdf_url TEXT,
    status TEXT NOT NULL DEFAULT 'pending_review',
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- Ensure newly added columns exist if table was already created
ALTER TABLE public.consultations ADD COLUMN IF NOT EXISTS patient_visit_summary JSONB;
ALTER TABLE public.consultations ADD COLUMN IF NOT EXISTS discharge_instructions JSONB;
ALTER TABLE public.consultations ADD COLUMN IF NOT EXISTS referral_letter JSONB;
ALTER TABLE public.consultations ADD COLUMN IF NOT EXISTS case_sheet_summary JSONB;
ALTER TABLE public.consultations ADD COLUMN IF NOT EXISTS pdf_url TEXT;

-- Indexes for rapid lookup
CREATE INDEX IF NOT EXISTS idx_consultations_session_id ON public.consultations(session_id);
CREATE INDEX IF NOT EXISTS idx_consultations_status ON public.consultations(status);
CREATE INDEX IF NOT EXISTS idx_consultations_created_at ON public.consultations(created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE public.consultations ENABLE ROW LEVEL SECURITY;

-- Allow public / anon and authenticated access for read and write
DROP POLICY IF EXISTS "Allow anon read and write on consultations" ON public.consultations;
CREATE POLICY "Allow anon read and write on consultations"
    ON public.consultations
    FOR ALL
    TO anon, authenticated
    USING (true)
    WITH CHECK (true);

-- Auto-update updated_at timestamp trigger
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS on_consultations_updated ON public.consultations;
CREATE TRIGGER on_consultations_updated
    BEFORE UPDATE ON public.consultations
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

-- ==============================================================================
-- 2. Supabase Storage Bucket for Generated PDFs (case-sheets)
-- ==============================================================================

-- Create public storage bucket for case sheets
INSERT INTO storage.buckets (id, name, public)
VALUES ('case-sheets', 'case-sheets', true)
ON CONFLICT (id) DO UPDATE SET public = true;

-- Policy to allow public read access on PDFs
DROP POLICY IF EXISTS "Public Read Access for case-sheets" ON storage.objects;
CREATE POLICY "Public Read Access for case-sheets"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'case-sheets');

-- Policy to allow uploads into case-sheets
DROP POLICY IF EXISTS "Allow Uploads to case-sheets" ON storage.objects;
CREATE POLICY "Allow Uploads to case-sheets"
ON storage.objects FOR INSERT
TO public
WITH CHECK (bucket_id = 'case-sheets');

-- Policy to allow updates/upserts into case-sheets
DROP POLICY IF EXISTS "Allow Updates to case-sheets" ON storage.objects;
CREATE POLICY "Allow Updates to case-sheets"
ON storage.objects FOR UPDATE
TO public
USING (bucket_id = 'case-sheets');
