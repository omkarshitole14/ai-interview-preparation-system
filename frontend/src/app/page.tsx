"use client";

import {
  DragEvent,
  useEffect,
  useRef,
  useState,
} from "react";

import { useRouter } from "next/navigation";

import { uploadResume } from "@/services/resumeApi";

import type {
  ResumeAnalysisResult,
} from "@/types/resume";

import {
  generateInterviewQuestions,
  type InterviewQuestionResponse,
  type InterviewType,
} from "@/services/interviewApi";

import ResumeUpload from "@/components/resume/ResumeUpload";
import ResumeTextViewer from "@/components/resume/ResumeTextViewer";
import CandidateProfile from "@/components/resume/CandidateProfile";
import InterviewQuestions from "@/components/interview/InterviewQuestions";
import RAGAssistant from "@/components/rag/RAGAssistant";

import {
  getAccessToken,
  removeAccessToken,
} from "@/lib/auth";

import {
  logoutUser,
} from "@/services/authApi";

export default function Home() {

  const router = useRouter();


  const [authenticated, setAuthenticated] =
    useState(false);

  const [checkingAuth, setCheckingAuth] =
    useState(true);


  const [generatingInterview, setGeneratingInterview] =
    useState(false);


  const [interviewQuestions, setInterviewQuestions] =
    useState<InterviewQuestionResponse | null>(null);


  const [sessionId, setSessionId] =
    useState<number | null>(null);


  const [file, setFile] =
    useState<File | null>(null);


  const [result, setResult] =
    useState<ResumeAnalysisResult | null>(null);


  const [loading, setLoading] =
    useState(false);


  const [error, setError] =
    useState("");


  const fileInputRef =
    useRef<HTMLInputElement>(null);


  /*
   * Check authentication when the page loads.
   */
  useEffect(() => {

    const token = getAccessToken();

    if (!token) {
      router.replace("/login");
      return;
    }

    setAuthenticated(true);
    setCheckingAuth(false);

  }, [router]);


  /*
   * Get JWT for protected API requests.
   */
  const getAuthToken = (): string => {

    const token = getAccessToken();

    if (!token) {

      removeAccessToken();

      router.replace("/login");

      throw new Error(
        "Your session has expired. Please log in again."
      );
    }

    return token;
  };


  /*
   * Logout.
   */
  const handleLogout = async () => {
  await logoutUser();

  removeAccessToken();

  setAuthenticated(false);

  router.replace("/login");
};

  /*
   * File selection.
   */
  const selectFile = (
    selectedFile: File | null
  ) => {

    if (!selectedFile) {
      return;
    }


    if (selectedFile.type !== "application/pdf") {

      setError(
        "Please select a PDF resume."
      );

      return;
    }


    setFile(selectedFile);

    setResult(null);

    setSessionId(null);

    setInterviewQuestions(null);

    setError("");
  };


  /*
   * Drag and drop.
   */
  const handleDrop = (
    event: DragEvent<HTMLDivElement>
  ) => {

    event.preventDefault();

    const droppedFile =
      event.dataTransfer.files[0];

    selectFile(droppedFile);
  };


  /*
   * Upload and analyze resume.
   */
  const handleAnalyze = async () => {

    if (!file) {

      setError(
        "Please select a PDF resume first."
      );

      return;
    }


    setLoading(true);

    setError("");

    setResult(null);

    setSessionId(null);

    setInterviewQuestions(null);


    try {

      const token = getAuthToken();


      const data = await uploadResume(
        file,
        token
      );


      setResult(data);

      setSessionId(
        data.session_id
      );

    } catch (err) {

      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong while analyzing the resume."
      );

    } finally {

      setLoading(false);

    }
  };


  /*
   * Generate interview questions.
   */
  const handleGenerateInterview = async (
    interviewType: InterviewType,
    questionCount: 5 | 10 | 15,
  ) => {

    if (!sessionId) {

      setError(
        "Please analyze your resume before generating interview questions."
      );

      return;
    }


    setError("");

    setGeneratingInterview(true);

    setInterviewQuestions(null);


    try {

      const token = getAuthToken();


      const data =
        await generateInterviewQuestions(
          sessionId,
          interviewType,
          questionCount,
          token,
        );


      setInterviewQuestions(data);

    } catch (err) {

      setError(
        err instanceof Error
          ? err.message
          : "Failed to generate interview questions."
      );

    } finally {

      setGeneratingInterview(false);

    }
  };


  /*
   * Authentication loading screen.
   */
  if (checkingAuth) {

    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-50">

        <div className="text-center">

          <p className="text-sm font-medium text-slate-700">
            Checking authentication...
          </p>

          <p className="mt-1 text-xs text-slate-400">
            Please wait
          </p>

        </div>

      </main>
    );
  }


  /*
   * Prevent rendering the application
   * before authentication has been confirmed.
   */
  if (!authenticated) {
    return null;
  }


  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">

      <div className="flex min-h-screen">

        {/* Sidebar */}
        <aside className="hidden w-64 border-r border-slate-200 bg-white md:flex md:flex-col">

          <div className="border-b border-slate-200 px-6 py-6">

            <h1 className="text-xl font-semibold tracking-tight">
              InterviewAI
            </h1>

            <p className="mt-1 text-xs text-slate-500">
              Interview preparation system
            </p>

          </div>


          <nav className="flex-1 px-4 py-6">

            <p className="px-3 pb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
              Workspace
            </p>


            <div className="space-y-1">

              <button
                type="button"
                className="w-full rounded-lg bg-slate-100 px-3 py-2.5 text-left text-sm font-medium text-slate-900"
              >
                Analyze Resume
              </button>


              <button
                type="button"
                className="w-full rounded-lg px-3 py-2.5 text-left text-sm text-slate-500 hover:bg-slate-50"
              >
                Interview
              </button>


              <button
                type="button"
                className="w-full rounded-lg px-3 py-2.5 text-left text-sm text-slate-500 hover:bg-slate-50"
              >
                Reports
              </button>

            </div>

          </nav>


          <div className="border-t border-slate-200 px-4 py-5">

            <button
              type="button"
              onClick={handleLogout}
              className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-left text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              Sign out
            </button>


            <p className="mt-4 px-2 text-xs text-slate-400">
              AI Interview System
            </p>

          </div>

        </aside>


        {/* Main */}
        <main className="flex-1">

          {/* Header */}
          <header className="border-b border-slate-200 bg-white">

            <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">

              <div>

                <p className="text-sm font-medium text-slate-500">
                  Resume Analysis
                </p>

                <h2 className="mt-1 text-2xl font-semibold tracking-tight">
                  Prepare your interview
                </h2>

              </div>


              <button
                type="button"
                onClick={handleLogout}
                className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 md:hidden"
              >
                Sign out
              </button>

            </div>

          </header>


          <div className="mx-auto max-w-7xl space-y-8 px-6 py-8">

            {/* Resume upload */}
            <ResumeUpload
              file={file}
              loading={loading}
              error={error}
              fileInputRef={fileInputRef}
              onFileSelect={selectFile}
              onDrop={handleDrop}
              onAnalyze={handleAnalyze}
            />


            {/* RAG assistant */}
            <RAGAssistant />


            {/* Resume analysis */}
            {result && (

              <section className="space-y-6">

                <div>

                  <p className="text-sm font-medium text-blue-600">
                    Analysis complete
                  </p>

                  <h3 className="mt-1 text-2xl font-semibold tracking-tight">
                    {result.candidate_profile.name || "Candidate Profile"}
                  </h3>

                  <p className="mt-1 text-sm text-slate-500">
                    Candidate Profile
                  </p>

                  <p className="mt-1 text-xs text-slate-400">
                    Resume: {result.filename}
                  </p>

                </div>


                {/* Profile summary */}
                <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">

                  <InfoCard
                    title="Education"
                    count={
                      result.candidate_profile.education.length
                    }
                  />


                  <InfoCard
                    title="Skills"
                    count={
                      result.candidate_profile.skills.length
                    }
                  />


                  <InfoCard
                    title="Projects"
                    count={
                      result.candidate_profile.projects.length
                    }
                  />


                  <InfoCard
                    title="Experience"
                    count={
                      result.candidate_profile.experience.length
                    }
                  />

                </div>


                <ResumeTextViewer
                  resumeText={result.resume_text}
                />


                <CandidateProfile
                  profile={result.candidate_profile}
                />


                <InterviewQuestions
                  interviewQuestions={
                    interviewQuestions
                  }
                  generating={
                    generatingInterview
                  }
                  onGenerate={
                    handleGenerateInterview
                  }
                  tokenGetter={
                    getAuthToken
                  }
                />

              </section>

            )}

          </div>

        </main>

      </div>

    </div>
  );
}


function InfoCard({
  title,
  count,
}: {
  title: string;
  count: number;
}) {

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">

      <p className="text-sm text-slate-500">
        {title}
      </p>

      <p className="mt-2 text-2xl font-semibold text-slate-900">
        {count}
      </p>

      <p className="mt-1 text-xs text-slate-400">
        Items detected
      </p>

    </div>
  );
}