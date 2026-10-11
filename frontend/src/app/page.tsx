
"use client";

import {
  type DragEvent,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import { useRouter } from "next/navigation";

import {
  uploadResume,
  getResumeHistory,
  getSavedResume,
  type ResumeHistoryItem,
} from "@/services/resumeApi";

import type { ResumeAnalysisResult } from "@/types/resume";

import {
  generateInterviewQuestions,
  getSavedInterview,
  type InterviewQuestionResponse,
  type InterviewType,
  type SavedInterviewSession,
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

import { logoutUser } from "@/services/authApi";

type WorkspaceTab = "resume" | "interview" | "reports";

export default function Home() {
  const router = useRouter();

  const [authenticated, setAuthenticated] = useState(false);
  const [checkingAuth, setCheckingAuth] = useState(true);

  const [activeTab, setActiveTab] =
    useState<WorkspaceTab>("resume");

  const [generatingInterview, setGeneratingInterview] =
    useState(false);

  const [interviewQuestions, setInterviewQuestions] =
    useState<InterviewQuestionResponse | null>(null);

  const [sessionId, setSessionId] =
    useState<number | null>(null);

  const [savedInterview, setSavedInterview] =
    useState<SavedInterviewSession | null>(null);

  const [resumeHistory, setResumeHistory] =
    useState<ResumeHistoryItem[]>([]);

  const [file, setFile] = useState<File | null>(null);

  const [result, setResult] =
    useState<ResumeAnalysisResult | null>(null);

  const [loading, setLoading] = useState(false);
  const [loadingSavedData, setLoadingSavedData] =
    useState(true);

  const [error, setError] = useState("");
  const [restoreError, setRestoreError] = useState("");

  const fileInputRef = useRef<HTMLInputElement>(null);

  const getAuthToken = useCallback((): string => {
    const token = getAccessToken();

    if (!token) {
      removeAccessToken();
      router.replace("/login");

      throw new Error(
        "Your session has expired. Please log in again.",
      );
    }

    return token;
  }, [router]);

  /*
   * Restore the saved interview for the currently selected session.
   */
  const refreshSavedInterview = useCallback(async () => {
    if (!sessionId) {
      setSavedInterview(null);
      setInterviewQuestions(null);
      return;
    }

    const data = await getSavedInterview(
      sessionId,
      getAuthToken(),
    );

    setSavedInterview(data);

    setInterviewQuestions({
      questions: data.questions.map((question) => ({
        id: question.id,
        question: question.question,
        category: question.category,
        difficulty: question.difficulty,
        expected_topics: question.expected_topics,
      })),
    });
  }, [sessionId, getAuthToken]);

  /*
   * Restore the most recent saved resume and interview session.
   */
  const restoreSavedData = useCallback(async () => {
    setLoadingSavedData(true);
    setRestoreError("");

    try {
      const token = getAuthToken();
      const history = await getResumeHistory(token);

      setResumeHistory(history);

      if (history.length === 0) {
        setResult(null);
        setSessionId(null);
        setSavedInterview(null);
        setInterviewQuestions(null);
        return;
      }

      const sortedResumes = [...history].sort(
        (a, b) =>
          new Date(b.created_at).getTime() -
          new Date(a.created_at).getTime(),
      );

      const latestResume = sortedResumes[0];

      const savedResume = await getSavedResume(
        latestResume.resume_id,
        token,
      );

      setResult(savedResume);

      const sortedSessions = [...latestResume.sessions].sort(
        (a, b) =>
          new Date(b.created_at).getTime() -
          new Date(a.created_at).getTime(),
      );

      if (sortedSessions.length === 0) {
        setSessionId(savedResume.session_id);
        setSavedInterview(null);
        setInterviewQuestions(null);
        return;
      }

      setSessionId(sortedSessions[0].session_id);

      const interview = await getSavedInterview(
        sortedSessions[0].session_id,
        token,
      );

      setSavedInterview(interview);

      setInterviewQuestions({
        questions: interview.questions.map((question) => ({
          id: question.id,
          question: question.question,
          category: question.category,
          difficulty: question.difficulty,
          expected_topics: question.expected_topics,
        })),
      });
    } catch (err) {
      console.error("Failed to restore saved data:", err);

      setRestoreError(
        err instanceof Error
          ? err.message
          : "Could not restore your saved data.",
      );
    } finally {
      setLoadingSavedData(false);
    }
  }, [getAuthToken]);

  /*
   * Check authentication, then restore saved data.
   */
  useEffect(() => {
    let cancelled = false;

    async function initialize() {
      const token = getAccessToken();

      if (!token) {
        router.replace("/login");
        setCheckingAuth(false);
        return;
      }

      setAuthenticated(true);

      try {
        await restoreSavedData();
      } finally {
        if (!cancelled) {
          setCheckingAuth(false);
        }
      }
    }

    void initialize();

    return () => {
      cancelled = true;
    };
  }, [router, restoreSavedData]);

  /*
   * Logout.
   */
  const handleLogout = async () => {
    try {
      await logoutUser();
    } catch (err) {
      console.error("Logout request failed:", err);
    } finally {
      removeAccessToken();
      setAuthenticated(false);
      router.replace("/login");
    }
  };

  /*
   * Select a PDF resume.
   */
  const selectFile = (selectedFile: File | null) => {
    if (!selectedFile) return;

    if (
      selectedFile.type !== "application/pdf" &&
      !selectedFile.name.toLowerCase().endsWith(".pdf")
    ) {
      setError("Please select a PDF resume.");
      return;
    }

    setFile(selectedFile);
    setError("");
  };

  /*
   * Drag and drop.
   */
  const handleDrop = (
    event: DragEvent<HTMLDivElement>,
  ) => {
    event.preventDefault();
    selectFile(event.dataTransfer.files[0] ?? null);
  };

  /*
   * Upload and analyze a new resume.
   */
  const handleAnalyze = async () => {
    if (!file) {
      setError("Please select a PDF resume first.");
      return;
    }

    setLoading(true);
    setError("");
    setRestoreError("");

    try {
      const data = await uploadResume(file, getAuthToken());

      setResult(data);
      setSessionId(data.session_id);
      setSavedInterview(null);
      setInterviewQuestions(null);
      setActiveTab("resume");

      // Refresh the user's saved resume history.
      const history = await getResumeHistory(getAuthToken());
      setResumeHistory(history);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong while analyzing the resume.",
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
        "Please analyze or restore a resume before generating interview questions.",
      );
      return;
    }

    setError("");
    setGeneratingInterview(true);

    try {
      const token = getAuthToken();

      await generateInterviewQuestions(
        sessionId,
        interviewType,
        questionCount,
        token,
      );

      // Fetch the saved questions so their database IDs and
      // any previously stored answers are available.
      const interview = await getSavedInterview(
        sessionId,
        token,
      );

      setSavedInterview(interview);

      setInterviewQuestions({
        questions: interview.questions.map((question) => ({
          id: question.id,
          question: question.question,
          category: question.category,
          difficulty: question.difficulty,
          expected_topics: question.expected_topics,
        })),
      });

      setActiveTab("interview");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to generate interview questions.",
      );
    } finally {
      setGeneratingInterview(false);
    }
  };

  /*
   * Authentication loading screen.
   */
  if (checkingAuth || loadingSavedData) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-50">
        <div className="text-center">
          <p className="text-sm font-medium text-slate-700">
            {checkingAuth
              ? "Checking authentication..."
              : "Restoring your saved work..."}
          </p>
          <p className="mt-1 text-xs text-slate-400">
            Please wait
          </p>
        </div>
      </main>
    );
  }

  if (!authenticated) return null;

  const totalQuestions =
    savedInterview?.questions.length ?? 0;

  const evaluatedQuestions =
    savedInterview?.questions.filter(
      (question) => question.evaluation !== null,
    ).length ?? 0;

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
              <NavButton
                active={activeTab === "resume"}
                onClick={() => setActiveTab("resume")}
              >
                Analyze Resume
              </NavButton>

              <NavButton
                active={activeTab === "interview"}
                onClick={() => setActiveTab("interview")}
              >
                Interview
              </NavButton>

              <NavButton
                active={activeTab === "reports"}
                onClick={() => setActiveTab("reports")}
              >
                Reports
              </NavButton>
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
          <header className="border-b border-slate-200 bg-white">
            <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
              <div>
                <p className="text-sm font-medium text-slate-500">
                  InterviewAI Workspace
                </p>
                <h2 className="mt-1 text-2xl font-semibold tracking-tight">
                  {activeTab === "resume"
                    ? "Prepare your interview"
                    : activeTab === "interview"
                      ? "Interview practice"
                      : "Interview reports"}
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
          
          
          {/* Mobile navigation */}
          <nav
            aria-label="Mobile workspace navigation"
            className="grid grid-cols-3 gap-2 border-b border-slate-200 bg-white px-3 py-3 md:hidden"
          >
            <MobileNavButton
              active={activeTab === "resume"}
              onClick={() => setActiveTab("resume")}
            >
              Resume
            </MobileNavButton>

            <MobileNavButton
              active={activeTab === "interview"}
              onClick={() => setActiveTab("interview")}
            >
              Interview
            </MobileNavButton>

            <MobileNavButton
              active={activeTab === "reports"}
              onClick={() => setActiveTab("reports")}
            >
              Reports
            </MobileNavButton>
          </nav>
          <div className="mx-auto max-w-7xl space-y-8 px-6 py-8">
            {restoreError && (
              <div
                role="alert"
                className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800"
              >
                <p>{restoreError}</p>
                <button
                  type="button"
                  onClick={() => void restoreSavedData()}
                  className="mt-2 font-semibold underline"
                >
                  Try restoring again
                </button>
              </div>
            )}

            {activeTab === "resume" && (
              <>
                <ResumeUpload
                  file={file}
                  loading={loading}
                  error={error}
                  fileInputRef={fileInputRef}
                  onFileSelect={selectFile}
                  onDrop={handleDrop}
                  onAnalyze={handleAnalyze}
                />

                <RAGAssistant />

                {result && (
                  <section className="space-y-6">
                    <div>
                      <p className="text-sm font-medium text-blue-600">
                        Analysis complete
                      </p>
                      <h3 className="mt-1 text-2xl font-semibold tracking-tight">
                        {result.candidate_profile.name ||
                          "Candidate Profile"}
                      </h3>
                      <p className="mt-1 text-sm text-slate-500">
                        Candidate Profile
                      </p>
                      <p className="mt-1 text-xs text-slate-400">
                        Resume: {result.filename}
                      </p>
                    </div>

                    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                      <InfoCard
                        title="Education"
                        count={result.candidate_profile.education.length}
                      />
                      <InfoCard
                        title="Skills"
                        count={result.candidate_profile.skills.length}
                      />
                      <InfoCard
                        title="Projects"
                        count={result.candidate_profile.projects.length}
                      />
                      <InfoCard
                        title="Experience"
                        count={result.candidate_profile.experience.length}
                      />
                    </div>

                    <ResumeTextViewer
                      resumeText={result.resume_text}
                    />

                    <CandidateProfile
                      profile={result.candidate_profile}
                    />
                  </section>
                )}

                {!result && resumeHistory.length > 0 && (
                  <section className="rounded-xl border border-slate-200 bg-white p-5">
                    <h3 className="font-semibold">
                      Your saved resumes
                    </h3>
                    <p className="mt-1 text-sm text-slate-500">
                      {resumeHistory.length} saved resume record(s).
                      The latest one is restored automatically.
                    </p>
                  </section>
                )}
              </>
            )}

            {activeTab === "interview" && (
              <>
                {error && (
                  <p
                    role="alert"
                    className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700"
                  >
                    {error}
                  </p>
                )}

                {result ? (
                  <InterviewQuestions
                    interviewQuestions={interviewQuestions}
                    generating={generatingInterview}
                    onGenerate={handleGenerateInterview}
                    tokenGetter={getAuthToken}
                    sessionId={sessionId}
                    savedInterview={savedInterview}
                    onRefreshSavedInterview={refreshSavedInterview}
                  />
                ) : (
                  <section className="rounded-xl border border-slate-200 bg-white p-6">
                    <h3 className="font-semibold">
                      Analyze a resume first
                    </h3>
                    <p className="mt-2 text-sm text-slate-500">
                      Upload a resume or restore a saved resume before
                      generating interview questions.
                    </p>
                    <button
                      type="button"
                      onClick={() => setActiveTab("resume")}
                      className="mt-4 rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-slate-800"
                    >
                      Go to resume analysis
                    </button>
                  </section>
                )}
              </>
            )}

            {activeTab === "reports" && (
              <section className="space-y-5 rounded-xl border border-slate-200 bg-white p-6">
                <div>
                  <h3 className="text-lg font-semibold">
                    Interview progress
                  </h3>
                  <p className="mt-1 text-sm text-slate-500">
                    A summary of the currently restored interview session.
                  </p>
                </div>

                <div className="grid gap-4 sm:grid-cols-3">
                  <InfoCard
                    title="Questions"
                    count={totalQuestions}
                  />
                  <InfoCard
                    title="Evaluated"
                    count={evaluatedQuestions}
                  />
                  <InfoCard
                    title="Remaining"
                    count={Math.max(
                      0,
                      totalQuestions - evaluatedQuestions,
                    )}
                  />
                </div>

                {savedInterview ? (
                  <p className="text-sm text-slate-600">
                    Session status: {savedInterview.status}
                  </p>
                ) : (
                  <p className="text-sm text-slate-500">
                    No saved interview session is available yet.
                    Generate and evaluate interview questions to track
                    progress here.
                  </p>
                )}

                <p className="text-xs text-slate-400">
                  This is a progress summary, not a downloadable report.
                  PDF report generation requires a report endpoint or
                  client-side report implementation.
                </p>

                <button
                  type="button"
                  onClick={() => setActiveTab("interview")}
                  className="rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-slate-800"
                >
                  Open interview
                </button>
              </section>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

function NavButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full rounded-lg px-3 py-2.5 text-left text-sm ${
        active
          ? "bg-slate-100 font-medium text-slate-900"
          : "text-slate-500 hover:bg-slate-50"
      }`}
    >
      {children}
    </button>
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
      <p className="text-sm text-slate-500">{title}</p>
      <p className="mt-2 text-2xl font-semibold text-slate-900">
        {count}
      </p>
      <p className="mt-1 text-xs text-slate-400">Items detected</p>
    </div>
  );
}


function MobileNavButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-current={active ? "page" : undefined}
      className={`min-h-11 rounded-lg px-2 py-3 text-center text-sm font-medium transition-colors ${
        active
          ? "bg-slate-900 text-white"
          : "bg-slate-100 text-slate-600 hover:bg-slate-200"
      }`}
    >
      {children}
    </button>
  );
}
