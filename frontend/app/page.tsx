"use client";

import { useState } from "react";

interface ExtractionResult {
  file_name: string;
  page_count: number | null;
  extraction_method: string | null;
  extracted_text: string | null;
  success: boolean;
}

export default function Home() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [url, setUrl] = useState("");
  const [results, setResults] = useState<ExtractionResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const API_URL = "http://localhost:8000";

  async function handleFileUpload() {
    if (!files || files.length === 0) return;

    setLoading(true);
    setError("");

    const formData = new FormData();
    if (files.length === 1) {
      formData.append("file", files[0]);
      try {
        const res = await fetch(`${API_URL}/extract/file`, {
          method: "POST",
          body: formData,
        });
        if (!res.ok) throw new Error("Extraction failed");
        const data = await res.json();
        setResults([data]);
      } catch {
        setError("Failed to extract text from file");
      }
    } else {
      Array.from(files).forEach((f) => formData.append("files", f));
      try {
        const res = await fetch(`${API_URL}/extract/batch`, {
          method: "POST",
          body: formData,
        });
        if (!res.ok) throw new Error("Extraction failed");
        const data = await res.json();
        setResults(data.results);
      } catch {
        setError("Failed to extract text from files");
      }
    }

    setLoading(false);
  }

  async function handleUrlExtract() {
    if (!url.trim()) return;

    setLoading(true);
    setError("");

    try {
      const res = await fetch(`${API_URL}/extract/url`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      if (!res.ok) throw new Error("Extraction failed");
      const data = await res.json();
      setResults([data]);
    } catch {
      setError("Failed to extract text from URL");
    }

    setLoading(false);
  }

  function downloadResults(format: "json" | "csv") {
    const content =
      format === "json"
        ? JSON.stringify(results, null, 2)
        : convertToCSV(results);

    const blob = new Blob([content], {
      type: format === "json" ? "application/json" : "text/csv",
    });
    const blobUrl = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = blobUrl;
    a.download = `extraction.${format}`;
    a.click();
    URL.revokeObjectURL(blobUrl);
  }

  function convertToCSV(data: ExtractionResult[]): string {
    const headers = [
      "file_name",
      "page_count",
      "extraction_method",
      "extracted_text",
      "success",
    ];
    const rows = data.map((r) =>
      headers.map((h) => JSON.stringify(r[h as keyof ExtractionResult] ?? "")).join(",")
    );
    return [headers.join(","), ...rows].join("\n");
  }

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Document Text Extraction</h1>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Upload Files</h2>
          <p className="text-gray-600 text-sm mb-4">
            Supported: PDF, DOCX, TXT, PNG, JPG
          </p>
          <input
            type="file"
            multiple
            accept=".pdf,.docx,.txt,.png,.jpg,.jpeg,.tiff,.bmp"
            onChange={(e) => setFiles(e.target.files)}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 mb-4"
          />
          <button
            onClick={handleFileUpload}
            disabled={!files || loading}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Processing..." : "Extract Text"}
          </button>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Extract from URL</h2>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/document.pdf"
            className="w-full border rounded px-3 py-2 mb-4"
          />
          <button
            onClick={handleUrlExtract}
            disabled={!url.trim() || loading}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Processing..." : "Extract from URL"}
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {results.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">
                Results ({results.length})
              </h2>
              <div className="space-x-2">
                <button
                  onClick={() => downloadResults("json")}
                  className="text-sm bg-gray-100 px-3 py-1 rounded hover:bg-gray-200"
                >
                  Download JSON
                </button>
                <button
                  onClick={() => downloadResults("csv")}
                  className="text-sm bg-gray-100 px-3 py-1 rounded hover:bg-gray-200"
                >
                  Download CSV
                </button>
              </div>
            </div>

            <div className="space-y-4">
              {results.map((result, i) => (
                <div key={i} className="border rounded p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-medium">{result.file_name}</h3>
                    <span
                      className={`text-xs px-2 py-1 rounded ${
                        result.success
                          ? "bg-green-100 text-green-700"
                          : "bg-red-100 text-red-700"
                      }`}
                    >
                      {result.success ? "Success" : "Failed"}
                    </span>
                  </div>
                  <div className="text-sm text-gray-500 mb-2">
                    {result.page_count && <span>Pages: {result.page_count} | </span>}
                    Method: {result.extraction_method || "N/A"}
                  </div>
                  {result.extracted_text && (
                    <pre className="bg-gray-50 p-3 rounded text-sm overflow-auto max-h-64 whitespace-pre-wrap">
                      {result.extracted_text.slice(0, 2000)}
                      {result.extracted_text.length > 2000 && "..."}
                    </pre>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}