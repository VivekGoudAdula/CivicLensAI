import { motion } from "framer-motion";
import { CheckCircle2, FileText, History } from "lucide-react";
import { Link, useSearchParams } from "react-router-dom";

import { PageHeader } from "@/components/layout/PageHeader";
import { PrimaryButton, SecondaryButton } from "@/components/ui/buttons";
import { Card, CardContent } from "@/components/ui/card";

export function ComplaintSubmittedPage() {
  const [searchParams] = useSearchParams();
  const complaintId = searchParams.get("id");

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <PageHeader title="Complaint Submitted" />

      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.35 }}
      >
        <Card className="overflow-hidden">
          <CardContent className="flex flex-col items-center px-6 py-12 text-center">
            <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-emerald-500/10">
              <CheckCircle2 className="h-10 w-10 text-emerald-500" />
            </div>
            <h2 className="text-2xl font-bold">Thank you for reporting!</h2>
            <p className="mt-3 max-w-md text-muted-foreground">
              Your complaint has been registered successfully. Officials will review it and
              update the status as progress is made.
            </p>
            {complaintId ? (
              <p className="mt-4 rounded-lg bg-muted px-4 py-2 font-mono text-sm">
                Reference ID: {complaintId}
              </p>
            ) : null}

            <div className="mt-8 flex flex-wrap justify-center gap-3">
              {complaintId ? (
                <PrimaryButton asChild>
                  <Link to={`/complaints/${complaintId}`}>
                    <FileText className="h-4 w-4" />
                    View Details
                  </Link>
                </PrimaryButton>
              ) : null}
              <SecondaryButton asChild>
                <Link to="/complaints">
                  <History className="h-4 w-4" />
                  Complaint History
                </Link>
              </SecondaryButton>
              <SecondaryButton asChild>
                <Link to="/complaints/submit">Submit Another</Link>
              </SecondaryButton>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
