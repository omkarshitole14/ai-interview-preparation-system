import { authenticatedFetch } from "@/services/apiClient";


const API_URL =
  process.env.NEXT_PUBLIC_API_URL;

if (!API_URL) {
  throw new Error(
    "NEXT_PUBLIC_API_URL is not configured.",
  );
}


export type InterviewType =
  | "mixed"
  | "technical"
  | "hr"
  | "resume"
  | "coding"
  | "ml_ai"
  | "genai_rag";


export interface InterviewQuestion {
  id: number;
  question: string;
  category: string;
  difficulty: string;
  expected_topics: string[];
}


export interface InterviewQuestionResponse {
  questions: InterviewQuestion[];
}


export interface InterviewAnswerEvaluation {
  score: number;
  feedback: string;
  strengths: string[];
  improvements: string[];
  time_complexity?: string | null;
  space_complexity?: string | null;
}


async function parseResponse(
  response: Response,
) {
  const data =
    await response.json().catch(
      () => null,
    );

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        `Request failed with status ${response.status}.`,
    );
  }

  return data;
}


export async function generateInterviewQuestions(
  sessionId: number,
  interviewType: InterviewType,
  questionCount: 5 | 10 | 15,
  token: string,
): Promise<InterviewQuestionResponse> {

  const response =
    await authenticatedFetch(
      `${API_URL}/api/interview/questions`,
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
          interview_type:
            interviewType,
          question_count:
            questionCount,
        }),
      },
      token,
    );

  return parseResponse(
    response,
  ) as Promise<InterviewQuestionResponse>;
}


export async function evaluateInterviewAnswer(
  questionId: number,
  answer: string,
  token: string,
): Promise<InterviewAnswerEvaluation> {

  const response =
    await authenticatedFetch(
      `${API_URL}/api/interview/evaluate`,
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify({
          question_id: questionId,
          answer,
        }),
      },
      token,
    );

  return parseResponse(
    response,
  ) as Promise<InterviewAnswerEvaluation>;
}