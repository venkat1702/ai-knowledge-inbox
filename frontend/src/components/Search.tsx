import { useState } from "react";
import { query } from "../services/api";

type Source = {
  item_id: string;
  title: string | null;
  chunk_index: number;
  chunk_text: string;
  score: number;
};

export default function Search() {
  const [searchQuery, setSearchQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(false);
  const [showSources, setShowSources] = useState(false);
  const [openSources, setOpenSources] = useState<Record<number, boolean>>({});

  const handleSearch = async () => {
    if (!searchQuery.trim() || searchQuery.length < 4) return;

    setLoading(true);

    try {
      const result = await query(searchQuery);

      setAnswer(result.answer);
      setSources(result.sources ?? []);

      setShowSources(false);
      setOpenSources({});
    } catch (error) {
      console.error(error);
      setAnswer("Something went wrong.");
      setSources([]);
    } finally {
      setLoading(false);
    }
  };

  const openSource = (index: number) => {
    setShowSources(true);

    setOpenSources((prev) => ({
      ...prev,
      [index]: true,
    }));

    setTimeout(() => {
      document.getElementById(`source-${index}`)?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }, 100);
  };

  const renderAnswer = (text: string) => {
    const parts = text.split(/(\[\d+(?:,\s*\d+)*\])/g);

    return parts.map((part, idx) => {
      const match = part.match(/\[(\d+(?:,\s*\d+)*)\]/);

      if (!match) {
        return <span key={idx}>{part}</span>;
      }

      const sourceIndexes = match[1]
        .split(",")
        .map((n) => Number(n.trim()) - 1)
        .filter((n) => n >= 0 && n < sources.length);

      return (
        <span key={idx} className="inline-flex gap-1">
          {sourceIndexes.map((sourceIndex) => (
            <button
              key={sourceIndex}
              onClick={() => openSource(sourceIndex)}
              className="rounded bg-blue-100 px-1.5 py-0.5 text-xs font-medium text-blue-700 hover:bg-blue-200"
            >
              [{sourceIndex + 1}]
            </button>
          ))}
        </span>
      );
    });
  };

  return (
    <div className="space-y-6 p-6">
      <div>
        <label className="mb-2 block text-sm font-bold uppercase">
          Ask a Question
        </label>

        <input
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="What do you want to know?"
          className="w-full border-4 border-black bg-white px-4 py-3 outline-none"
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              handleSearch();
            }
          }}
        />
      </div>

      <button
        disabled={loading}
        onClick={handleSearch}
        className="flex items-center gap-2 border-4 border-black bg-[#7dfdc0] px-6 py-3 font-black uppercase shadow-[4px_4px_0px_0px_#000] transition-all hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-[2px_2px_0px_0px_#000] disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading && (
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-black border-t-transparent" />
        )}

        {loading ? "Finding..." : "Ask"}
      </button>

      {answer && (
        <>
          <div className="border-4 border-black bg-[#7dfdc0] p-4 shadow-[6px_6px_0px_#000]">
            <h3 className="mb-3 text-lg font-black uppercase">Answer</h3>

            <div className="text-sm leading-7">{renderAnswer(answer)}</div>
          </div>

          <div className="border-4 border-black bg-white shadow-[6px_6px_0px_#000]">
            <button
              onClick={() => setShowSources(!showSources)}
              className="flex w-full items-center justify-between p-4 text-left font-black uppercase transition-transform hover:-translate-x-1 hover:-translate-y-1"
            >
              <span>Sources ({sources.length})</span>

              <span className="text-2xl leading-none">
                {showSources ? "−" : "+"}
              </span>
            </button>

            {showSources && (
              <div className="border-t-4 border-black p-4">
                <div className="space-y-4">
                  {sources.map((source, index) => (
                    <div
                      key={`${source.item_id}-${source.chunk_index}`}
                      id={`source-${index}`}
                      className="overflow-hidden border-4 border-black bg-[#ffe45e] shadow-[4px_4px_0px_#000]"
                    >
                      <button
                        onClick={() =>
                          setOpenSources((prev) => ({
                            ...prev,
                            [index]: !prev[index],
                          }))
                        }
                        className="flex w-full items-center justify-between p-3 text-left transition-transform hover:-translate-x-1 hover:-translate-y-1"
                      >
                        <div>
                          <div className="font-black uppercase">
                            Source {index + 1}
                          </div>

                          <div className="mt-1 text-xs font-semibold">
                            Similarity: {(source.score * 100).toFixed(1)}%
                          </div>
                        </div>

                        <span className="text-xl font-black">
                          {openSources[index] ? "−" : "+"}
                        </span>
                      </button>

                      {openSources[index] && (
                        <div className="border-t-4 border-black bg-white p-3">
                          <p className="text-sm whitespace-pre-wrap leading-6">
                            {source.chunk_text}
                          </p>
                        </div>
                      )}
                    </div>
                  ))}

                  {sources.length === 0 && (
                    <div className="border-4 border-black bg-[#d8c7ff] p-4 font-bold shadow-[4px_4px_0px_#000]">
                      No sources returned.
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
