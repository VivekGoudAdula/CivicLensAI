import { Link } from "react-router-dom";
import { FileText, Plus } from "lucide-react";

import { PrimaryButton } from "@/components/ui/buttons";
import { EmptyState } from "@/components/empty-states/empty-state";

export function NoComplaintsEmptyState() {
  return (
    <EmptyState
      icon={FileText}
      title="No complaints yet"
      description="Citizen complaints will appear here once submitted. Start by registering the first grievance for your constituency."
      action={
        <PrimaryButton asChild>
          <Link to="/complaints/submit">
            <Plus className="h-4 w-4" />
            Register Complaint
          </Link>
        </PrimaryButton>
      }
    />
  );
}
