import { motion } from "framer-motion";
import {
  ArrowRight,
  Clock3,
  FileText,
  History,
  MapPin,
  Mic,
  Shield,
  Sparkles,
  Upload,
} from "lucide-react";
import { Link } from "react-router-dom";

import { CategoryBadge } from "@/components/data-display/category-badge";
import { StatusChip } from "@/components/data-display/status-chip";
import { PageHeader } from "@/components/layout/PageHeader";
import { SkeletonCard } from "@/components/loading/skeleton-card";
import { PrimaryButton, SecondaryButton } from "@/components/ui/buttons";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { env } from "@/config/env";
import { useComplaints } from "@/hooks/use-complaints";
import {
  formatComplaintStatus,
  formatDateTime,
  statusToVariant,
} from "@/lib/complaint-utils";

const quickActions = [
  {
    title: "Submit Complaint",
    description: "Report a new civic issue with photo and voice evidence.",
    href: "/complaints/submit",
    icon: Upload,
  },
  {
    title: "Complaint History",
    description: "Track status and manage all your submitted grievances.",
    href: "/complaints",
    icon: History,
  },
];

const howItWorks = [
  {
    step: "01",
    title: "Describe the Issue",
    description: "Fill in details, select a category, and attach photo or voice evidence.",
  },
  {
    step: "02",
    title: "Pin the Location",
    description: "Use the interactive map to mark the exact spot of the civic problem.",
  },
  {
    step: "03",
    title: "Track Resolution",
    description: "Monitor complaint status from pending through to resolution.",
  },
];

const features = [
  {
    icon: MapPin,
    title: "GPS Location Picker",
    description: "Search, drop a pin, and auto-fill address with reverse geocoding.",
  },
  {
    icon: Upload,
    title: "Photo Evidence",
    description: "Upload compressed images stored securely with your complaint.",
  },
  {
    icon: Mic,
    title: "Voice Recording",
    description: "Record and attach voice notes directly from your browser.",
  },
  {
    icon: Shield,
    title: "Anonymous Reporting",
    description: "Submit grievances anonymously while keeping officials informed.",
  },
  {
    icon: Clock3,
    title: "Real-time Status",
    description: "Follow your complaint from pending to resolved.",
  },
  {
    icon: Sparkles,
    title: "AI-Ready Platform",
    description: "Built for Phase 5 Gemini-powered analysis and prioritization.",
  },
];

export function HomePage() {
  const { data: recentData, isLoading } = useComplaints({ page: 1, page_size: 5 });

  return (
    <div className="space-y-12">
      <section className="relative overflow-hidden rounded-2xl border bg-gradient-to-br from-primary/10 via-background to-background p-8 md:p-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45 }}
          className="relative z-10 max-w-3xl"
        >
          <p className="mb-3 text-sm font-semibold uppercase tracking-wider text-primary">
            Citizen Portal
          </p>
          <h1 className="text-4xl font-bold tracking-tight md:text-5xl">
            Report civic issues. Build a better constituency.
          </h1>
          <p className="mt-4 max-w-2xl text-lg text-muted-foreground">
            {env.appName} empowers citizens of Amethi to submit complaints with location,
            photos, and voice evidence — helping officials respond faster and smarter.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <PrimaryButton asChild size="lg">
              <Link to="/complaints/submit">
                Submit Complaint
                <ArrowRight className="h-4 w-4" />
              </Link>
            </PrimaryButton>
            <SecondaryButton asChild size="lg">
              <Link to="/complaints">View Complaint History</Link>
            </SecondaryButton>
          </div>
        </motion.div>
        <div
          className="pointer-events-none absolute -right-16 -top-16 h-64 w-64 rounded-full bg-primary/10 blur-3xl"
          aria-hidden="true"
        />
      </section>

      <section>
        <PageHeader
          title="Quick Actions"
          description="Get started with the most common citizen portal tasks."
        />
        <div className="grid gap-4 md:grid-cols-2">
          {quickActions.map((action, index) => (
            <motion.div
              key={action.title}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.08 }}
            >
              <Link to={action.href} className="block h-full">
                <Card className="h-full transition-shadow hover:shadow-md">
                  <CardHeader>
                    <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <action.icon className="h-5 w-5 text-primary" />
                    </div>
                    <CardTitle>{action.title}</CardTitle>
                    <CardDescription>{action.description}</CardDescription>
                  </CardHeader>
                </Card>
              </Link>
            </motion.div>
          ))}
        </div>
      </section>

      <section>
        <div className="mb-6 flex items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold tracking-tight">Recent Complaints</h2>
            <p className="mt-1 text-muted-foreground">
              Latest grievances submitted through the citizen portal.
            </p>
          </div>
          <SecondaryButton asChild>
            <Link to="/complaints">View All</Link>
          </SecondaryButton>
        </div>

        {isLoading ? (
          <div className="grid gap-4">
            <SkeletonCard />
            <SkeletonCard />
          </div>
        ) : null}

        {!isLoading && recentData?.items.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center py-12 text-center">
              <FileText className="mb-4 h-10 w-10 text-muted-foreground" />
              <p className="font-medium">No complaints yet</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Be the first to report a civic issue in your area.
              </p>
              <PrimaryButton asChild className="mt-4">
                <Link to="/complaints/submit">Submit First Complaint</Link>
              </PrimaryButton>
            </CardContent>
          </Card>
        ) : null}

        {!isLoading && recentData && recentData.items.length > 0 ? (
          <div className="grid gap-4">
            {recentData.items.map((complaint) => (
              <Link key={complaint.id} to={`/complaints/${complaint.id}`}>
                <Card className="transition-shadow hover:shadow-md">
                  <CardContent className="flex flex-col gap-3 p-5 sm:flex-row sm:items-center sm:justify-between">
                    <div className="min-w-0 flex-1">
                      <p className="truncate font-semibold">{complaint.title}</p>
                      <p className="mt-1 line-clamp-1 text-sm text-muted-foreground">
                        {complaint.description}
                      </p>
                      <p className="mt-2 text-xs text-muted-foreground">
                        {formatDateTime(complaint.submitted_at)}
                      </p>
                    </div>
                    <div className="flex flex-wrap items-center gap-2">
                      <CategoryBadge category={complaint.category_name} />
                      <StatusChip
                        label={formatComplaintStatus(complaint.status)}
                        variant={statusToVariant(complaint.status)}
                      />
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        ) : null}
      </section>

      <section>
        <PageHeader
          title="How It Works"
          description="Three simple steps to report and track civic issues."
        />
        <div className="grid gap-4 md:grid-cols-3">
          {howItWorks.map((item) => (
            <Card key={item.step}>
              <CardHeader>
                <p className="text-sm font-bold text-primary">{item.step}</p>
                <CardTitle className="text-lg">{item.title}</CardTitle>
                <CardDescription>{item.description}</CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      </section>

      <section>
        <PageHeader
          title="Platform Features"
          description="Everything you need for effective civic grievance reporting."
        />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <Card key={feature.title}>
              <CardHeader>
                <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <feature.icon className="h-5 w-5 text-primary" />
                </div>
                <CardTitle className="text-base">{feature.title}</CardTitle>
                <CardDescription>{feature.description}</CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      </section>

      <footer className="rounded-xl border bg-muted/30 px-6 py-8">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="font-semibold">{env.appName}</p>
            <p className="mt-1 text-sm text-muted-foreground">
              Civic intelligence for Amethi constituency · v{env.appVersion}
            </p>
          </div>
          <div className="flex flex-wrap gap-4 text-sm">
            <Link to="/complaints/submit" className="text-primary hover:underline">
              Submit Complaint
            </Link>
            <Link to="/complaints" className="text-primary hover:underline">
              Complaint History
            </Link>
            <Link to="/design-system" className="text-muted-foreground hover:underline">
              Design System
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
