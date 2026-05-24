"""
AI Resume Builder
=================
Tailors resumes to job descriptions using local LLM
Generates downloadable PDF
"""

from typing import Dict, Optional
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, 
    Table, TableStyle, HRFlowable
)
from reportlab.lib.colors import HexColor, black
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

from config import Config
from core.local_llm import llm_manager
from database.db_manager import db


class ResumeBuilder:
    """Build and tailor resumes using local AI"""
    
    def __init__(self):
        self.output_dir = Config.GENERATED_RESUMES
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def tailor_resume(self, resume_text: str, job_description: str) -> Dict:
        """
        Tailor resume to match job description
        
        Args:
            resume_text: Original resume content
            job_description: Target job description
            
        Returns:
            dict with tailored resume
        """
        if not llm_manager.is_ollama_running():
            return {
                "success": False,
                "error": "Ollama is not running. Start it with: ollama serve"
            }
        
        try:
            prompt = f"""You are an expert resume writer and career coach.

Your task: Tailor this resume to match the job description.

IMPORTANT RULES:
1. NEVER fabricate information - only reorganize and reword existing content
2. Highlight relevant skills and experiences
3. Use keywords from the job description naturally
4. Use strong action verbs
5. Keep it concise and ATS-friendly

=== ORIGINAL RESUME ===
{resume_text}

=== JOB DESCRIPTION ===
{job_description}

=== OUTPUT FORMAT ===
Provide the tailored resume with these sections:

**CONTACT INFORMATION**
[Extract from original]

**PROFESSIONAL SUMMARY**
[2-3 sentences tailored to this specific job]

**KEY SKILLS**
[Relevant skills as bullet points]

**PROFESSIONAL EXPERIENCE**
[Experience with tailored bullet points]

**EDUCATION**
[Education details]

**PROJECTS** (if applicable)
[Relevant projects]

---

**MATCH ANALYSIS**
- Match Score: [percentage]
- Key Matching Skills: [list]
- Gaps to Address: [list]
- Interview Tips: [2-3 tips specific to this job]
"""
            
            llm = llm_manager.llm
            
            system_prompt = """You are an expert resume writer. 
Create professional, ATS-friendly resumes. 
Be truthful - never add false information.
Use strong action verbs and quantify achievements."""
            
            tailored_resume = llm.generate(prompt, system_prompt)
            
            # Save to history
            db.save_resume_history(
                original_resume=resume_text,
                job_description=job_description,
                tailored_resume=tailored_resume
            )
            
            return {
                "success": True,
                "tailored_resume": tailored_resume
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_resume(self, resume_text: str) -> Dict:
        """
        Analyze resume for improvements
        
        Args:
            resume_text: Resume content
            
        Returns:
            dict with analysis
        """
        if not llm_manager.is_ollama_running():
            return {
                "success": False,
                "error": "Ollama is not running"
            }
        
        try:
            prompt = f"""Analyze this resume and provide detailed feedback:

{resume_text}

Provide analysis in this format:

**OVERALL SCORE**: [X/100]

**STRENGTHS** ✅
1. [Strength 1]
2. [Strength 2]
3. [Strength 3]

**AREAS FOR IMPROVEMENT** ⚠️
1. [Issue 1] - How to fix
2. [Issue 2] - How to fix
3. [Issue 3] - How to fix

**MISSING ELEMENTS** ❌
- [Missing element 1]
- [Missing element 2]

**ATS OPTIMIZATION TIPS** 🎯
- [Tip 1]
- [Tip 2]

**KEYWORD SUGGESTIONS** 🔑
[List of keywords to add based on content]

**QUICK WINS** ⚡
3 things to improve immediately:
1. [Quick fix 1]
2. [Quick fix 2]
3. [Quick fix 3]
"""
            
            llm = llm_manager.llm
            analysis = llm.generate(
                prompt,
                system_prompt="You are an expert resume reviewer and career coach."
            )
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_pdf(self, resume_content: str, filename: str = None) -> Dict:
        """
        Generate PDF from resume content
        
        Args:
            resume_content: Formatted resume text
            filename: Output filename (optional)
            
        Returns:
            dict with file path and download URL
        """
        try:
            # Generate filename
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"resume_{timestamp}.pdf"
            
            filepath = self.output_dir / filename
            
            # Create PDF document
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=letter,
                rightMargin=0.75 * inch,
                leftMargin=0.75 * inch,
                topMargin=0.75 * inch,
                bottomMargin=0.75 * inch
            )
            
            # Styles
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'ResumeTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=6,
                textColor=HexColor('#1a365d'),
                alignment=TA_CENTER
            )
            
            section_style = ParagraphStyle(
                'SectionHeader',
                parent=styles['Heading2'],
                fontSize=12,
                spaceBefore=12,
                spaceAfter=6,
                textColor=HexColor('#2d3748'),
                borderColor=HexColor('#4a5568'),
                borderWidth=0,
                borderPadding=0
            )
            
            body_style = ParagraphStyle(
                'ResumeBody',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=4,
                alignment=TA_JUSTIFY,
                leading=14
            )
            
            bullet_style = ParagraphStyle(
                'ResumeBullet',
                parent=styles['Normal'],
                fontSize=10,
                leftIndent=15,
                spaceAfter=3,
                bulletIndent=5,
                leading=14
            )
            
            # Build content
            content = []
            
            # Parse resume content
            lines = resume_content.split('\n')
            skip_section = False
            
            for line in lines:
                line = line.strip()
                
                if not line:
                    continue
                
                # Skip Match Analysis section in PDF
                if 'MATCH ANALYSIS' in line.upper():
                    skip_section = True
                    continue
                
                if skip_section:
                    continue
                
                # Section headers
                if line.startswith('**') and line.endswith('**'):
                    section_name = line.strip('*').strip()
                    content.append(Spacer(1, 8))
                    content.append(Paragraph(section_name.upper(), section_style))
                    content.append(HRFlowable(
                        width="100%", 
                        thickness=1, 
                        color=HexColor('#e2e8f0')
                    ))
                    content.append(Spacer(1, 4))
                
                # Bullet points
                elif line.startswith('- ') or line.startswith('• '):
                    bullet_text = line[2:].strip()
                    content.append(Paragraph(f"• {bullet_text}", bullet_style))
                
                # Skip placeholder text
                elif line.startswith('[') and line.endswith(']'):
                    continue
                
                # Regular text
                else:
                    # Clean up any remaining markdown
                    clean_line = line.replace('**', '').replace('*', '')
                    if clean_line:
                        content.append(Paragraph(clean_line, body_style))
            
            # Build PDF
            doc.build(content)
            
            return {
                "success": True,
                "filepath": str(filepath),
                "filename": filename,
                "download_url": f"/download/resume/{filename}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def extract_from_pdf(self, pdf_path: str) -> Dict:
        """Extract text from PDF resume"""
        try:
            from PyPDF2 import PdfReader
            
            reader = PdfReader(pdf_path)
            text = ""
            
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            return {
                "success": True,
                "text": text.strip()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_cover_letter(
        self, 
        resume_text: str, 
        job_description: str,
        company_name: str = "the company"
    ) -> Dict:
        """Generate cover letter based on resume and job"""
        if not llm_manager.is_ollama_running():
            return {"success": False, "error": "Ollama not running"}
        
        try:
            prompt = f"""Write a professional cover letter based on this resume and job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

COMPANY: {company_name}

Write a compelling cover letter that:
1. Opens with enthusiasm for the role
2. Highlights 2-3 most relevant experiences
3. Shows knowledge of the company/role
4. Closes with a call to action

Keep it concise (3-4 paragraphs).
"""
            
            llm = llm_manager.llm
            cover_letter = llm.generate(
                prompt,
                system_prompt="You write professional, engaging cover letters."
            )
            
            return {
                "success": True,
                "cover_letter": cover_letter
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}


# Singleton instance
resume_builder = ResumeBuilder()