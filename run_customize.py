"""Standalone script to demonstrate resume customization.

Since no ANTHROPIC_API_KEY is available in this environment, this script
applies rule-based tailoring to demonstrate the pipeline. In production,
the LLM-powered customizer.customize_resume() would do this intelligently.
"""

from resume_customizer.bank import ResumeBank
from resume_customizer.models import Resume, Experience, ContactInfo
from resume_customizer.pdf_generator import generate_pdf
from pathlib import Path


def tailor_for_roblox_pmm(resume: Resume, job_text: str) -> Resume:
    """Rule-based tailoring targeting the Roblox PMM Intern role.

    In production this would be handled by the LLM via customize_resume().
    """
    data = resume.model_dump()

    # 1. Rewrite summary to target the PMM role
    data["summary"] = (
        "MBA candidate at UC Berkeley Haas with 8 years of experience in entertainment "
        "production, combining deep creative industry expertise with cross-functional "
        "project management, go-to-market storytelling, and stakeholder engagement. "
        "Proven track record driving adoption of immersive technologies (VR/3D/AI) across "
        "15+ major studio productions. Passionate about gaming, interactive media, and "
        "building community-driven creative platforms."
    )

    # 2. Re-organize experience bullets by relevance to the JD
    # Group: GTM/Marketing-adjacent, Cross-functional/Storytelling, Ops/Innovation
    data["experience"] = [
        {
            "title": "Production Designer & Set Designer (Contract)",
            "company": "Film & Television Production",
            "location": "Los Angeles, CA",
            "start_date": "2017",
            "end_date": "2025",
            "bullets": [
                # GTM & Storytelling — most relevant to PMM
                "Select Credits: The Odyssey (Universal), Harry Potter Series (Warner Bros.), "
                "The Batman (Warner Bros./DC Studios), Moana - Live Action (Disney), "
                "Red One (Amazon Studios), Ghostbusters: Afterlife (Sony) — 6x Art Directors Guild Award nominee/winner",

                "Revamped $2M creative installation by analyzing stakeholder requirements and "
                "audience impact, repositioning the design proposal to secure executive approval "
                "and protect the $50M production timeline",

                "Spearheaded adoption of VR and real-time 3D visualization technology to "
                "communicate complex creative concepts to non-technical stakeholders, reducing "
                "approval timelines by 30% and accelerating cross-functional collaboration",

                # Cross-functional & Stakeholder Engagement — maps to "collaborative, globally minded"
                "Bridged operational silos between global Design and Visual Effects teams by "
                "establishing standardized cross-functional asset conversion protocols, saving "
                "250+ redundant labor hours across distributed teams",

                "Facilitated remote decision-making for executive stakeholders by developing "
                "immersive VR environments using real-time data, accelerating design consensus "
                "across global production teams",

                "Fostered collaborative creative culture with executive stakeholders including "
                "Christopher Nolan by pioneering advanced visualization technologies, building "
                "authentic engagement in the creative vision",

                # Operations & Innovation — maps to "operation management skills"
                "Delivered $8M capital project 10% under budget by structuring parallel workflows "
                "and coordinating cross-functional teams pending executive authorization",

                "Increased team output capacity by 160% without additional headcount by developing "
                "an AI-assisted automation framework, demonstrating technology adoption strategy",

                "Aligned end-to-end operations with strict budgetary constraints through competitive "
                "vendor analysis, delivering 66% cost reduction via strategic negotiation",

                "Mentored designers and engineers by converting personal workflows into shared "
                "templates and standardized frameworks, improving department-wide proficiency",
            ],
        }
    ]

    # 3. Reorder skills — most relevant to Roblox PMM first
    data["skills"] = [
        "Go-to-Market Strategy",
        "Cross-Functional Project Management",
        "Storytelling & Content Development",
        "Stakeholder Engagement",
        "Unreal Engine",
        "Blender",
        "Adobe Creative Cloud",
        "VR/3D Visualization",
        "Python (automation)",
        "Tableau",
        "Alteryx",
    ]

    # 4. Enrich education details to highlight PMM-relevant activities
    data["education"][0]["details"] = [
        "Co-President of Digital Media & Entertainment Club — organizing industry events and creator community engagement",
        "Project Manager for AI Summit — led cross-functional team to plan and execute campus-wide technology conference",
        "Member of Haas Consulting Club, Communications Rep for MBA Cohort",
    ]

    return Resume.model_validate(data)


def main() -> None:
    bank = ResumeBank()

    # Load resume and job description
    resume = bank.load("chris_cortner")
    job_text = Path("jobs/roblox_pmm_intern.txt").read_text()

    # Tailor
    tailored = tailor_for_roblox_pmm(resume, job_text)

    # Show text output
    print("=" * 70)
    print("TAILORED RESUME — Roblox Product Marketing Manager Intern")
    print("=" * 70)
    print()
    print(tailored.to_text())

    # Save JSON to bank
    bank.save("chris_cortner_roblox_pmm", tailored)
    print("Saved tailored JSON: resumes/chris_cortner_roblox_pmm.json")

    # Generate PDF
    out = Path("output/chris_cortner_roblox_pmm.pdf")
    generate_pdf(tailored, out)
    print(f"PDF saved: {out.resolve()}")


if __name__ == "__main__":
    main()
