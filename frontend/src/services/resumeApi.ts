
import type { ResumeAnalysisResult } from "@/types/resume";
import { authenticatedFetch } from "@/services/apiClient";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

if (!API_URL) {
  throw new Error("NEXT_PUBLIC_API_URL is not configured.");
}

export type ResumeHistoryItem = {
  resume_id: number;
  filename: string;
  created_at: string;
  sessions: {
    session_id: number;
    status: string;
    interview_type: string;
    question_count: number;
    created_at: string;
  }[];
};

async function parseResponse(response: Response) {
  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(data?.detail || `Request failed: ${response.status}`);
  }

  return data;
}

export async function uploadResume(
  file: File,
  token: string,
): Promise<ResumeAnalysisResult> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await authenticatedFetch(
    `${API_URL}/api/resume/upload`,
    { method: "POST", body: formData },
    token,
  );

  return parseResponse(response) as Promise<ResumeAnalysisResult>;
}

export async function getResumeHistory(
  token: string,
): Promise<ResumeHistoryItem[]> {
  const response = await authenticatedFetch(
    `${API_URL}/api/resume/history`,
    {},
    token,
  );

  return parseResponse(response) as Promise<ResumeHistoryItem[]>;
}

export async function getSavedResume(
  resumeId: number,
  token: string,
): Promise<ResumeAnalysisResult> {
  const response = await authenticatedFetch(
    `${API_URL}/api/resume/${resumeId}`,
    {},
    token,
  );

  return parseResponse(response) as Promise<ResumeAnalysisResult>;
}
