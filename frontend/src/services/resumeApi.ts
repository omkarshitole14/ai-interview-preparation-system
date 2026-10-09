import type {
  ResumeAnalysisResult,
} from "@/types/resume";

import { authenticatedFetch } from "@/services/apiClient";


const API_URL =
  process.env.NEXT_PUBLIC_API_URL;

if (!API_URL) {
  throw new Error(
    "NEXT_PUBLIC_API_URL is not configured.",
  );
}


export async function uploadResume(
  file: File,
  token: string,
): Promise<ResumeAnalysisResult> {

  const formData =
    new FormData();

  formData.append(
    "file",
    file,
  );

  const response =
    await authenticatedFetch(
      `${API_URL}/api/resume/upload`,
      {
        method: "POST",
        body: formData,
      },
      token,
    );

  const data =
    await response.json().catch(
      () => null,
    );

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        "Resume analysis failed.",
    );
  }

  return data as ResumeAnalysisResult;
}