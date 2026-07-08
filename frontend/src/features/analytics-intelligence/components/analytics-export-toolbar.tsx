import { Download, FileJson, Image, Printer } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  downloadElementAsPng,
  exportToCsv,
  exportToJson,
  printDashboard,
} from "@/features/analytics-intelligence/lib/export-utils";
import type { AnalyticsIntelligenceResponse } from "@/features/analytics-intelligence/types/analytics";
import { showSuccessToast } from "@/components/feedback/toast";

interface AnalyticsExportToolbarProps {
  data: AnalyticsIntelligenceResponse;
  dashboardRef: React.RefObject<HTMLElement | null>;
}

export function AnalyticsExportToolbar({ data, dashboardRef }: AnalyticsExportToolbarProps) {
  const handleCsv = () => {
    exportToCsv(data.export_rows, `civiclens-analytics-${Date.now()}.csv`);
    showSuccessToast("CSV exported");
  };

  const handleJson = () => {
    exportToJson(data, `civiclens-analytics-${Date.now()}.json`);
    showSuccessToast("JSON exported");
  };

  const handlePrint = () => {
    printDashboard();
  };

  const handlePng = async () => {
    if (!dashboardRef.current) return;
    await downloadElementAsPng(
      dashboardRef.current,
      `civiclens-dashboard-${Date.now()}.png`,
    );
    showSuccessToast("Dashboard image downloaded");
  };

  return (
    <div className="flex flex-wrap gap-2 print:hidden">
      <Button variant="outline" size="sm" onClick={handleCsv}>
        <Download className="h-4 w-4" />
        Export CSV
      </Button>
      <Button variant="outline" size="sm" onClick={handleJson}>
        <FileJson className="h-4 w-4" />
        Export JSON
      </Button>
      <Button variant="outline" size="sm" onClick={handlePrint}>
        <Printer className="h-4 w-4" />
        Print
      </Button>
      <Button variant="outline" size="sm" onClick={() => void handlePng()}>
        <Image className="h-4 w-4" />
        Download PNG
      </Button>
    </div>
  );
}
