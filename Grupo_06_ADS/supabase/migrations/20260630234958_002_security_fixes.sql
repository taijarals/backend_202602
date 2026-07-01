/*
# Security Fixes Migration

This migration addresses security vulnerabilities identified:

1. **Function Search Path Mutable**: Fixed `update_updated_at_column` function
   to use an immutable search_path, preventing search_path attacks.

2. **RLS Policy Always True**: Fixed three policies that had `WITH CHECK (true)`
   which bypassed row-level security:
   - `conquistas` INSERT policy
   - `pontuacoes` INSERT policy  
   - `respostas_tentativa` INSERT policy

## Changes Made

### Function Fix
- Added `SET search_path = ''` to `update_updated_at_column` function
- This prevents the function from being vulnerable to search_path manipulation attacks

### RLS Policy Fixes

**conquistas table:**
- Changed from: `WITH CHECK (true)`
- Changed to: `WITH CHECK (auth.uid() IN (SELECT user_id FROM profiles WHERE id = aluno_id))`
- Ensures only authenticated users can insert conquistas for themselves

**pontuacoes table:**
- Changed from: `WITH CHECK (true)`
- Changed to: `WITH CHECK (auth.uid() IN (SELECT user_id FROM profiles WHERE id = aluno_id))`
- Ensures only authenticated users can add points for themselves (or system via service role)

**respostas_tentativa table:**
- Changed from: `WITH CHECK (true)`
- Changed to: `WITH CHECK (auth.uid() IN (SELECT user_id FROM profiles p JOIN tentativas_prova t ON t.aluno_id = p.id WHERE t.id = tentativa_id))`
- Ensures users can only submit answers for their own test attempts

## Security
- All policies now properly enforce ownership checks using `auth.uid()`
- Function is protected against search_path attacks
*/

-- Fix 1: Update function with secure search_path
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER 
SECURITY DEFINER
SET search_path = ''
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

-- Fix 2: Fix conquistas INSERT policy
DROP POLICY IF EXISTS "conquistas_insert_own" ON conquistas;
CREATE POLICY "conquistas_insert_own" ON conquistas FOR INSERT
    TO authenticated 
    WITH CHECK (auth.uid() IN (SELECT user_id FROM profiles WHERE id = aluno_id));

-- Fix 3: Fix pontuacoes INSERT policy
DROP POLICY IF EXISTS "pontuacoes_insert_system" ON pontuacoes;
CREATE POLICY "pontuacoes_insert_own" ON pontuacoes FOR INSERT
    TO authenticated 
    WITH CHECK (auth.uid() IN (SELECT user_id FROM profiles WHERE id = aluno_id));

-- Fix 4: Fix respostas_tentativa INSERT policy
DROP POLICY IF EXISTS "respostas_insert_student" ON respostas_tentativa;
CREATE POLICY "respostas_insert_student" ON respostas_tentativa FOR INSERT
    TO authenticated 
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM tentativas_prova t
            JOIN profiles p ON p.id = t.aluno_id
            WHERE t.id = tentativa_id 
            AND p.user_id = auth.uid()
        )
    );

-- Additional: Add policy to allow service role (system) to insert pontuacoes
-- This is needed for automatic point awards from the backend
DROP POLICY IF EXISTS "pontuacoes_insert_service" ON pontuacoes;
CREATE POLICY "pontuacoes_insert_service" ON pontuacoes FOR INSERT
    TO service_role
    WITH CHECK (true);