import { Building2 } from "lucide-react";

import { Badge } from "@/components/ui/badge";

export function DepartmentBadge({
  name,
  code,
}: {
  name: string;
  code?: string;
}) {
  return (
    <Badge variant="secondary" className="gap-1">
      <Building2 className="h-3 w-3" aria-hidden="true" />
      {code ? `${code} · ` : ""}
      {name}
    </Badge>
  );
}
