"use client";

import { useEffect, useState } from "react";
import {
  evaluateInterviewAnswer,
  type InterviewAnswerEvaluation,
  type InterviewQuestionResponse,
  type InterviewType,
  type SavedInterviewSession,
} from "@/services/interviewApi";

type InterviewQuestionsProps = {
  interviewQuestions: InterviewQuestionResponse | null;
  generating: boolean;
  onGenerate: (
    interviewType: InterviewType,
    questionCount: 5 | 10 | 15,
  ) => void;
  tokenGetter: () => string;
  sessionId: number | null;
  savedInterview: SavedInterviewSession | null;
  onRefreshSavedInterview: () => Promise<void>;
};

const interviewTypeOptions: Array<{
  value: InterviewType;
  label: string;
}> = [
  { value: "mixed", label: "Mixed Interview" },
  { value: "technical", label: "Technical" },
  { value: "hr", label: "HR / Behavioral" },
  { value: "resume", label: "Resume-Based" },
  { value: "coding", label: "Coding" },
  { value: "ml_ai", label: "ML / AI" },
  { value: "genai_rag", label: "GenAI / RAG" },
];

function isCodingEvaluation(
  evaluation: InterviewAnswerEvaluation,
): boolean {
  return Boolean(
    evaluation.time_complexity && evaluation.space_complexity,
  );
}

export default function InterviewQuestions({
  interviewQuestions,
  generating,
  onGenerate,
  tokenGetter,
  sessionId,
  savedInterview,
  onRefreshSavedInterview,
}: InterviewQuestionsProps) {
  const [interviewType, setInterviewType] =
    useState<InterviewType>("mixed");

  const [questionCount, setQuestionCount] =
    useState<5 | 10 | 15>(10);

  const [answers, setAnswers] =
    useState<Record<number, string>>({});

  const [evaluating, setEvaluating] =
    useState<number | null>(null);

  const [evaluations, setEvaluations] =
    useState<Record<number, InterviewAnswerEvaluation>>({});

  const [evaluationErrors, setEvaluationErrors] =
    useState<Record<number, string>>({});

  useEffect(() => {
  if (!savedInterview) {
    setAnswers({});
    setEvaluations({});
    return;
  }

  const nextAnswers: Record<number, string> = {};
  const nextEvaluations: Record<
    number,
    InterviewAnswerEvaluation
  > = {};

  for (const question of savedInterview.questions) {
    if (question.answer !== null) {
      nextAnswers[question.id] = question.answer;
    }

    if (question.evaluation !== null) {
      nextEvaluations[question.id] =
        question.evaluation;
    }
  }

  setAnswers(nextAnswers);
  setEvaluations(nextEvaluations);
}, [savedInterview]);

  const handleEvaluate = async (questionId: number) => {
    const answer = answers[questionId]?.trim();

    const question =
      interviewQuestions?.questions.find(
        (item) => item.id === questionId,
      );

    if (!question) return;

    if (!answer) {
      setEvaluationErrors((prev) => ({
        ...prev,
        [questionId]: "Please write an answer first.",
      }));

      return;
    }

    if (answer.length < 20) {
      setEvaluationErrors((prev) => ({
        ...prev,
        [questionId]:
          "Please provide a more detailed answer.",
      }));

      return;
    }

    setEvaluating(questionId);

    setEvaluationErrors((prev) => ({
      ...prev,
      [questionId]: "",
    }));

    setEvaluations((prev) => {
      const updated = { ...prev };
      delete updated[questionId];
      return updated;
    });

    try {
      const result = await evaluateInterviewAnswer(
        questionId,
        answer,
        tokenGetter(),
      );

      setEvaluations((prev) => ({
  ...prev,
  [questionId]: result,
}));

await onRefreshSavedInterview();
    } catch (error) {
      setEvaluationErrors((prev) => ({
        ...prev,
        [questionId]:
          error instanceof Error
            ? error.message
            : "Answer evaluation failed.",
      }));
    } finally {
      setEvaluating(null);
    }
  };

  return (
    <section className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div>
          <h3 className="font-semibold">
            Interview Preparation
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            Choose the interview style and question count
            before generating your interview.
          </p>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <label className="text-sm font-medium text-slate-700">
            Interview type

            <select
              value={interviewType}
              onChange={(event) =>
                setInterviewType(
                  event.target.value as InterviewType,
                )
              }
              disabled={generating}
              className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none focus:border-slate-500 focus:ring-2 focus:ring-slate-100"
            >
              {interviewTypeOptions.map((option) => (
                <option
                  key={option.value}
                  value={option.value}
                >
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <label className="text-sm font-medium text-slate-700">
            Number of questions

            <select
              value={questionCount}
              onChange={(event) =>
                setQuestionCount(
                  Number(event.target.value) as 5 | 10 | 15,
                )
              }
              disabled={generating}
              className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none focus:border-slate-500 focus:ring-2 focus:ring-slate-100"
            >
              <option value={5}>5</option>
              <option value={10}>10</option>
              <option value={15}>15</option>
            </select>
          </label>

          <div className="flex items-end">
            <button
              type="button"
              onClick={() =>
                onGenerate(
                  interviewType,
                  questionCount,
                )
              }
              disabled={generating}
              className="w-full rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {generating
                ? "Generating Questions..."
                : "Generate Interview"}
            </button>
          </div>
        </div>
      </div>

      {interviewQuestions && (
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="border-b border-slate-200 pb-4">
            <h3 className="font-semibold">
              Interview Questions
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              {interviewQuestions.questions.length} questions
              generated from your resume and selected interview
              type.
            </p>
          </div>

          <div className="mt-6 space-y-4">
            {interviewQuestions.questions.map(
              (item, index) => {
                const questionId = item.id;

                const isCoding =
                  item.category.toLowerCase() ===
                  "coding";

                const evaluation =
                  evaluations[questionId];

                return (
                  <div
                    key={questionId}
                    className="rounded-xl border border-slate-200 bg-slate-50 p-5"
                  >
                    <div className="flex items-center justify-between gap-4">
                      <span className="text-xs font-medium uppercase tracking-wide text-slate-400">
                        Question {index + 1}
                      </span>

                      <div className="flex flex-wrap gap-2">
                        <span className="rounded-full bg-white px-3 py-1 text-xs text-slate-600">
                          {item.category}
                        </span>

                        <span className="rounded-full bg-white px-3 py-1 text-xs text-slate-600">
                          {item.difficulty}
                        </span>
                      </div>
                    </div>

                    <p className="mt-4 whitespace-pre-wrap text-sm font-medium leading-6 text-slate-800">
                      {item.question}
                    </p>

                    {item.expected_topics.length > 0 && (
                      <div className="mt-4">
                        <p className="text-xs font-medium text-slate-500">
                          Expected topics
                        </p>

                        <div className="mt-2 flex flex-wrap gap-2">
                          {item.expected_topics.map(
                            (topic, topicIndex) => (
                              <span
                                key={topicIndex}
                                className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs text-slate-600"
                              >
                                {topic}
                              </span>
                            ),
                          )}
                        </div>
                      </div>
                    )}

                    <div className="mt-6">
                      <label
                        htmlFor={`answer-${questionId}`}
                        className="text-sm font-medium text-slate-700"
                      >
                        {isCoding
                          ? "Your code"
                          : "Your answer"}
                      </label>

                      <textarea
                        id={`answer-${questionId}`}
                        value={
                          answers[questionId] || ""
                        }
                        disabled={Boolean(evaluations[questionId])}
                        onChange={(event) => {
                          const value =
                            event.target.value;

                          setAnswers((prev) => ({
                            ...prev,
                            [questionId]: value,
                          }));

                          setEvaluations((prev) => {
                            const updated = {
                              ...prev,
                            };

                            delete updated[questionId];

                            return updated;
                          });

                          setEvaluationErrors(
                            (prev) => ({
                              ...prev,
                              [questionId]: "",
                            }),
                          );
                        }}
                        placeholder={
                          isCoding
                            ? "Write your solution here..."
                            : "Write your answer here..."
                        }
                        rows={isCoding ? 12 : 5}
                        maxLength={10000}
                        spellCheck={!isCoding}
                        className={`mt-2 w-full rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-800 outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-100 ${
                          isCoding
                            ? "font-mono"
                            : ""
                        }`}
                      />

                      <div className="mt-3 flex items-center justify-between gap-4">
                        <p className="text-xs text-slate-400">
                          {
                            (
                              answers[
                                questionId
                              ] || ""
                            ).length
                          }
                          /10000
                        </p>

                        <button
                          type="button"
                          onClick={() =>
                            handleEvaluate(
                              questionId,
                            )
                          }
                          disabled={
                            evaluating !== null ||
                            Boolean(evaluations[questionId])

                          }
                          className="rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                        >
                          {evaluating ===
                          questionId
                            ? "Evaluating..."
                            : isCoding
                              ? "Evaluate Code"
                              : "Evaluate Answer"}
                        </button>
                      </div>

                      {evaluationErrors[
                        questionId
                      ] && (
                        <p className="mt-2 text-sm text-red-600">
                          {
                            evaluationErrors[
                              questionId
                            ]
                          }
                        </p>
                      )}
                    </div>

                    {evaluation && (
                      <div className="mt-5 rounded-xl border border-slate-200 bg-white p-5">
                        <div className="flex items-center justify-between">
                          <h4 className="text-sm font-semibold text-slate-800">
                            {isCoding
                              ? "Code Evaluation"
                              : "Answer Evaluation"}
                          </h4>

                          <span className="text-sm font-semibold text-slate-700">
                            Score:{" "}
                            {evaluation.score}/10
                          </span>
                        </div>

                        {isCoding &&
                          isCodingEvaluation(
                            evaluation,
                          ) && (
                            <div className="mt-4 grid gap-3 sm:grid-cols-2">
                              <div className="rounded-lg bg-slate-50 p-3">
                                <p className="text-xs font-medium text-slate-500">
                                  Time complexity
                                </p>

                                <p className="mt-1 text-sm text-slate-700">
                                  {
                                    evaluation.time_complexity
                                  }
                                </p>
                              </div>

                              <div className="rounded-lg bg-slate-50 p-3">
                                <p className="text-xs font-medium text-slate-500">
                                  Space complexity
                                </p>

                                <p className="mt-1 text-sm text-slate-700">
                                  {
                                    evaluation.space_complexity
                                  }
                                </p>
                              </div>
                            </div>
                          )}

                        <div className="mt-4">
                          <p className="text-xs font-medium text-slate-500">
                            Feedback
                          </p>

                          <p className="mt-1 text-sm leading-6 text-slate-700">
                            {evaluation.feedback}
                          </p>
                        </div>

                        {evaluation.strengths
                          .length > 0 && (
                          <div className="mt-4">
                            <p className="text-xs font-medium text-slate-500">
                              Strengths
                            </p>

                            <ul className="mt-2 space-y-1">
                              {evaluation.strengths.map(
                                (strength, i) => (
                                  <li
                                    key={i}
                                    className="text-sm text-slate-700"
                                  >
                                    {strength}
                                  </li>
                                ),
                              )}
                            </ul>
                          </div>
                        )}

                        {evaluation.improvements
                          .length > 0 && (
                          <div className="mt-4">
                            <p className="text-xs font-medium text-slate-500">
                              Improvements
                            </p>

                            <ul className="mt-2 space-y-1">
                              {evaluation.improvements.map(
                                (
                                  improvement,
                                  i,
                                ) => (
                                  <li
                                    key={i}
                                    className="text-sm text-slate-700"
                                  >
                                    {improvement}
                                  </li>
                                ),
                              )}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              },
            )}
          </div>
        </div>
      )}
    </section>
  );
}