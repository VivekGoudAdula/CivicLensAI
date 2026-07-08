import { Suspense, lazy } from "react";
import {
  FileSearch,
  MessageSquare,
  Settings,
  Shield,
} from "lucide-react";
import {
  createBrowserRouter,
  Navigate,
  RouterProvider,
} from "react-router-dom";

import { AppLayout } from "@/components/layout/AppLayout";
import { LoadingPage } from "@/pages/LoadingPage";
import { NotFoundPage } from "@/pages/NotFoundPage";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";

function lazyWithRetry<T extends React.ComponentType<any>>(
  importFn: () => Promise<{ default: T } | { [key: string]: any }>
): React.LazyExoticComponent<T> {
  return lazy(async () => {
    try {
      const module = await importFn();
      if ("default" in module) {
        return { default: module.default };
      }
      const keys = Object.keys(module);
      return { default: module[keys[0]] as T };
    } catch (error: any) {
      if (
        error?.message?.includes("Failed to fetch dynamically imported module") ||
        /dynamic.*import/i.test(error?.message || "")
      ) {
        const hasReloaded = sessionStorage.getItem("page_reloaded_on_chunk_fail");
        if (!hasReloaded) {
          sessionStorage.setItem("page_reloaded_on_chunk_fail", "true");
          window.location.reload();
          return new Promise(() => {});
        }
      }
      throw error;
    }
  });
}

const LandingPage = lazyWithRetry(() =>
  import("@/pages/LandingPage").then((module) => ({ default: module.LandingPage })),
);
const AdminLoginPage = lazyWithRetry(() =>
  import("@/pages/AdminLoginPage").then((module) => ({ default: module.AdminLoginPage })),
);
const SignUpPage = lazyWithRetry(() =>
  import("@/pages/SignUpPage").then((module) => ({ default: module.SignUpPage })),
);
const HomePage = lazyWithRetry(() =>
  import("@/pages/HomePage").then((module) => ({ default: module.HomePage })),
);
const CivicInsightsPage = lazy(() =>
  import("@/pages/CivicInsightsPage").then((module) => ({
    default: module.CivicInsightsPage,
  })),
);
const ClusterDetailsPage = lazy(() =>
  import("@/pages/ClusterDetailsPage").then((module) => ({
    default: module.ClusterDetailsPage,
  })),
);
const GovernancePage = lazy(() =>
  import("@/pages/GovernancePage").then((module) => ({
    default: module.GovernancePage,
  })),
);
const FeaturePage = lazy(() =>
  import("@/pages/FeaturePage").then((module) => ({
    default: module.FeaturePage,
  })),
);
const DesignSystemPage = lazy(() =>
  import("@/pages/DesignSystemPage").then((module) => ({
    default: module.DesignSystemPage,
  })),
);
const SubmitComplaintPage = lazy(() =>
  import("@/pages/SubmitComplaintPage").then((module) => ({
    default: module.SubmitComplaintPage,
  })),
);
const ComplaintSubmittedPage = lazy(() =>
  import("@/pages/ComplaintSubmittedPage").then((module) => ({
    default: module.ComplaintSubmittedPage,
  })),
);
const ComplaintHistoryPage = lazy(() =>
  import("@/pages/ComplaintHistoryPage").then((module) => ({
    default: module.ComplaintHistoryPage,
  })),
);
const ComplaintDetailsPage = lazy(() =>
  import("@/pages/ComplaintDetailsPage").then((module) => ({
    default: module.ComplaintDetailsPage,
  })),
);
const DashboardLayout = lazy(() =>
  import("@/features/dashboard/layout/DashboardLayout").then((module) => ({
    default: module.DashboardLayout,
  })),
);
const DashboardHomePage = lazy(() =>
  import("@/features/dashboard/pages/DashboardHomePage").then((module) => ({
    default: module.DashboardHomePage,
  })),
);
const DashboardComplaintsPage = lazy(() =>
  import("@/features/dashboard/pages/DashboardComplaintsPage").then((module) => ({
    default: module.DashboardComplaintsPage,
  })),
);
const DashboardComplaintDetailPage = lazy(() =>
  import("@/features/dashboard/pages/DashboardComplaintDetailPage").then((module) => ({
    default: module.DashboardComplaintDetailPage,
  })),
);
const DashboardPriorityPage = lazy(() =>
  import("@/features/dashboard/pages/DashboardPriorityPage").then((module) => ({
    default: module.DashboardPriorityPage,
  })),
);
const DashboardClustersPage = lazy(() =>
  import("@/features/dashboard/pages/DashboardClustersPage").then((module) => ({
    default: module.DashboardClustersPage,
  })),
);
const DashboardAnalyticsPage = lazy(() =>
  import("@/features/dashboard/pages/DashboardAnalyticsPage").then((module) => ({
    default: module.DashboardAnalyticsPage,
  })),
);
const DashboardActivitiesPage = lazy(() =>
  import("@/features/dashboard/pages/DashboardActivitiesPage").then((module) => ({
    default: module.DashboardActivitiesPage,
  })),
);
const MapPage = lazy(() =>
  import("@/features/gis/pages/MapPage").then((module) => ({
    default: module.MapPage,
  })),
);
const AnalyticsPage = lazy(() =>
  import("@/features/analytics-intelligence/pages/AnalyticsPage").then((module) => ({
    default: module.AnalyticsPage,
  })),
);
const RecommendationCenterPage = lazy(() =>
  import("@/features/recommendations/pages/RecommendationCenterPage").then((module) => ({
    default: module.RecommendationCenterPage,
  })),
);
const SearchPage = lazy(() =>
  import("@/features/search/pages/SearchPage").then((module) => ({
    default: module.SearchPage,
  })),
);

function withSuspense(element: React.ReactNode) {
  return <Suspense fallback={<LoadingPage />}>{element}</Suspense>;
}

export const router = createBrowserRouter([
  {
    path: "/",
    element: withSuspense(<LandingPage />),
  },
  {
    path: "/admin",
    element: withSuspense(<AdminLoginPage />),
  },
  {
    path: "/signup",
    element: withSuspense(<SignUpPage />),
  },
  {
    path: "/dashboard",
    element: <ProtectedRoute><DashboardLayout /></ProtectedRoute>,
    children: [
      {
        index: true,
        element: withSuspense(<DashboardHomePage />),
      },
      {
        path: "complaints",
        element: withSuspense(<DashboardComplaintsPage />),
      },
      {
        path: "complaints/:id",
        element: withSuspense(<DashboardComplaintDetailPage />),
      },
      {
        path: "priority",
        element: withSuspense(<DashboardPriorityPage />),
      },
      {
        path: "clusters",
        element: withSuspense(<DashboardClustersPage />),
      },
      {
        path: "analytics",
        element: withSuspense(<DashboardAnalyticsPage />),
      },
      {
        path: "activities",
        element: withSuspense(<DashboardActivitiesPage />),
      },
      {
        path: "map",
        element: withSuspense(<MapPage />),
      },
      {
        path: "analytics-intelligence",
        element: withSuspense(<AnalyticsPage />),
      },
      {
        path: "recommendations",
        element: withSuspense(<RecommendationCenterPage />),
      },
      {
        path: "search",
        element: withSuspense(<SearchPage />),
      },
      {
        path: "policy-analysis",
        element: withSuspense(
          <FeaturePage
            title="Policy Analysis"
            description="Analyze civic policies and legislation with AI-assisted insights."
            icon={FileSearch}
          />,
        ),
      },
      {
        path: "civic-insights",
        element: withSuspense(<CivicInsightsPage />),
      },
      {
        path: "civic-insights/clusters/:id",
        element: withSuspense(<ClusterDetailsPage />),
      },
      {
        path: "governance",
        element: withSuspense(<GovernancePage />),
      },
      {
        path: "compliance",
        element: withSuspense(
          <FeaturePage
            title="Compliance"
            description="Monitor regulatory compliance and civic accountability."
            icon={Shield}
          />,
        ),
      },
      {
        path: "settings",
        element: withSuspense(
          <FeaturePage
            title="Settings"
            description="Configure your CivicLens AI workspace preferences."
            icon={Settings}
          />,
        ),
      },
    ],
  },
  {
    path: "/",
    element: <ProtectedRoute><AppLayout /></ProtectedRoute>,
    children: [
      {
        path: "submit",
        element: withSuspense(<HomePage />),
      },
      {
        path: "complaints/submit",
        element: withSuspense(<SubmitComplaintPage />),
      },
      {
        path: "complaints/success",
        element: withSuspense(<ComplaintSubmittedPage />),
      },
      {
        path: "complaints",
        element: withSuspense(<ComplaintHistoryPage />),
      },
      {
        path: "complaints/:id",
        element: withSuspense(<ComplaintDetailsPage />),
      },
      {
        path: "design-system",
        element: withSuspense(<DesignSystemPage />),
      },
      {
        path: "public-forum",
        element: withSuspense(
          <FeaturePage
            title="Public Forum"
            description="Engage in structured public discourse on civic matters."
            icon={MessageSquare}
          />,
        ),
      },
      {
        path: "404",
        element: <NotFoundPage />,
      },
      {
        path: "*",
        element: <Navigate to="/404" replace />,
      },
    ],
  },
]);

export function AppRouter() {
  return <RouterProvider router={router} />;
}
