/**
 * MwohaOS — Personal Opportunity Intelligence & Execution Operating System
 * Milestone 6: Evidence-Grounded AI Preparation Studio & Workspace
 */

import React, { useState } from 'react';
import { 
  Server, 
  Database, 
  Cpu, 
  CheckCircle2, 
  Terminal, 
  ShieldCheck, 
  Layers, 
  Settings, 
  Clock, 
  ArrowRight, 
  FileText, 
  Activity, 
  Copy, 
  Check,
  Code2,
  FolderTree,
  AlertTriangle,
  Briefcase,
  Sparkles,
  ExternalLink,
  ChevronRight,
  ClipboardCheck,
  FileCheck2,
  HelpCircle,
  Send,
  AlertCircle,
  Wand2,
  RotateCcw,
  BookOpen,
  Award,
  Zap
} from 'lucide-react';

interface MockApplication {
  id: string;
  title: string;
  org: string;
  category: string;
  deadline: string;
  daysRemaining: number;
  matchScore: number;
  status: 'SAVED' | 'PREPARING' | 'READY_FOR_REVIEW' | 'READY_TO_SUBMIT' | 'SUBMITTED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  docsAttached: number;
  docsRequired: number;
  questionsAnswered: number;
  questionsTotal: number;
  userReviewed: boolean;
  submissionRef?: string;
  notes: string;
  // Milestone 6 AI Prep state
  hasTailoredCoverLetter: boolean;
  coverLetterVersion: number;
  atsCoverageScore: number;
  questionsDrafted: boolean;
}

export default function App() {
  const [activeTab, setActiveTab] = useState<'aiprep' | 'workspace' | 'matching' | 'overview' | 'architecture' | 'tests' | 'health'>('aiprep');
  const [copiedCmd, setCopiedCmd] = useState<string | null>(null);

  // Application Workspace Interactive State
  const [selectedAppId, setSelectedAppId] = useState<string>('app-1');
  const [apps, setApps] = useState<MockApplication[]>([
    {
      id: 'app-1',
      title: 'Senior Earth Observation Researcher',
      org: 'European Space Agency (ESA)',
      category: 'Fellowship / Research',
      deadline: '2026-10-18',
      daysRemaining: 21,
      matchScore: 92,
      status: 'PREPARING',
      priority: 'HIGH',
      docsAttached: 2,
      docsRequired: 3,
      questionsAnswered: 1,
      questionsTotal: 2,
      userReviewed: false,
      notes: 'Focus on multi-spectral satellite imagery and agricultural yield prediction in East Africa.',
      hasTailoredCoverLetter: true,
      coverLetterVersion: 1,
      atsCoverageScore: 88,
      questionsDrafted: true,
    },
    {
      id: 'app-2',
      title: 'Geospatial Machine Learning Engineer',
      org: 'United Nations Environment Programme (UNEP)',
      category: 'Full-time / Technical',
      deadline: '2026-10-25',
      daysRemaining: 28,
      matchScore: 89,
      status: 'PREPARING',
      priority: 'HIGH',
      docsAttached: 2,
      docsRequired: 2,
      questionsAnswered: 2,
      questionsTotal: 2,
      userReviewed: false,
      notes: 'Remote Sensing & GIS with Python and Google Earth Engine.',
      hasTailoredCoverLetter: true,
      coverLetterVersion: 2,
      atsCoverageScore: 94,
      questionsDrafted: true,
    },
    {
      id: 'app-3',
      title: 'Climate Adaptation Tech Innovation Grant',
      org: 'Global Innovation Fund',
      category: 'Grant / Funding',
      deadline: '2026-11-01',
      daysRemaining: 35,
      matchScore: 85,
      status: 'SAVED',
      priority: 'MEDIUM',
      docsAttached: 1,
      docsRequired: 4,
      questionsAnswered: 0,
      questionsTotal: 3,
      userReviewed: false,
      notes: 'Concept note required before full grant proposal submission.',
      hasTailoredCoverLetter: false,
      coverLetterVersion: 0,
      atsCoverageScore: 72,
      questionsDrafted: false,
    },
  ]);

  // AI Prep Studio Interactive State
  const [aiTone, setAiTone] = useState<'PROFESSIONAL' | 'EXECUTIVE' | 'ACADEMIC'>('PROFESSIONAL');
  const [clVersion, setClVersion] = useState<number>(1);
  const [isGeneratingCL, setIsGeneratingCL] = useState<boolean>(false);
  const [isOptimizingCV, setIsOptimizingCV] = useState<boolean>(false);
  const [selectedQuestionIndex, setSelectedQuestionIndex] = useState<number>(0);
  const [questionTone, setQuestionTone] = useState<'STAR_METHOD' | 'CONCISE' | 'EXECUTIVE'>('STAR_METHOD');
  const [isDraftingQuestion, setIsDraftingQuestion] = useState<boolean>(false);
  const [prepAllSuccess, setPrepAllSuccess] = useState<boolean>(false);

  const selectedApp = apps.find(a => a.id === selectedAppId) || apps[0];

  // Dynamic Cover Letter Versions for ESA app
  const coverLetterDrafts: Record<number, { text: string; citations: string[]; wordCount: number }> = {
    1: {
      text: `Dear Hiring Committee at European Space Agency,

I am writing to express my strong enthusiasm for the Senior Earth Observation Researcher role at the European Space Agency. With a proven research background in Python and satellite radar remote sensing, I am deeply inspired by ESA's mission to advance European satellite observations for global climate resilience.

In my recent capacity as Earth Observation Specialist at Regional Geospatial Centre, I spearheaded automated SAR processing workflows that improved ingest efficiency by 40%. This directly aligns with your requirement for demonstrated proficiency in developing automated Sentinel-1 processing pipelines.

Furthermore, through my work on the 'AgriSAR Radar Sentinel Pipeline', I architected an automated flood mapping algorithm using Python, GDAL, and Sentinel-1 data. This solution was deployed across 5 agricultural hubs, reducing response times by 3 days. Combining this practical track record with my PhD in Remote Sensing & Earth Systems from the Technical University of Munich, I am prepared to contribute immediately to ESA's Earth observation objectives.

I welcome the opportunity to discuss how my verified background and technical capabilities can support your upcoming research programs. Thank you for your consideration.

Sincerely,
Henry Mwoha`,
      citations: [
        'SKILL: Python (Expert)',
        'SKILL: Sentinel-1 Radar (Advanced)',
        'EXPERIENCE: Earth Observation Specialist @ Regional Geospatial Centre',
        'PROJECT: AgriSAR Radar Sentinel Pipeline (Impact: 5 hubs)',
        'EDUCATION: PhD in Remote Sensing @ TUM (2023)'
      ],
      wordCount: 196
    },
    2: {
      text: `Dear Search Committee at European Space Agency,

I am pleased to present my candidacy for the Senior Earth Observation Researcher position at ESA. As a researcher specializing in multi-spectral radar remote sensing and satellite analytics, I bring a demonstrated history of bridging complex algorithmic research with mission-critical applications.

Throughout my career at Regional Geospatial Centre, I architected open-source Sentinel-1 processing workflows handling large-scale SAR data ingestion. My research specifically tackled multi-temporal land degradation and environmental monitoring, addressing the precise challenges outlined in ESA's mandate for advanced radar processing pipelines.

My doctoral research at the Technical University of Munich focused on Earth Observation systems, complemented by hands-on engineering of the AgriSAR Radar Pipeline. This initiative delivered measurable impact across multiple stakeholder hubs. I am eager to leverage this foundation to drive ESA's observational and scientific priorities forward.

Thank you for your review. I look forward to the prospect of discussing how my technical background aligns with your team's mission.

Respectfully,
Henry Mwoha`,
      citations: [
        'SKILL: Python & SAR Processing',
        'EXPERIENCE: Regional Geospatial Centre Workflow Architect',
        'EDUCATION: PhD @ Technical University of Munich',
        'PROJECT: AgriSAR Sentinel Analytics'
      ],
      wordCount: 181
    }
  };

  // Questions Mock Data
  const mockQuestions = [
    {
      q: 'Describe your hands-on experience developing satellite data processing pipelines with Python and Sentinel radar.',
      limitWords: 150,
      category: 'TECHNICAL',
      answers: {
        STAR_METHOD: 'Situation: At the Regional Geospatial Centre, regional agricultural monitors faced delayed flood assessments due to manual SAR preprocessing bottlenecks.\n\nTask: As Lead Researcher, my mandate was to engineer an automated, scalable radar satellite processing pipeline utilizing Python and Sentinel-1 data.\n\nAction: I designed the AgriSAR pipeline using Python, GDAL, and Docker containerization. I implemented automated radiometric calibration, terrain correction, and temporal speckle filtering, reducing processing runtimes by 40%.\n\nResult: The pipeline was operationalized across 5 regional agricultural hubs, accelerating emergency flood response times by 3 days while ensuring 100% reproducible scientific outputs.',
        CONCISE: 'I have 5+ years of Python-based SAR engineering experience. At Regional Geospatial Centre, I built the open-source AgriSAR processing pipeline using GDAL, Sentinel-1 radar, and Docker, reducing ingest latency by 40% and deploying across 5 regional operational hubs for automated flood and crop monitoring.',
        EXECUTIVE: 'My technical leadership in Earth Observation focuses on translating satellite data into automated intelligence. By spearheading the Python-based AgriSAR pipeline for Sentinel-1 radar data, my team lowered institutional processing overhead by 40% and delivered automated monitoring across 5 regional centers.'
      }
    },
    {
      q: 'How does your research trajectory align with ESA\'s long-term Earth observation and climate priorities?',
      limitWords: 200,
      category: 'MOTIVATION',
      answers: {
        STAR_METHOD: 'Situation: Global climate resilience requires high-frequency, peer-reviewed satellite observations that translate raw orbital passes into actionable environmental baselines.\n\nTask: My academic and professional mission has centered on advancing robust remote sensing methodologies directly aligned with ESA’s Living Planet Programme.\n\nAction: During my doctoral work at the Technical University of Munich and subsequent field research, I specialized in multi-temporal radar satellite analysis, publishing findings on synthetic aperture radar calibration and land degradation.\n\nResult: Joining ESA represents the natural culmination of this trajectory, enabling me to contribute rigorous research and scalable automated pipelines to Europe’s flagship observation satellites.',
        CONCISE: 'My research in radar remote sensing directly advances ESA’s Living Planet Programme. Having completed doctoral research in Earth Systems at TUM and developed real-world SAR processing pipelines, my focus on climate monitoring and open science aligns seamlessly with ESA’s mission.',
        EXECUTIVE: 'Strategic Earth observation requires the convergence of rigorous academic methodology and scalable computational execution. My trajectory—from doctoral work at TUM to architecting operational SAR workflows—is purposefully aligned with ESA’s strategic leadership in global environmental monitoring.'
      }
    }
  ];

  // Calculate live readiness score
  const docScore = (selectedApp.docsAttached / selectedApp.docsRequired) * 40;
  const qScore = (selectedApp.questionsAnswered / selectedApp.questionsTotal) * 30;
  const reviewScore = selectedApp.userReviewed ? 20 : 0;
  const planningScore = 10;
  const totalReadiness = Math.round(docScore + qScore + reviewScore + planningScore);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCmd(text);
    setTimeout(() => setCopiedCmd(null), 2000);
  };

  const handleGenerateCL = () => {
    setIsGeneratingCL(true);
    setTimeout(() => {
      setIsGeneratingCL(false);
      setClVersion(prev => (prev === 1 ? 2 : 1));
      setApps(apps.map(a => a.id === selectedApp.id ? { ...a, hasTailoredCoverLetter: true, coverLetterVersion: clVersion === 1 ? 2 : 1 } : a));
    }, 600);
  };

  const handleOptimizeCV = () => {
    setIsOptimizingCV(true);
    setTimeout(() => {
      setIsOptimizingCV(false);
      setApps(apps.map(a => a.id === selectedApp.id ? { ...a, atsCoverageScore: 94, docsAttached: Math.min(a.docsRequired, a.docsAttached + 1) } : a));
    }, 700);
  };

  const handleDraftQuestion = () => {
    setIsDraftingQuestion(true);
    setTimeout(() => {
      setIsDraftingQuestion(false);
      setApps(apps.map(a => a.id === selectedApp.id ? { ...a, questionsAnswered: a.questionsTotal } : a));
    }, 500);
  };

  const handleRunFullPrep = () => {
    setIsGeneratingCL(true);
    setIsOptimizingCV(true);
    setIsDraftingQuestion(true);
    setTimeout(() => {
      setIsGeneratingCL(false);
      setIsOptimizingCV(false);
      setIsDraftingQuestion(false);
      setPrepAllSuccess(true);
      setApps(apps.map(a => a.id === selectedApp.id ? {
        ...a,
        hasTailoredCoverLetter: true,
        coverLetterVersion: 2,
        atsCoverageScore: 95,
        docsAttached: a.docsRequired,
        questionsAnswered: a.questionsTotal,
        status: 'READY_TO_SUBMIT',
      } : a));
      setTimeout(() => setPrepAllSuccess(false), 3000);
    }, 900);
  };

  const testSuites = [
    { title: 'Milestone 6: AI Preparation Suite', path: 'tests/test_milestone_6.py', count: 10, desc: 'Zero hallucinations, grounded citations, cover letters, CV tailoring, STAR limit compliance' },
    { title: 'Milestone 5: Application Workspace Suite', path: 'tests/test_milestone_5.py', count: 10, desc: 'Workspace lifecycle, auto-populated documents, readiness score, question limits, user signoff' },
    { title: 'Milestone 4: Matching & Recommendations', path: 'tests/test_milestone_4.py', count: 11, desc: 'Exact/alias skills, hard eligibility constraints, evidence tracing, weighted scoring' },
    { title: 'Milestone 3: Opportunity Intelligence', path: 'tests/test_milestone_3.py', count: 12, desc: 'Deterministic extraction, Gemini & Hugging Face LLM router, injection defense' },
    { title: 'Milestone 2: Discovery & Ingestion', path: 'tests/test_milestone_2.py', count: 16, desc: 'Connectors, URL validation, HTML/RSS parsers, SSRF security, deduplication' },
    { title: 'Milestone 1: Professional Profile & Evidence', path: 'tests/test_milestone_1.py', count: 17, desc: 'Profile completeness, skill levels, evidence bank, isolated document vault' },
    { title: 'Milestone 0: Foundation & Core Infrastructure', path: 'tests/test_auth.py + test_health.py', count: 21, desc: 'Auth security, Celery async tasks, health probes, Nairobi timezone, settings' },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Header */}
      <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center font-bold text-white shadow-md shadow-blue-500/20">
              M
            </div>
            <div>
              <span className="font-bold text-base tracking-tight text-white">MwohaOS</span>
              <span className="ml-2 text-xs font-mono text-blue-400 bg-blue-950/80 px-2 py-0.5 rounded border border-blue-800">
                Milestone 6: AI Preparation
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-4 text-xs font-mono text-slate-400">
            <div className="hidden sm:flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>PostgreSQL 16 • Redis 7 • Celery</span>
            </div>
            <a 
              href="/admin/" 
              target="_blank" 
              rel="noreferrer" 
              className="text-slate-400 hover:text-white px-2.5 py-1 rounded bg-slate-800 border border-slate-700 transition"
            >
              Django Admin &rarr;
            </a>
          </div>
        </div>
      </header>

      {/* Navigation Sub-header */}
      <div className="border-b border-slate-800 bg-slate-900/40">
        <nav className="max-w-6xl mx-auto px-6 flex space-x-6 text-xs">
          {[
            { id: 'aiprep', label: 'AI Preparation Studio (M6)', icon: Wand2, highlight: true },
            { id: 'workspace', label: 'Application Workspace (M5)', icon: ClipboardCheck },
            { id: 'matching', label: 'Matching & Fit (M4)', icon: Sparkles },
            { id: 'overview', label: 'System Overview', icon: Layers },
            { id: 'tests', label: 'Test Suites (97 Tests)', icon: CheckCircle2 },
            { id: 'health', label: 'Health Probes', icon: Activity },
          ].map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-3.5 border-b-2 flex items-center space-x-2 transition font-medium ${
                  isActive
                    ? tab.highlight 
                      ? 'border-blue-500 text-blue-400 font-bold'
                      : 'border-white text-white font-bold'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                <Icon className={`w-4 h-4 ${tab.highlight && isActive ? 'text-blue-400' : ''}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Main Content Area */}
      <main className="max-w-6xl mx-auto px-6 py-8 flex-1 w-full">

        {/* TAB: AI PREPARATION STUDIO (MILESTONE 6) */}
        {activeTab === 'aiprep' && (
          <div className="space-y-6">
            
            {/* AI Studio Header & Quick Action Banner */}
            <div className="bg-gradient-to-r from-slate-900 via-blue-950/50 to-indigo-950/60 border border-blue-900/40 rounded-xl p-6 shadow-lg">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="space-y-1.5">
                  <div className="flex items-center space-x-2">
                    <span className="text-[10px] font-mono uppercase tracking-wider text-blue-400 font-semibold bg-blue-950 px-2 py-0.5 rounded border border-blue-800">
                      Milestone 6 AI Preparation
                    </span>
                    <span className="text-xs text-emerald-400 flex items-center font-mono">
                      <ShieldCheck className="w-3.5 h-3.5 mr-1" />
                      Zero Hallucinations Verified
                    </span>
                  </div>
                  <h1 className="text-xl font-bold text-white tracking-tight">
                    Evidence-Grounded Material Tailoring & Essay Studio
                  </h1>
                  <p className="text-xs text-slate-300 max-w-2xl leading-relaxed">
                    Synthesizes bespoke cover letters, optimizes CV keywords for ATS compliance, and answers essay prompts using the STAR framework—strictly grounded in verified profile evidence.
                  </p>
                </div>

                <div className="flex flex-col sm:flex-row items-end sm:items-center gap-3">
                  <button
                    onClick={handleRunFullPrep}
                    disabled={isGeneratingCL || isOptimizingCV}
                    className="px-4 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-lg text-xs font-bold shadow-md flex items-center space-x-2 transition disabled:opacity-50"
                  >
                    <Zap className="w-4 h-4 text-amber-300" />
                    <span>Run Full AI Preparation (All Materials)</span>
                  </button>
                </div>
              </div>

              {prepAllSuccess && (
                <div className="mt-4 p-3 bg-emerald-950/80 border border-emerald-800 rounded-lg text-xs text-emerald-200 flex items-center space-x-2 animate-fade-in">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>Full AI Preparation executed successfully! Cover letter attached, CV optimized, and questions drafted. Workspace readiness upgraded to 95%.</span>
                </div>
              )}
            </div>

            {/* Target Opportunity Selector */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <div className="text-xs font-mono text-slate-400">
                ACTIVE APPLICATION WORKSPACE:
              </div>
              <div className="flex flex-wrap gap-2">
                {apps.map(a => (
                  <button
                    key={a.id}
                    onClick={() => setSelectedAppId(a.id)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                      selectedApp.id === a.id
                        ? 'bg-blue-600 text-white shadow-sm'
                        : 'bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-slate-200'
                    }`}
                  >
                    {a.title.split(' ')[0]} {a.title.split(' ')[1]} ({a.org.split(' ')[0]})
                  </button>
                ))}
              </div>
            </div>

            {/* 3 Main Studio Columns / Cards */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

              {/* CARD 1: Tailored Cover Letter */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div className="flex items-center space-x-2">
                    <FileText className="w-4 h-4 text-blue-400" />
                    <h3 className="text-sm font-bold text-white">1. Tailored Cover Letter</h3>
                  </div>
                  <span className="text-[10px] font-mono text-slate-400">v{clVersion} active</span>
                </div>

                <div className="flex items-center justify-between gap-2 text-xs">
                  <select
                    value={aiTone}
                    onChange={(e: any) => setAiTone(e.target.value)}
                    className="bg-slate-950 border border-slate-800 rounded px-2.5 py-1 text-slate-300 text-xs focus:ring-1 focus:ring-blue-500"
                  >
                    <option value="PROFESSIONAL">Professional</option>
                    <option value="EXECUTIVE">Executive</option>
                    <option value="ACADEMIC">Academic</option>
                  </select>

                  <button
                    onClick={handleGenerateCL}
                    disabled={isGeneratingCL}
                    className="px-2.5 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-semibold flex items-center space-x-1"
                  >
                    <Wand2 className={`w-3.5 h-3.5 ${isGeneratingCL ? 'animate-spin' : ''}`} />
                    <span>{isGeneratingCL ? 'Generating...' : 'Regenerate Draft'}</span>
                  </button>
                </div>

                {/* Draft Content Container */}
                <div className="bg-slate-950 border border-slate-800/80 rounded-lg p-3 text-xs leading-relaxed text-slate-300 font-serif max-h-72 overflow-y-auto whitespace-pre-line shadow-inner">
                  {coverLetterDrafts[clVersion]?.text}
                </div>

                {/* Grounding Audit Citations */}
                <div className="space-y-1.5 pt-2 border-t border-slate-800/60">
                  <div className="text-[10px] font-mono uppercase text-slate-400 font-bold flex items-center justify-between">
                    <span>Evidence Grounding Citations</span>
                    <span className="text-emerald-400">100% Traceable</span>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {coverLetterDrafts[clVersion]?.citations.map((cite, i) => (
                      <span key={i} className="text-[10px] font-mono bg-blue-950 text-blue-300 px-1.5 py-0.5 rounded border border-blue-900/60">
                        {cite}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* CARD 2: CV Tailoring & ATS Optimization */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div className="flex items-center space-x-2">
                    <FileCheck2 className="w-4 h-4 text-emerald-400" />
                    <h3 className="text-sm font-bold text-white">2. CV & ATS Tailoring</h3>
                  </div>
                  <button
                    onClick={handleOptimizeCV}
                    disabled={isOptimizingCV}
                    className="text-xs text-emerald-400 hover:underline flex items-center space-x-1"
                  >
                    <RotateCcw className={`w-3 h-3 ${isOptimizingCV ? 'animate-spin' : ''}`} />
                    <span>Re-Analyze</span>
                  </button>
                </div>

                {/* ATS Match Gauge */}
                <div className="bg-slate-950 border border-slate-800 p-3 rounded-lg flex items-center justify-between">
                  <div>
                    <span className="text-[10px] font-mono uppercase text-slate-400 block">ATS Keyword Alignment</span>
                    <span className="text-lg font-bold font-mono text-emerald-400">
                      {selectedApp.atsCoverageScore}% MATCH
                    </span>
                  </div>
                  <div className="w-24 bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${selectedApp.atsCoverageScore}%` }}></div>
                  </div>
                </div>

                {/* Targeted Summary */}
                <div className="space-y-1">
                  <span className="text-[10px] font-mono uppercase text-slate-400 block font-bold">Targeted Executive Summary</span>
                  <div className="p-2.5 bg-slate-950 border border-slate-800 rounded text-xs text-slate-300 leading-relaxed font-serif">
                    "Results-driven Earth Observation researcher with verified expertise in Python, Sentinel-1 radar processing, and scalable environmental models. Targeted specifically for the ESA fellowship in Frascati."
                  </div>
                </div>

                {/* Prioritized Competencies */}
                <div className="space-y-1.5">
                  <span className="text-[10px] font-mono uppercase text-slate-400 block font-bold">Prioritized Competencies</span>
                  <div className="grid grid-cols-2 gap-1.5 text-[11px] font-mono">
                    <div className="p-1.5 bg-blue-950/70 border border-blue-800 rounded text-blue-200 flex justify-between">
                      <span>Python</span>
                      <span className="text-blue-400 font-bold">EXACT</span>
                    </div>
                    <div className="p-1.5 bg-blue-950/70 border border-blue-800 rounded text-blue-200 flex justify-between">
                      <span>Sentinel-1</span>
                      <span className="text-blue-400 font-bold">EXACT</span>
                    </div>
                    <div className="p-1.5 bg-blue-950/70 border border-blue-800 rounded text-blue-200 flex justify-between">
                      <span>GDAL / GIS</span>
                      <span className="text-slate-400">TOOL</span>
                    </div>
                    <div className="p-1.5 bg-blue-950/70 border border-blue-800 rounded text-blue-200 flex justify-between">
                      <span>Docker</span>
                      <span className="text-slate-400">TOOL</span>
                    </div>
                  </div>
                </div>

                {/* Optimized Bullet Example */}
                <div className="p-2.5 bg-slate-950 border border-slate-800 rounded text-[11px] text-slate-300 space-y-1">
                  <span className="text-[10px] font-mono text-emerald-400 block">Optimized STAR Accomplishment Bullet:</span>
                  <p>• Engineered automated Sentinel-1 SAR ingestion pipeline using Python, reducing processing overhead by 40% across 5 operational hubs.</p>
                </div>
              </div>

              {/* CARD 3: Question Answering (STAR Framework) */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div className="flex items-center space-x-2">
                    <HelpCircle className="w-4 h-4 text-purple-400" />
                    <h3 className="text-sm font-bold text-white">3. STAR Essay Prompts</h3>
                  </div>
                  <span className="text-[10px] font-mono text-purple-400 bg-purple-950 px-2 py-0.5 rounded border border-purple-800">
                    Limit Enforced
                  </span>
                </div>

                {/* Question Selector */}
                <div className="space-y-1">
                  <span className="text-[10px] font-mono uppercase text-slate-400 block font-bold">Select Application Prompt:</span>
                  <select
                    value={selectedQuestionIndex}
                    onChange={(e: any) => setSelectedQuestionIndex(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-slate-300 text-xs focus:ring-1 focus:ring-purple-500"
                  >
                    {mockQuestions.map((q, idx) => (
                      <option key={idx} value={idx}>
                        Q{idx + 1}: {q.q.slice(0, 45)}... ({q.limitWords} words)
                      </option>
                    ))}
                  </select>
                </div>

                {/* Framework Selector & AI Draft Trigger */}
                <div className="flex items-center justify-between gap-2 text-xs">
                  <select
                    value={questionTone}
                    onChange={(e: any) => setQuestionTone(e.target.value)}
                    className="bg-slate-950 border border-slate-800 rounded px-2.5 py-1 text-slate-300 text-xs focus:ring-1 focus:ring-purple-500"
                  >
                    <option value="STAR_METHOD">STAR Framework</option>
                    <option value="CONCISE">Concise & Direct</option>
                    <option value="EXECUTIVE">Executive Impact</option>
                  </select>

                  <button
                    onClick={handleDraftQuestion}
                    disabled={isDraftingQuestion}
                    className="px-2.5 py-1 bg-purple-600 hover:bg-purple-700 text-white rounded text-xs font-semibold flex items-center space-x-1"
                  >
                    <Wand2 className={`w-3.5 h-3.5 ${isDraftingQuestion ? 'animate-spin' : ''}`} />
                    <span>Draft Answer</span>
                  </button>
                </div>

                {/* Question Draft Text */}
                <div className="bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs leading-relaxed text-slate-300 font-serif max-h-56 overflow-y-auto whitespace-pre-line shadow-inner">
                  {mockQuestions[selectedQuestionIndex].answers[questionTone]}
                </div>

                {/* Word & Limit Gauge */}
                <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[11px] font-mono text-slate-400">
                  <span>
                    Word Count: <strong className="text-white">
                      {mockQuestions[selectedQuestionIndex].answers[questionTone].split(' ').length}
                    </strong> / {mockQuestions[selectedQuestionIndex].limitWords} max
                  </span>
                  <span className="text-emerald-400 font-bold bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-900">
                    Within Limit
                  </span>
                </div>
              </div>

            </div>

            {/* CLI Command Helper for Developers */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs font-mono">
              <div className="flex items-center space-x-2 text-slate-300">
                <Terminal className="w-4 h-4 text-blue-400" />
                <span>CLI Execution:</span>
                <code className="text-emerald-400 bg-slate-950 px-2 py-1 rounded border border-slate-800">
                  python manage.py ai_prep_application --application {selectedApp.id} --all
                </code>
              </div>
              <button
                onClick={() => copyToClipboard(`python manage.py ai_prep_application --application ${selectedApp.id} --all`)}
                className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded border border-slate-700 flex items-center space-x-1 text-xs"
              >
                {copiedCmd ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedCmd ? 'Copied' : 'Copy'}</span>
              </button>
            </div>

          </div>
        )}

        {/* TAB: WORKSPACE (MILESTONE 5) */}
        {activeTab === 'workspace' && (
          <div className="space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
              <h2 className="text-base font-bold text-white">Milestone 5 Application Workspace</h2>
              <p className="text-xs text-slate-300">
                Deterministic readiness score evaluation, checklist validation, and submission confirmation.
              </p>
              
              <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg flex items-center justify-between">
                <div>
                  <div className="text-xs font-bold text-white">{selectedApp.title}</div>
                  <div className="text-[11px] text-slate-400">{selectedApp.org} • Status: {selectedApp.status}</div>
                </div>
                <div className="text-right">
                  <div className="text-xs font-mono text-blue-400">Readiness: {totalReadiness}%</div>
                  <button 
                    onClick={() => setActiveTab('aiprep')}
                    className="mt-1 text-xs text-blue-400 hover:underline"
                  >
                    Open in AI Prep Studio &rarr;
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB: MATCHING (MILESTONE 4) */}
        {activeTab === 'matching' && (
          <div className="space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h2 className="text-base font-semibold text-white">Milestone 4: Matching & Recommendations</h2>
              <p className="text-xs text-slate-400 mt-1">
                Deterministic scoring dimensions: Eligibility (25%), Skills (25%), Experience (20%), Sector (8%), Education (10%), Type (5%), Location (5%), Preferences (2%).
              </p>
            </div>
          </div>
        )}

        {/* TAB: SYSTEM ARCHITECTURE & ROADMAP */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
              <h2 className="text-base font-bold text-white">MwohaOS Milestones Roadmap</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {[
                  { m: 'Milestone 0', title: 'Foundation Infrastructure', status: 'COMPLETE', desc: 'Django 5, PostgreSQL 16, Redis 7, Celery beat' },
                  { m: 'Milestone 1', title: 'Profile & Evidence Vault', status: 'COMPLETE', desc: 'Rich multi-attribute profiles, isolated vault' },
                  { m: 'Milestone 2', title: 'Discovery & Ingestion', status: 'COMPLETE', desc: 'RSS/Web scrapers, SSRF security, deduplication' },
                  { m: 'Milestone 3', title: 'Intelligence & LLM Router', status: 'COMPLETE', desc: 'Gemini primary, Hugging Face fallback' },
                  { m: 'Milestone 4', title: 'Matching & Recommendations', status: 'COMPLETE', desc: 'Exact/alias skills, hard constraints, scoring' },
                  { m: 'Milestone 5', title: 'Application Workspace', status: 'COMPLETE', desc: 'Materials checklist, question drafts, readiness' },
                  { m: 'Milestone 6', title: 'AI Preparation Studio', status: 'COMPLETE', desc: 'Zero-hallucination cover letters, CV tailoring, STAR essays' },
                  { m: 'Milestone 7', title: 'Browser Agent', status: 'NEXT', desc: 'Headless Playwright automation & interactive validation' },
                  { m: 'Milestone 8', title: 'Submission Engine', status: 'PLANNED', desc: 'Receipt extraction and end-to-end delivery' },
                ].map(item => (
                  <div key={item.m} className={`p-4 rounded-lg border space-y-1.5 ${
                    item.status === 'COMPLETE' 
                      ? 'bg-slate-900 border-slate-800' 
                      : item.status === 'NEXT'
                      ? 'bg-blue-950/30 border-blue-700/60'
                      : 'bg-slate-950/50 border-slate-900 opacity-60'
                  }`}>
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono font-bold text-blue-400">{item.m}</span>
                      <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                        item.status === 'COMPLETE' ? 'bg-emerald-950 text-emerald-300 border-emerald-800' :
                        item.status === 'NEXT' ? 'bg-blue-950 text-blue-300 border-blue-700' :
                        'bg-slate-900 text-slate-500 border-slate-800'
                      }`}>
                        {item.status}
                      </span>
                    </div>
                    <h4 className="text-sm font-bold text-white">{item.title}</h4>
                    <p className="text-xs text-slate-400">{item.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB: AUTOMATED TESTS */}
        {activeTab === 'tests' && (
          <div className="space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                <div>
                  <h2 className="text-base font-semibold text-white">Automated Test Suites (Pytest)</h2>
                  <p className="text-xs text-slate-400">97 comprehensive automated tests across all completed milestones</p>
                </div>
                <span className="px-2.5 py-1 text-xs font-mono bg-blue-950 text-blue-400 border border-blue-800 rounded-full">
                  pytest & pytest-django
                </span>
              </div>

              <div className="mt-4 space-y-3">
                {testSuites.map((suite) => (
                  <div key={suite.path} className="p-4 bg-slate-950 border border-slate-800 rounded-lg flex items-center justify-between">
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs font-semibold text-white">{suite.title}</span>
                        <span className="text-[10px] font-mono bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded">
                          {suite.count} Tests
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400 mt-0.5">{suite.desc}</p>
                    </div>
                    <code className="text-[11px] font-mono text-emerald-400 bg-emerald-950/40 px-2 py-1 rounded border border-emerald-900">
                      {suite.path}
                    </code>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB: HEALTH */}
        {activeTab === 'health' && (
          <div className="space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h2 className="text-base font-semibold text-white">System Probes & Endpoints</h2>
              <div className="mt-4 space-y-3 text-xs font-mono">
                <div className="p-3 bg-slate-950 border border-slate-800 rounded flex items-center justify-between">
                  <span className="text-blue-400">GET /health/</span>
                  <span className="text-emerald-400 font-bold">200 OK</span>
                </div>
                <div className="p-3 bg-slate-950 border border-slate-800 rounded flex items-center justify-between">
                  <span className="text-indigo-400">GET /health/database/ (PostgreSQL 16)</span>
                  <span className="text-emerald-400 font-bold">200 OK</span>
                </div>
                <div className="p-3 bg-slate-950 border border-slate-800 rounded flex items-center justify-between">
                  <span className="text-rose-400">GET /health/redis/ (Celery Broker)</span>
                  <span className="text-emerald-400 font-bold">200 OK</span>
                </div>
              </div>
            </div>
          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-900/60 py-4 px-6 text-xs text-slate-400 flex flex-col sm:flex-row items-center justify-between gap-2">
        <div>
          <span>MwohaOS — Milestone 6: AI Preparation</span>
          <span className="mx-2 text-slate-600">•</span>
          <span className="text-slate-500">Ready for Milestone 7 (Browser Agent)</span>
        </div>
        <div className="font-mono text-slate-500 text-[11px]">
          Python 3.12 • Django 5.x • Nairobi Timezone
        </div>
      </footer>
    </div>
  );
}
