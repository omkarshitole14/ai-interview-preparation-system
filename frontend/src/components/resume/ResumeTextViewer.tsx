type ResumeTextViewerProps = {
  resumeText: string;
};

export default function ResumeTextViewer({
  resumeText,
}: ResumeTextViewerProps) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-6 py-5">
        <h3 className="font-semibold">Extracted Resume Text</h3>

        <p className="mt-1 text-sm text-slate-500">
          Text extracted directly from the uploaded PDF.
        </p>
      </div>

      <div className="max-h-[500px] overflow-y-auto px-6 py-5">
        <pre className="whitespace-pre-wrap font-sans text-sm leading-7 text-slate-700">
          {resumeText}
        </pre>
      </div>
    </div>
  );
}