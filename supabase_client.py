from supabase import create_client
import os

# ================= SUPABASE CONFIG =================

SUPABASE_URL = "https://bdhleygddjoxoeuqsirk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJkaGxleWdkZGpveG9ldXFzaXJrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY4NDE5MjUsImV4cCI6MjA4MjQxNzkyNX0.KDy2YAlbLtN0BsDTMW8snyiXL5_QJFIe8EKTGELAEo8"

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
