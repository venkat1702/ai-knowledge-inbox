import { useCallback, useEffect, useState } from "react";
import { getItems, ingest } from "../services/api";

type Item = {
  id: string;
  source_type: "text" | "url";
  title: string;
  source_url: string | null;
  chunk_count: number;
  created_at: string;
  content_preview: string;
};

export default function Ingest() {
  const [contentType, setContentType] = useState<"note" | "url">("note");
  const [content, setContent] = useState("");

  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(false);
  const [itemsLoading, setItemsLoading] = useState(true);
  const [isItemsOpen, setIsItemsOpen] = useState(false);

  const loadItems = useCallback(async () => {
    try {
      setItemsLoading(true);

      const response = await getItems();

      setItems(response.items ?? []);
    } catch (error) {
      console.error("Failed to load items", error);
    } finally {
      setItemsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadItems();
  }, [loadItems]);

  const handleSave = async () => {
    if (!content.trim()) return;

    try {
      setLoading(true);

      if (contentType === "note") {
        await ingest({
          source_type: "text",
          content,
        });
      } else {
        await ingest({
          source_type: "url",
          url: content,
        });
      }

      setContent("");

      await loadItems();
      setIsItemsOpen(true);
    } catch (error) {
      console.error("Failed to ingest content", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 p-6">
      {/* Content Type */}
      <div>
        <label className="mb-2 block text-sm font-bold uppercase">
          Content Type
        </label>

        <select
          value={contentType}
          onChange={(e) => setContentType(e.target.value as "note" | "url")}
          className="w-full border-4 border-black bg-white px-4 py-3 font-medium outline-none"
        >
          <option value="note">Note</option>
          <option value="url">URL</option>
        </select>
      </div>

      {/* Content Input */}
      <div>
        <label className="mb-2 block text-sm font-bold uppercase">
          {contentType === "note" ? "Note Content" : "Website URL"}
        </label>

        {contentType === "note" ? (
          <textarea
            rows={6}
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Paste your notes..."
            className="w-full border-4 border-black bg-white p-4 outline-none"
          />
        ) : (
          <input
            type="url"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="https://example.com"
            className="w-full border-4 border-black bg-white px-4 py-3 outline-none"
          />
        )}
      </div>

      {/* Save Button */}
      <button
        disabled={loading}
        onClick={handleSave}
        className="flex items-center gap-2 border-4 border-black bg-[#7dfdc0] px-6 py-3 font-black uppercase shadow-[4px_4px_0px_0px_#000] transition-all hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-[2px_2px_0px_0px_#000] disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading && (
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-black border-t-transparent" />
        )}

        {loading ? "Saving..." : "Save"}
      </button>

      {/* Recent Items Accordion */}
      <div className="border-4 border-black bg-white shadow-[6px_6px_0px_0px_#000]">
        <button
          type="button"
          onClick={() => setIsItemsOpen((prev) => !prev)}
          className="flex w-full items-center justify-between bg-[#ffe45e] px-4 py-3 text-left font-black uppercase"
        >
          <span>Recent Items ({items.length})</span>

          <span
            className={`transition-transform duration-200 ${
              isItemsOpen ? "rotate-180" : ""
            }`}
          >
            ▼
          </span>
        </button>

        {isItemsOpen && (
          <div className="border-t-4 border-black p-4">
            {itemsLoading ? (
              <div className="font-medium">Loading items...</div>
            ) : items.length === 0 ? (
              <div className="font-medium">No items found.</div>
            ) : (
              <div className="space-y-3">
                {items.map((item) => (
                  <div
                    key={item.id}
                    className="border-4 border-black bg-[#f8f8f8] p-4 transition-all hover:-translate-y-1 hover:shadow-[4px_4px_0px_0px_#000]"
                  >
                    <div className="flex items-center justify-between gap-4">
                      <p className="font-bold">
                        {item.source_url ? "🌐 URL" : "📝 NOTE"}
                      </p>

                      <span className="border-2 border-black bg-white px-2 py-1 text-xs font-bold">
                        {item.chunk_count} chunks
                      </span>
                    </div>

                    {item.source_url && (
                      <p className="mt-2 break-all text-sm font-medium">
                        {item.source_url}
                      </p>
                    )}

                    <p className="mt-3 line-clamp-2 text-sm">
                      {item.content_preview}
                    </p>

                    <p className="mt-3 text-xs font-medium text-slate-600">
                      {new Date(item.created_at).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
