export type CandidateProfile = {
  id: string;
  name: string | null;
  education: string[];
  skills: string[];
  projects: string[];
  experience: string[];
  certifications: string[];
};

export type ResumeAnalysisResult = {
  resume_id: number;
  session_id: number;
  filename: string;
  resume_text: string;
  candidate_profile: CandidateProfile;
};