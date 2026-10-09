"use client";

import { useState } from "react";

import {
  queryRAG,
  type RAGQueryResponse,
} from "@/services/ragApi";


export default function RAGAssistant() {

  const [question, setQuestion] =
    useState("");

  const [result, setResult] =
    useState<RAGQueryResponse | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  async function handleAsk() {

    const trimmedQuestion =
      question.trim();


    if (!trimmedQuestion) {

      setError(
        "Please enter a question."
      );

      return;
    }


    setLoading(true);

    setError("");

    setResult(null);


    try {

      const data =
        await queryRAG(
          trimmedQuestion
        );

      setResult(data);

    } catch (err) {

      setError(
        err instanceof Error
          ? err.message
          : "Unable to get an answer."
      );

    } finally {

      setLoading(false);

    }
  }


  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

      <div className="mb-5">

        <p className="text-sm font-medium text-blue-600">
          Knowledge Base
        </p>

        <h2 className="mt-1 text-xl font-semibold text-slate-900">
          Interview Knowledge Assistant
        </h2>

        <p className="mt-1 text-sm text-slate-500">
          Ask questions about interview preparation and the system will use the knowledge base when relevant.
        </p>

      </div>


      <div className="space-y-3">

        <textarea
          value={question}
          onChange={(event) =>
            setQuestion(event.target.value)
          }
          placeholder="Ask an interview preparation question..."
          rows={5}
          maxLength={5000}
          className="w-full resize-y rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-2 focus:ring-blue-100"
        />


        <div className="flex items-center justify-between">

          <p className="text-xs text-slate-400">
            {question.length}/5000
          </p>


          <button
            type="button"
            onClick={handleAsk}
            disabled={loading}
            className="rounded-lg bg-slate-900 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading
              ? "Thinking..."
              : "Ask Question"}
          </button>

        </div>

      </div>


      {error && (

        <div className="mt-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>

      )}


      {loading && (

        <div className="mt-5 rounded-xl border border-slate-200 bg-slate-50 px-4 py-4">

          <p className="text-sm font-medium text-slate-700">
            Searching and generating an answer...
          </p>

          <p className="mt-1 text-xs text-slate-500">
            Relevant knowledge-base content is used when available; otherwise the assistant uses general knowledge.
          </p>

        </div>

      )}


      {result && (

        <div className="mt-6 space-y-6">

          <div>

            <p className="text-sm font-medium text-slate-500">
              Answer
            </p>

            <div className="mt-2 rounded-xl border border-slate-200 bg-slate-50 p-5">

              <p className="whitespace-pre-wrap text-sm leading-7 text-slate-800">
                {result.answer}
              </p>

            </div>

          </div>


          <div>

            <p className="text-sm font-medium text-slate-500">
              Answer source
            </p>

            <div className="mt-2 rounded-xl border border-slate-200 bg-white p-4">

              <p className="text-sm font-medium text-slate-800">
                {result.source_label}
              </p>

              <p className="mt-1 text-xs text-slate-500">

                {result.mode === "rag"
                  ? "The answer was generated using retrieved knowledge-base context."
                  : "No sufficiently relevant knowledge-base context was found, so Gemini answered using general knowledge."}

              </p>

            </div>

          </div>


          {result.mode === "rag" && (

            <div>

              <div className="flex items-center justify-between">

                <p className="text-sm font-medium text-slate-500">
                  Retrieved Sources
                </p>

                <p className="text-xs text-slate-400">
                  {result.sources.length} sources
                </p>

              </div>


              <div className="mt-3 space-y-3">

                {result.sources.map(
                  (source, index) => (

                    <article
                      key={source.chunk_id}
                      className="rounded-xl border border-slate-200 bg-white p-4"
                    >

                      <div className="flex items-center justify-between gap-4">

                        <p className="text-sm font-medium text-slate-800">
                          Source {index + 1}
                        </p>

                        <p className="text-xs text-slate-400">
                          Chunk {source.chunk_id}

                          {source.score !== null
                            ? ` · ${source.score.toFixed(3)}`
                            : ""}
                        </p>

                      </div>


                      <p className="mt-1 text-xs text-slate-500">
                        {source.source}
                      </p>


                      <p className="mt-3 text-sm leading-6 text-slate-600">
                        {source.text}
                      </p>

                    </article>

                  ),
                )}

              </div>

            </div>

          )}

        </div>

      )}

    </section>
  );
}