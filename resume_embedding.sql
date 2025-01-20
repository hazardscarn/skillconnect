--drop table resumes;

----This is the SQL script to create the table and function for the resume embedding in Supabase
----Script have to be added in the supabase project as a sql query

-- Enable the vector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the resumes table with all columns
CREATE TABLE resumes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  content TEXT,
  profession_type TEXT,
  file_name TEXT,
  file_path TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  embedding VECTOR(768)
);

-- Create an index for faster similarity searches
CREATE INDEX ON resumes 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create a function to search for similar resumes with profession filter
CREATE FUNCTION match_resumes (
  query_embedding VECTOR(768),
  profession_filter TEXT DEFAULT NULL,
  match_threshold FLOAT default 0.5,
  match_count INT default 10
)
RETURNS TABLE (
  id UUID,
  content TEXT,
  profession_type TEXT,
  file_name TEXT,
  file_path TEXT,
  created_at TIMESTAMP WITH TIME ZONE,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    resumes.id,
    resumes.content,
    resumes.profession_type,
    resumes.file_name,
    resumes.file_path,
    resumes.created_at,
    1 - (resumes.embedding <=> query_embedding) AS similarity
  FROM resumes
  WHERE 
    CASE 
      WHEN profession_filter IS NULL THEN true
      ELSE profession_type = profession_filter
    END
    AND 1 - (resumes.embedding <=> query_embedding) > match_threshold
  ORDER BY resumes.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;