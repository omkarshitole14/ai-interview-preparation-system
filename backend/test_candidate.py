from unittest.mock import patch

from app.services.candidate_service import analyze_resume


def test_candidate_analysis():
    resume_text = """
    Omkar Shitole
    B.Tech in Electronics and Telecommunication Engineering

    Skills: Python, SQL, Machine Learning, FastAPI, Streamlit

    Projects:
    AI Interview Preparation Assistant
    AI Enhanced Career Guidance System

    Certification:
    Deloitte Data Analytics Job Simulation
    """

    expected_profile = {
        "name": "Omkar Shitole",
        "education": [
            "B.Tech in Electronics and Telecommunication Engineering"
        ],
        "skills": [
            "Python",
            "SQL",
            "Machine Learning",
            "FastAPI",
            "Streamlit",
        ],
        "projects": [
            "AI Interview Preparation Assistant",
            "AI Enhanced Career Guidance System",
        ],
        "experience": [],
        "certifications": [
            "Deloitte Data Analytics Job Simulation"
        ],
    }

    with patch(
        "app.services.candidate_service.client.models.generate_content"
    ) as mock_generate:

        mock_generate.return_value.text = """
        {
            "name": "Omkar Shitole",
            "education": ["B.Tech in Electronics and Telecommunication Engineering"],
            "skills": ["Python", "SQL", "Machine Learning", "FastAPI", "Streamlit"],
            "projects": ["AI Interview Preparation Assistant", "AI Enhanced Career Guidance System"],
            "experience": [],
            "certifications": ["Deloitte Data Analytics Job Simulation"]
        }
        """

        profile = analyze_resume(resume_text)

    assert profile.name == expected_profile["name"]
    assert profile.education == expected_profile["education"]
    assert profile.skills == expected_profile["skills"]
    assert profile.projects == expected_profile["projects"]
    assert profile.experience == expected_profile["experience"]
    assert profile.certifications == expected_profile["certifications"]

    mock_generate.assert_called_once()