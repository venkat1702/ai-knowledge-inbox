import { useState } from "react";
import Search from "./components/Search";
import Ingest from "./components/Ingest";

export default function App() {
  const [activeTab, setActiveTab] = useState<"ingest" | "search">("ingest");

  return (
    <div className="min-h-screen bg-[#fff8e7] p-6">
      <div className="mx-auto max-w-5xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="mt-6 text-5xl font-black tracking-tight text-black">
            AI Knowledge Inbox
          </h1>

          <p className="mt-3 max-w-2xl text-base font-medium text-black">
            Save notes, ingest URLs, and chat with your personal knowledge base.
          </p>
        </div>

        {/* Main Card */}
        <div className="border-4 border-black bg-white shadow-[10px_10px_0px_0px_#000]">
          {/* Tabs */}
          <div className="flex border-b-4 border-black">
            <button
              onClick={() => setActiveTab("ingest")}
              className={`flex-1 border-r-4 border-black px-6 py-4 text-sm font-black uppercase transition-all ${
                activeTab === "ingest"
                  ? "bg-[#ffe45e]"
                  : "bg-white hover:bg-[#f3f3f3]"
              }`}
            >
              📥 Ingest
            </button>

            <button
              onClick={() => setActiveTab("search")}
              className={`flex-1 px-6 py-4 text-sm font-black uppercase transition-all ${
                activeTab === "search"
                  ? "bg-[#d8c7ff]"
                  : "bg-white hover:bg-[#f3f3f3]"
              }`}
            >
              🔍 Search
            </button>
          </div>

          {/* Content */}
          <div className="bg-white p-6">
            {activeTab === "ingest" && <Ingest />}
            {activeTab === "search" && <Search />}
          </div>
        </div>
      </div>
    </div>
  );
}
