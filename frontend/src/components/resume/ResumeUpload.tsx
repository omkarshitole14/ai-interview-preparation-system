"use client";

import { DragEvent, RefObject } from "react";

type ResumeUploadProps = {
  file: File | null;
  loading: boolean;
  error: string;
  fileInputRef: RefObject<HTMLInputElement | null>;
  onFileSelect: (file: File | null) => void;
  onDrop: (event: DragEvent<HTMLDivElement>) => void;
  onAnalyze: () => void;
};

export default function ResumeUpload({
  file,
  loading,
  error,
  fileInputRef,
  onFileSelect,
  onDrop,
  onAnalyze,
}: ResumeUploadProps) {
  return (
    <section>
      <div className="mb-4">
        <h3 className="text-lg font-semibold">Upload your resume</h3>

        <p className="mt-1 text-sm text-slate-500">
          Upload a PDF resume to extract your profile and prepare for
          the interview.
        </p>
      </div>

      <div
        onDragOver={(event) => event.preventDefault()}
        onDrop={onDrop}
        className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm"
      >
        <div className="rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 px-6 py-12 text-center">
          <h4 className="text-base font-semibold">
            Drop your resume here
          </h4>

          <p className="mt-2 text-sm text-slate-500">
            PDF files only
          </p>

          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="mt-6 rounded-lg bg-slate-900 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-slate-800"
          >
            Choose Resume
          </button>

          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,application/pdf"
            className="hidden"
            onChange={(event) =>
              onFileSelect(event.target.files?.[0] || null)
            }
          />

          {file && (
            <div className="mx-auto mt-6 max-w-md rounded-lg border border-slate-200 bg-white px-4 py-3 text-left">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                Selected file
              </p>

              <p className="mt-1 truncate text-sm font-medium text-slate-800">
                {file.name}
              </p>
            </div>
          )}

          <button
            type="button"
            onClick={onAnalyze}
            disabled={!file || loading}
            className="mt-6 rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {loading ? "Analyzing Resume..." : "Analyze Resume"}
          </button>
        </div>

        {error && (
          <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}
      </div>
    </section>
  );
}