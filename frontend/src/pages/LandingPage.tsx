import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowRight, Landmark, Sparkles, Send, Activity, ShieldAlert, Cpu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { env } from "@/config/env";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { y: 30, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] },
  },
};

export function LandingPage() {
  return (
    <div className="relative min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between overflow-hidden">
      {/* Background Decorative Blobs */}
      <div className="absolute inset-0 z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-blue-500/10 blur-[120px] animate-pulse" style={{ animationDuration: "8s" }} />
        <div className="absolute bottom-[20%] right-[-10%] w-[60%] h-[60%] rounded-full bg-violet-600/10 blur-[140px] animate-pulse" style={{ animationDuration: "12s" }} />
        {/* Fine subtle Grid Overlay */}
        <div 
          className="absolute inset-0 opacity-[0.03]" 
          style={{ 
            backgroundImage: "radial-gradient(#ffffff 1px, transparent 1px)", 
            backgroundSize: "24px 24px" 
          }} 
        />
      </div>

      {/* Top Navbar */}
      <header className="relative z-10 border-b border-slate-800/60 bg-slate-950/70 backdrop-blur-md sticky top-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-md shadow-blue-500/20">
              <Landmark className="h-5.5 w-5.5" />
            </div>
            <div>
              <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-blue-400 via-indigo-200 to-white bg-clip-text text-transparent">
                {env.appName}
              </span>
            </div>
          </div>
          <div>
            <Button asChild variant="outline" className="border-slate-800 bg-slate-900/40 hover:bg-slate-800 text-slate-200 hover:text-white transition-all duration-300">
              <Link to="/admin">Admin Login</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 flex-1 flex flex-col justify-center items-center px-4 py-20 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
        <motion.div 
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="flex flex-col items-center text-center w-full"
        >
          {/* Hero Section */}
          <motion.div variants={itemVariants} className="mb-6">
            <span className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full border border-blue-500/30 bg-blue-500/10 text-blue-400 text-xs font-semibold uppercase tracking-wider shadow-inner shadow-blue-500/5">
              <Sparkles className="h-3.5 w-3.5 animate-pulse text-blue-400" />
              AI-Powered Civic Intelligence
            </span>
          </motion.div>

          <motion.h1 
            variants={itemVariants} 
            className="text-5xl font-black tracking-tight sm:text-7xl lg:text-8xl bg-gradient-to-b from-white via-slate-100 to-slate-500 bg-clip-text text-transparent drop-shadow-xl"
          >
            CivicLens AI
          </motion.h1>

          <motion.p 
            variants={itemVariants} 
            className="mt-6 text-lg sm:text-xl text-slate-400 leading-relaxed max-w-3xl"
          >
            Empelling community engagement and regional leadership. Report issues in real-time, get automatic AI urgency prioritizing, and observe active local resolution pipelines.
          </motion.p>

          <motion.div variants={itemVariants} className="mt-10 flex flex-wrap gap-4 justify-center">
            <Button asChild size="lg" className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold shadow-lg shadow-blue-500/25 hover:shadow-blue-500/45 transform hover:-translate-y-0.5 transition-all duration-300 px-8 py-6 rounded-xl">
              <Link to="/submit" className="flex items-center gap-2">
                Submit Complaint
                <ArrowRight className="h-5 w-5" />
              </Link>
            </Button>
          </motion.div>

          {/* Feature Grid */}
          <motion.div 
            variants={itemVariants} 
            className="mt-24 grid gap-8 md:grid-cols-3 w-full"
          >
            {/* Card 1 */}
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-indigo-500/10 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              <div className="relative h-full border border-slate-800/80 bg-slate-900/35 backdrop-blur-sm p-8 rounded-2xl shadow-xl hover:border-slate-700/80 transition-all duration-300 transform group-hover:-translate-y-1.5 flex flex-col items-start text-left">
                <div className="h-12 w-12 rounded-xl bg-blue-500/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <Send className="h-6 w-6 text-blue-400" />
                </div>
                <h3 className="text-xl font-bold text-slate-100 mb-3 group-hover:text-blue-400 transition-colors duration-300">Submit Complaint</h3>
                <p className="text-slate-400 text-sm leading-relaxed">
                  Pinpoint community issues with GPS location precision. Add high-quality photos, videos, and descriptive audio notes instantly.
                </p>
              </div>
            </div>

            {/* Card 2 */}
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-violet-500/10 to-purple-500/10 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              <div className="relative h-full border border-slate-800/80 bg-slate-900/35 backdrop-blur-sm p-8 rounded-2xl shadow-xl hover:border-slate-700/80 transition-all duration-300 transform group-hover:-translate-y-1.5 flex flex-col items-start text-left">
                <div className="h-12 w-12 rounded-xl bg-violet-500/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <Cpu className="h-6 w-6 text-violet-400" />
                </div>
                <h3 className="text-xl font-bold text-slate-100 mb-3 group-hover:text-violet-400 transition-colors duration-300">AI Priority & Categorization</h3>
                <p className="text-slate-400 text-sm leading-relaxed">
                  Fast Gemini pipeline models automatically categorize issues, detect duplicate incidents, and rank severity score in real-time.
                </p>
              </div>
            </div>

            {/* Card 3 */}
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/10 to-teal-500/10 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              <div className="relative h-full border border-slate-800/80 bg-slate-900/35 backdrop-blur-sm p-8 rounded-2xl shadow-xl hover:border-slate-700/80 transition-all duration-300 transform group-hover:-translate-y-1.5 flex flex-col items-start text-left">
                <div className="h-12 w-12 rounded-xl bg-emerald-500/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <Activity className="h-6 w-6 text-emerald-400" />
                </div>
                <h3 className="text-xl font-bold text-slate-100 mb-3 group-hover:text-emerald-400 transition-colors duration-300">Live Dashboard & Action</h3>
                <p className="text-slate-400 text-sm leading-relaxed">
                  Track governance actions and resolution metrics. Watch as public departments get assigned tasks, and map real-time progress.
                </p>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-slate-900 py-8 bg-slate-950/60 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-slate-500">
          <p>© 2026 {env.appName}. All rights reserved.</p>
          <div className="flex gap-6">
            <Link to="/submit" className="hover:text-slate-300 transition-colors duration-200">Citizen Portal</Link>
            <Link to="/admin" className="hover:text-slate-300 transition-colors duration-200">Admin Center</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
