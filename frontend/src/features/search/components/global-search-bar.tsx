import { useNavigate } from "react-router-dom";
import { useState } from "react";

import { SearchBox } from "@/components/ui/search-box";

interface GlobalSearchBarProps {
  className?: string;
}

export function GlobalSearchBar({ className }: GlobalSearchBarProps) {
  const navigate = useNavigate();
  const [value, setValue] = useState("");

  const handleSearch = (query: string) => {
    const trimmed = query.trim();
    if (!trimmed) return;
    navigate(`/search?q=${encodeURIComponent(trimmed)}`);
  };

  return (
    <SearchBox
      className={className}
      value={value}
      onChange={setValue}
      onSearch={handleSearch}
      placeholder="Search complaints, clusters, villages..."
      aria-label="Global search"
    />
  );
}
