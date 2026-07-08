import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  BarChart3,
  FileText,
  Info,
  Sparkles,
  Users,
} from "lucide-react";

import { AIInsightCard } from "@/components/data-display/ai-insight-card";
import { AIConfidenceBadge } from "@/components/data-display/ai-confidence-badge";
import { CategoryBadge } from "@/components/data-display/category-badge";
import { DataTable } from "@/components/data-display/data-table";
import { DepartmentBadge } from "@/components/data-display/department-badge";
import { InformationCard } from "@/components/data-display/information-card";
import { PriorityBadge } from "@/components/data-display/priority-badge";
import { PriorityCard } from "@/components/data-display/priority-card";
import { SeverityBadge } from "@/components/data-display/severity-badge";
import { StatisticCard } from "@/components/data-display/statistic-card";
import { StatusChip } from "@/components/data-display/status-chip";
import { ErrorState } from "@/components/empty-states/error-state";
import { NoAnalyticsEmptyState } from "@/components/empty-states/no-analytics";
import { NoComplaintsEmptyState } from "@/components/empty-states/no-complaints";
import { NoInternetEmptyState } from "@/components/empty-states/no-internet";
import { NoRecommendationsEmptyState } from "@/components/empty-states/no-recommendations";
import { NoSearchResultsEmptyState } from "@/components/empty-states/no-search-results";
import { ConfirmationModal } from "@/components/feedback/confirmation-modal";
import { Drawer } from "@/components/feedback/drawer";
import { ProgressLoader } from "@/components/feedback/progress-loader";
import { Spinner } from "@/components/feedback/spinner";
import {
  showErrorToast,
  showInfoToast,
  showSuccessToast,
  showWarningToast,
} from "@/components/feedback/toast";
import { AreaChartWrapper } from "@/components/charts/area-chart";
import { BarChartWrapper } from "@/components/charts/bar-chart";
import { KPICard } from "@/components/charts/kpi-card";
import { LineChartWrapper } from "@/components/charts/line-chart";
import { PieChartWrapper } from "@/components/charts/pie-chart";
import { DashboardGrid } from "@/components/layout/DashboardGrid";
import { PageHeader } from "@/components/layout/PageHeader";
import { SectionContainer } from "@/components/layout/SectionContainer";
import { FullPageLoader } from "@/components/loading/full-page-loader";
import { SkeletonCards } from "@/components/loading/skeleton-card";
import { SkeletonForm } from "@/components/loading/skeleton-form";
import { SkeletonTable } from "@/components/loading/skeleton-table";
import { MapContainer } from "@/components/maps/map-container";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DangerButton,
  GhostButton,
  LoadingButton,
  PrimaryButton,
  SecondaryButton,
} from "@/components/ui/buttons";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { MultiSelect } from "@/components/ui/multi-select";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { SearchBox } from "@/components/ui/search-box";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { typography } from "@/design-system/tokens";

const formSchema = z.object({
  title: z.string().min(3),
  category: z.string().min(1),
});

type FormValues = z.infer<typeof formSchema>;

const tableData = [
  { village: "Jagdishpur", complaints: 12, status: "Active", priority: "high" },
  { village: "Bhadar", complaints: 8, status: "Active", priority: "medium" },
  { village: "Semari", complaints: 15, status: "Critical", priority: "critical" },
  { village: "Musafirkhana", complaints: 6, status: "Resolved", priority: "low" },
  { village: "Singhpur", complaints: 9, status: "Active", priority: "high" },
  { village: "Tiloi", complaints: 4, status: "Pending", priority: "medium" },
];

const barData = [
  { name: "Roads", value: 24 },
  { name: "Water", value: 18 },
  { name: "Health", value: 12 },
  { name: "Education", value: 9 },
];

const pieData = [
  { name: "Submitted", value: 35 },
  { name: "Clustered", value: 28 },
  { name: "In Progress", value: 22 },
  { name: "Resolved", value: 15 },
];

const lineData = [
  { name: "Jan", value: 12 },
  { name: "Feb", value: 19 },
  { name: "Mar", value: 15 },
  { name: "Apr", value: 22 },
  { name: "May", value: 28 },
  { name: "Jun", value: 24 },
];

const areaData = [
  { name: "W1", value: 8 },
  { name: "W2", value: 12 },
  { name: "W3", value: 10 },
  { name: "W4", value: 18 },
  { name: "W5", value: 15 },
];

const mapMarkers = [
  { id: "1", x: 30, y: 40, label: "Jagdishpur" },
  { id: "2", x: 55, y: 35, label: "Bhadar" },
  { id: "3", x: 45, y: 60, label: "Semari" },
  { id: "4", x: 70, y: 50, label: "Musafirkhana" },
];

const multiOptions = [
  { value: "roads", label: "Roads" },
  { value: "water", label: "Water" },
  { value: "health", label: "Health" },
  { value: "education", label: "Education" },
];

export function DesignSystemPage() {
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [multiValue, setMultiValue] = useState<string[]>(["roads"]);
  const [showFullLoader, setShowFullLoader] = useState(false);
  const [progress, setProgress] = useState(65);

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { title: "", category: "" },
  });

  return (
    <div className="space-y-10 pb-16">
      <PageHeader
        title="Design System"
        description="CivicLens AI component library — tokens, layouts, data display, feedback, charts, and maps."
        breadcrumbs={[
          { label: "Home", href: "/" },
          { label: "Design System" },
        ]}
        actions={
          <Badge variant="info" className="gap-1">
            <Sparkles className="h-3 w-3" />
            Phase 3
          </Badge>
        }
      />

      <Tabs defaultValue="tokens" className="space-y-6">
        <TabsList className="flex h-auto flex-wrap gap-1">
          <TabsTrigger value="tokens">Tokens</TabsTrigger>
          <TabsTrigger value="buttons">Buttons</TabsTrigger>
          <TabsTrigger value="cards">Cards</TabsTrigger>
          <TabsTrigger value="forms">Forms</TabsTrigger>
          <TabsTrigger value="badges">Badges</TabsTrigger>
          <TabsTrigger value="data">Data</TabsTrigger>
          <TabsTrigger value="feedback">Feedback</TabsTrigger>
          <TabsTrigger value="loading">Loading</TabsTrigger>
          <TabsTrigger value="empty">Empty States</TabsTrigger>
          <TabsTrigger value="charts">Charts</TabsTrigger>
          <TabsTrigger value="maps">Maps</TabsTrigger>
        </TabsList>

        <TabsContent value="tokens" className="space-y-8">
          <SectionContainer title="Typography" description="Inter font family with semantic scale">
            <div className="space-y-4 rounded-xl border p-6">
              <p style={{ fontSize: typography.fontSize["4xl"], fontWeight: typography.fontWeight.bold }}>Heading 1 — 4xl Bold</p>
              <p style={{ fontSize: typography.fontSize["2xl"], fontWeight: typography.fontWeight.semibold }}>Heading 2 — 2xl Semibold</p>
              <p style={{ fontSize: typography.fontSize.lg, fontWeight: typography.fontWeight.medium }}>Heading 3 — lg Medium</p>
              <p style={{ fontSize: typography.fontSize.base }}>Body — base Regular</p>
              <p style={{ fontSize: typography.fontSize.sm }} className="text-muted-foreground">Caption — sm Muted</p>
              <p className="font-mono text-sm">Mono — JetBrains Mono for code</p>
            </div>
          </SectionContainer>

          <SectionContainer title="Colors" description="Semantic color tokens">
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
              {["primary", "secondary", "success", "warning", "info", "destructive"].map((color) => (
                <div key={color} className="space-y-2">
                  <div className={`h-16 rounded-lg bg-${color} border`} style={{ backgroundColor: `hsl(var(--${color}))` }} />
                  <p className="text-xs font-medium capitalize">{color}</p>
                </div>
              ))}
            </div>
          </SectionContainer>

          <SectionContainer title="Spacing & Radius">
            <div className="flex flex-wrap gap-4">
              {["sm", "md", "lg", "xl", "2xl"].map((r) => (
                <div key={r} className={`h-16 w-16 border bg-muted rounded-${r}`} />
              ))}
            </div>
          </SectionContainer>
        </TabsContent>

        <TabsContent value="buttons">
          <SectionContainer title="Button Variants">
            <div className="flex flex-wrap gap-3">
              <PrimaryButton>Primary</PrimaryButton>
              <SecondaryButton>Secondary</SecondaryButton>
              <GhostButton>Ghost</GhostButton>
              <DangerButton>Danger</DangerButton>
              <Button size="icon" variant="outline" aria-label="Icon button">
                <Sparkles className="h-4 w-4" />
              </Button>
              <LoadingButton loading>Loading</LoadingButton>
            </div>
          </SectionContainer>
        </TabsContent>

        <TabsContent value="cards" className="space-y-8">
          <DashboardGrid columns={3}>
            <StatisticCard title="Total Complaints" value="142" description="Amethi constituency" icon={FileText} trend={{ value: "+12% this month", positive: false }} />
            <AIInsightCard title="Road Infrastructure Cluster" summary="AI detected systemic road damage across 4 villages requiring PWD intervention." confidence={0.89} themes={["roads", "infrastructure", "rural"]} />
            <PriorityCard title="Water Crisis" description="Critical water supply issues in Semari and Musafirkhana blocks." priority="critical" count={8} />
          </DashboardGrid>
          <InformationCard title="Constituency Info" content="Amethi parliamentary constituency spans 6 major villages with active civic monitoring." icon={Info} footer="Updated daily" />
        </TabsContent>

        <TabsContent value="forms" className="space-y-8">
          <SectionContainer title="Form Controls">
            <form className="grid max-w-lg gap-4" onSubmit={form.handleSubmit(() => showSuccessToast("Form submitted"))}>
              <div className="space-y-2">
                <Label htmlFor="title">Complaint Title</Label>
                <Input id="title" placeholder="Enter title..." {...form.register("title")} />
              </div>
              <div className="space-y-2">
                <Label>Category</Label>
                <Select onValueChange={(v) => form.setValue("category", v)}>
                  <SelectTrigger><SelectValue placeholder="Select category" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="roads">Roads</SelectItem>
                    <SelectItem value="water">Water</SelectItem>
                    <SelectItem value="health">Health</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea id="description" placeholder="Describe the issue..." />
              </div>
              <SearchBox placeholder="Search villages..." className="max-w-full" />
              <div className="space-y-2">
                <Label>Categories (Multi Select)</Label>
                <MultiSelect options={multiOptions} value={multiValue} onChange={setMultiValue} />
              </div>
              <div className="flex items-center gap-2">
                <Checkbox id="urgent" />
                <Label htmlFor="urgent">Mark as urgent</Label>
              </div>
              <div className="flex items-center gap-2">
                <Switch id="notify" />
                <Label htmlFor="notify">Notify department</Label>
              </div>
              <RadioGroup defaultValue="public">
                <div className="flex items-center gap-2">
                  <RadioGroupItem value="public" id="public" />
                  <Label htmlFor="public">Public</Label>
                </div>
                <div className="flex items-center gap-2">
                  <RadioGroupItem value="private" id="private" />
                  <Label htmlFor="private">Private</Label>
                </div>
              </RadioGroup>
              <PrimaryButton type="submit">Submit Complaint</PrimaryButton>
            </form>
          </SectionContainer>
        </TabsContent>

        <TabsContent value="badges">
          <SectionContainer title="Status & Badges">
            <div className="flex flex-wrap gap-3">
              <StatusChip label="Resolved" variant="success" />
              <StatusChip label="Pending" variant="warning" />
              <StatusChip label="Rejected" variant="error" />
              <StatusChip label="Under Review" variant="info" />
              <StatusChip label="Draft" variant="neutral" />
              <PriorityBadge priority="critical" />
              <PriorityBadge priority="high" />
              <CategoryBadge category="roads" />
              <AIConfidenceBadge score={0.92} />
              <DepartmentBadge name="Public Works" code="PWD" />
              <SeverityBadge severity="high" />
            </div>
          </SectionContainer>
        </TabsContent>

        <TabsContent value="data">
          <SectionContainer title="Data Table" description="Sortable, searchable, paginated">
            <DataTable
              data={tableData}
              columns={[
                { key: "village", header: "Village" },
                { key: "complaints", header: "Complaints" },
                { key: "status", header: "Status", render: (row) => <StatusChip label={row.status as string} variant={row.status === "Resolved" ? "success" : row.status === "Critical" ? "error" : "info"} /> },
                { key: "priority", header: "Priority", render: (row) => <PriorityBadge priority={row.priority as "low" | "medium" | "high" | "critical"} /> },
              ]}
            />
          </SectionContainer>
        </TabsContent>

        <TabsContent value="feedback" className="space-y-8">
          <SectionContainer title="Toasts">
            <div className="flex flex-wrap gap-3">
              <SecondaryButton onClick={() => showSuccessToast("Success", "Operation completed")}>Success Toast</SecondaryButton>
              <SecondaryButton onClick={() => showErrorToast("Error", "Something failed")}>Error Toast</SecondaryButton>
              <SecondaryButton onClick={() => showWarningToast("Warning", "Please review")}>Warning Toast</SecondaryButton>
              <SecondaryButton onClick={() => showInfoToast("Info", "New update available")}>Info Toast</SecondaryButton>
            </div>
          </SectionContainer>
          <SectionContainer title="Dialogs & Drawers">
            <div className="flex flex-wrap gap-3">
              <Dialog>
                <DialogTrigger asChild><SecondaryButton>Open Dialog</SecondaryButton></DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Sample Dialog</DialogTitle>
                    <DialogDescription>Modal dialog with animated entrance.</DialogDescription>
                  </DialogHeader>
                </DialogContent>
              </Dialog>
              <SecondaryButton onClick={() => setConfirmOpen(true)}>Confirmation Modal</SecondaryButton>
              <SecondaryButton onClick={() => setDrawerOpen(true)}>Open Drawer</SecondaryButton>
            </div>
          </SectionContainer>
          <ConfirmationModal open={confirmOpen} onOpenChange={setConfirmOpen} title="Delete complaint?" description="This action cannot be undone." onConfirm={() => { setConfirmOpen(false); showSuccessToast("Deleted"); }} />
          <Drawer open={drawerOpen} onOpenChange={setDrawerOpen} title="Complaint Details" description="Side drawer panel">
            <p className="text-sm text-muted-foreground">Drawer content for detail views.</p>
          </Drawer>
        </TabsContent>

        <TabsContent value="loading" className="space-y-8">
          <SectionContainer title="Spinners & Progress">
            <div className="flex items-center gap-8">
              <Spinner size="sm" />
              <Spinner size="md" />
              <Spinner size="lg" />
              <div className="w-48"><ProgressLoader value={progress} label="Processing" /></div>
              <SecondaryButton onClick={() => setProgress((p) => (p >= 100 ? 0 : p + 10))}>Increment</SecondaryButton>
            </div>
          </SectionContainer>
          <SectionContainer title="Skeletons">
            <div className="space-y-8">
              <SkeletonCards count={3} />
              <SkeletonTable />
              <SkeletonForm />
            </div>
          </SectionContainer>
          <SecondaryButton onClick={() => { setShowFullLoader(true); setTimeout(() => setShowFullLoader(false), 2000); }}>
            Show Full Page Loader (2s)
          </SecondaryButton>
          {showFullLoader ? <FullPageLoader /> : null}
        </TabsContent>

        <TabsContent value="empty" className="space-y-8">
          <NoComplaintsEmptyState />
          <NoRecommendationsEmptyState />
          <NoAnalyticsEmptyState />
          <NoSearchResultsEmptyState query="water supply" />
          <NoInternetEmptyState onRetry={() => showInfoToast("Retrying connection...")} />
          <ErrorState onRetry={() => showInfoToast("Retrying...")} />
        </TabsContent>

        <TabsContent value="charts" className="space-y-8">
          <DashboardGrid columns={4}>
            <KPICard label="Complaints" value="142" change={12} icon={FileText} />
            <KPICard label="Clusters" value="18" change={-3} icon={BarChart3} />
            <KPICard label="Recommendations" value="24" change={8} icon={Sparkles} />
            <KPICard label="Citizens" value="3.2K" change={5} icon={Users} />
          </DashboardGrid>
          <div className="grid gap-6 lg:grid-cols-2">
            <BarChartWrapper data={barData} title="Complaints by Category" />
            <PieChartWrapper data={pieData} title="Status Distribution" />
            <LineChartWrapper data={lineData} title="Monthly Trend" />
            <AreaChartWrapper data={areaData} title="Weekly Activity" />
          </div>
        </TabsContent>

        <TabsContent value="maps">
          <SectionContainer title="Map Container" description="Reusable map architecture with markers, heatmap layer, controls, and legend">
            <MapContainer
              markers={mapMarkers}
              heatmapPoints={[
                { x: 45, y: 45, intensity: 0.8 },
                { x: 60, y: 40, intensity: 0.5 },
              ]}
              legendItems={[
                { color: "hsl(var(--primary))", label: "Village" },
                { color: "hsl(var(--destructive))", label: "High complaint density" },
              ]}
              onZoomIn={() => showInfoToast("Zoom in")}
              onZoomOut={() => showInfoToast("Zoom out")}
              onReset={() => showInfoToast("Reset view")}
            />
          </SectionContainer>
          <SectionContainer title="Map Loading State">
            <MapContainer loading />
          </SectionContainer>
        </TabsContent>
      </Tabs>
    </div>
  );
}
