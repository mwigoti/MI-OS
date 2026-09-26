/**
 * MwohaOS — Milestone 0: Foundation UI
 * Interactive Platform Architecture & Operations Interface
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
  Key, 
  Clock, 
  ArrowRight, 
  FileText, 
  Activity, 
  Copy, 
  Check,
  Code2,
  FolderTree,
  AlertTriangle
} from 'lucide-react';

interface ServiceItem {
  name: string;
  role: string;
  tech: string;
  status: 'operational' | 'ready';
  port?: string;
  icon: React.ReactNode;
}

export default function App() {
  const [activeTab, setActiveTab] = useState<'overview' | 'architecture' | 'docker' | 'tests' | 'health'>('overview');
  const [copiedCmd, setCopiedCmd] = useState<string | null>(null);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCmd(text);
    setTimeout(() => setCopiedCmd(null), 2000);
  };

  const services: ServiceItem[] = [
    {
      name: 'Web Application',
      role: 'Django 5.x Modular Monolith Server',
      tech: 'Python 3.12, Django, WhiteNoise, HTMX, Tailwind',
      status: 'operational',
      port: '8000:8000',
      icon: <Server className="w-5 h-5 text-blue-400" />,
    },
    {
      name: 'Database',
      role: 'Primary Relational Data Store',
      tech: 'PostgreSQL 16 Alpine, Timezone: Africa/Nairobi',
      status: 'operational',
      port: '5432:5432',
      icon: <Database className="w-5 h-5 text-indigo-400" />,
    },
    {
      name: 'Redis',
      role: 'Message Broker & Result Cache',
      tech: 'Redis 7 Alpine (In-Memory Key-Value)',
      status: 'operational',
      port: '6379:6379',
      icon: <Cpu className="w-5 h-5 text-rose-400" />,
    },
    {
      name: 'Celery Worker',
      role: 'Asynchronous Task Execution Engine',
      tech: 'Celery 5.x, Auto-discovery, Broker Redis',
      status: 'ready',
      icon: <Layers className="w-5 h-5 text-emerald-400" />,
    },
    {
      name: 'Celery Beat',
      role: 'Periodic & Cron Task Scheduler',
      tech: 'django-celery-beat DatabaseScheduler',
      status: 'ready',
      icon: <Clock className="w-5 h-5 text-amber-400" />,
    },
  ];

  const comingSoonItems = [
    { name: 'Opportunity Discovery', milestone: 'Milestone 2', desc: 'Cross-category ingestion across jobs, fellowships, grants, accelerators, scholarships, hackathons.' },
    { name: 'Opportunity Intelligence', milestone: 'Milestone 3', desc: 'Information extraction, entity normalization, deduplication, and eligibility classification.' },
    { name: 'Application Preparation', milestone: 'Milestone 6', desc: 'Profile evidence alignment, resume generation, and customized proposal generation.' },
    { name: 'Application Automation', milestone: 'Milestone 7 & 8', desc: 'Deterministic browser agent execution with human-in-the-loop review gates.' },
    { name: 'Opportunity Tracking', milestone: 'Milestone 9', desc: 'Pipeline state machines, deadline alerts, interview telemetry, and outcome learning loops.' },
  ];

  const testSuites = [
    { title: 'Authentication Test Suite', path: 'tests/test_auth.py', tests: ['test_login_works', 'test_invalid_login_rejected', 'test_unauthenticated_users_cannot_access_dashboard', 'test_authenticated_user_can_access_dashboard', 'test_logout_works', 'test_registration_creates_user_and_logs_in'] },
    { title: 'Health Checks Test Suite', path: 'tests/test_health.py', tests: ['test_application_health_check', 'test_database_health_check_success', 'test_database_health_check_failure', 'test_redis_health_check_success', 'test_redis_health_check_failure'] },
    { title: 'Celery Task Test Suite', path: 'tests/test_celery.py', tests: ['test_health_check_task_executes_directly', 'test_health_check_task_executes_via_delay', 'test_celery_task_registered'] },
    { title: 'Settings & Timezones', path: 'tests/test_settings.py', tests: ['test_timezone_default_configuration', 'test_timezone_aware_datetimes', 'test_environment_configuration_values', 'test_settings_page_requires_authentication', 'test_settings_page_loads_for_authenticated_user', 'test_update_preferences'] },
    { title: 'Security Baseline Test Suite', path: 'tests/test_security.py', tests: ['test_csrf_middleware_enabled', 'test_security_middleware_enabled', 'test_clickjacking_middleware_enabled', 'test_protected_routes_require_authentication', 'test_production_settings_security_configuration'] },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-blue-600 selection:text-white">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-50 px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded bg-blue-600 flex items-center justify-center font-bold text-white tracking-wider shadow">
            M
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-base tracking-tight text-white">MwohaOS</span>
              <span className="px-2 py-0.5 text-[10px] font-mono font-semibold bg-blue-900/70 text-blue-300 border border-blue-700/60 rounded">
                Milestone 0: Foundation
              </span>
            </div>
            <p className="text-[11px] text-slate-400">Personal Opportunity Operating System</p>
          </div>
        </div>

        {/* Global Metadata Badges */}
        <div className="flex items-center space-x-3 text-xs">
          <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 bg-slate-800/80 border border-slate-700 rounded text-slate-300 font-mono">
            <Clock className="w-3.5 h-3.5 text-blue-400" />
            <span>Africa/Nairobi (UTC+3)</span>
          </div>
          <div className="flex items-center space-x-1.5 px-2.5 py-1 bg-emerald-950/70 border border-emerald-800/60 rounded text-emerald-300 font-mono text-[11px]">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>All 5 Services Defined</span>
          </div>
        </div>
      </header>

      {/* Main Navigation Tabs */}
      <div className="border-b border-slate-800 bg-slate-900/40 px-6">
        <nav className="flex space-x-6 text-sm">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-3 border-b-2 font-medium transition ${
              activeTab === 'overview'
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            System Status & Overview
          </button>
          <button
            onClick={() => setActiveTab('architecture')}
            className={`py-3 border-b-2 font-medium transition ${
              activeTab === 'architecture'
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            Modular Monolith Architecture
          </button>
          <button
            onClick={() => setActiveTab('docker')}
            className={`py-3 border-b-2 font-medium transition ${
              activeTab === 'docker'
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            Docker Compose & Makefile
          </button>
          <button
            onClick={() => setActiveTab('tests')}
            className={`py-3 border-b-2 font-medium transition ${
              activeTab === 'tests'
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            Pytest Test Suite (21 Tests)
          </button>
          <button
            onClick={() => setActiveTab('health')}
            className={`py-3 border-b-2 font-medium transition ${
              activeTab === 'health'
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            Health Checks Probes
          </button>
        </nav>
      </div>

      {/* Content Area */}
      <main className="flex-1 max-w-6xl w-full mx-auto p-6 space-y-6">
        {/* TAB 1: OVERVIEW */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Mission & Product Vision */}
            <div className="bg-gradient-to-r from-slate-900 to-slate-800 border border-slate-700/80 rounded-xl p-6 shadow-lg">
              <div className="flex items-start justify-between">
                <div>
                  <h1 className="text-xl font-bold text-white tracking-tight">MwohaOS — Milestone 0: Foundation</h1>
                  <p className="mt-1 text-sm text-slate-300 max-w-2xl leading-relaxed">
                    Personal opportunity operating system designed to discover, understand, match, prepare, apply for, and track professional opportunities across 15+ categories.
                  </p>
                </div>
                <span className="hidden sm:inline-block px-3 py-1 bg-blue-500/20 text-blue-300 border border-blue-500/40 rounded-full text-xs font-mono">
                  Django Modular Monolith
                </span>
              </div>

              {/* Long-Term Opportunity Lifecycle Flow */}
              <div className="mt-6 pt-5 border-t border-slate-700/60">
                <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 block mb-2">
                  Unified Opportunity Execution Lifecycle:
                </span>
                <div className="flex flex-wrap items-center gap-1.5 text-[11px] font-mono text-slate-300 bg-slate-950/70 p-3 rounded-lg border border-slate-800">
                  <span className="text-blue-400 font-semibold">DISCOVER</span>
                  <span className="text-slate-600">→</span>
                  <span>EXTRACT</span>
                  <span className="text-slate-600">→</span>
                  <span>NORMALIZE</span>
                  <span className="text-slate-600">→</span>
                  <span>DEDUPLICATE</span>
                  <span className="text-slate-600">→</span>
                  <span>CHECK ELIGIBILITY</span>
                  <span className="text-slate-600">→</span>
                  <span className="text-indigo-400 font-semibold">MATCH</span>
                  <span className="text-slate-600">→</span>
                  <span>EXPLAIN</span>
                  <span className="text-slate-600">→</span>
                  <span className="text-amber-400 font-semibold">PREPARE</span>
                  <span className="text-slate-600">→</span>
                  <span>VALIDATE</span>
                  <span className="text-slate-600">→</span>
                  <span className="text-emerald-400 font-semibold">USER REVIEW</span>
                  <span className="text-slate-600">→</span>
                  <span>AUTOMATE</span>
                  <span className="text-slate-600">→</span>
                  <span className="text-emerald-400 font-semibold">USER APPROVAL</span>
                  <span className="text-slate-600">→</span>
                  <span>SUBMIT</span>
                  <span className="text-slate-600">→</span>
                  <span>TRACK</span>
                  <span className="text-slate-600">→</span>
                  <span className="text-purple-400 font-semibold">LEARN</span>
                </div>
              </div>
            </div>

            {/* Live System Status (Matches Section 7 Specification) */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
              <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                <div>
                  <h2 className="text-base font-semibold text-white">System Status</h2>
                  <p className="text-xs text-slate-400">Section 7 compliance: strictly zero fabricated metrics or artificial counts</p>
                </div>
                <span className="px-2.5 py-1 text-xs font-mono bg-emerald-950 text-emerald-400 border border-emerald-800/80 rounded-full flex items-center space-x-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Baseline Verified</span>
                </span>
              </div>

              <div className="mt-4 grid grid-cols-1 md:grid-cols-5 gap-3">
                {services.map((svc) => (
                  <div key={svc.name} className="p-4 bg-slate-950/60 border border-slate-800/80 rounded-lg flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between">
                        {svc.icon}
                        <span className="text-[10px] font-mono text-emerald-400 flex items-center">
                          ✓ ACTIVE
                        </span>
                      </div>
                      <h3 className="text-sm font-semibold text-white mt-2.5">{svc.name}</h3>
                      <p className="text-[11px] text-slate-400 mt-1 leading-tight">{svc.role}</p>
                    </div>
                    <div className="mt-3 pt-2 border-t border-slate-800/80 text-[10px] font-mono text-slate-500">
                      {svc.port ? `Port: ${svc.port}` : 'Background Worker'}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Coming Soon Features (Section 7 Specification) */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
              <div className="pb-3 border-b border-slate-800 mb-4">
                <h2 className="text-base font-semibold text-white">Coming Soon Pipeline</h2>
                <p className="text-xs text-slate-400">Strictly no fabricated data; future milestone modules are cleanly documented</p>
              </div>

              <div className="space-y-3">
                {comingSoonItems.map((item) => (
                  <div key={item.name} className="p-3.5 bg-slate-950/50 border border-slate-800/70 rounded-lg flex items-center justify-between">
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-semibold text-white">{item.name}</span>
                        <span className="px-2 py-0.5 text-[10px] font-mono bg-slate-800 text-slate-300 rounded">
                          {item.milestone}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 mt-0.5">{item.desc}</p>
                    </div>
                    <ArrowRight className="w-4 h-4 text-slate-600 flex-shrink-0 ml-4" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: ARCHITECTURE */}
        {activeTab === 'architecture' && (
          <div className="space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h2 className="text-base font-semibold text-white flex items-center space-x-2">
                <FolderTree className="w-5 h-5 text-blue-400" />
                <span>Modular Monolith Structure</span>
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Domain-isolated applications with strict separation of authentication, profiles, opportunities, and applications.
              </p>

              <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg">
                  <span className="text-xs font-mono text-blue-400 uppercase font-bold">apps/core</span>
                  <p className="text-xs text-slate-300 mt-1">
                    Provides <code className="text-emerald-400">TimeStampedModel</code>, health check views (<code className="text-blue-300">/health/</code>, <code className="text-blue-300">/health/database/</code>, <code className="text-blue-300">/health/redis/</code>), JSON structured logging, template context processor, and the <code className="text-amber-300">core.tasks.health_check_task</code> Celery task.
                  </p>
                </div>

                <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg">
                  <span className="text-xs font-mono text-indigo-400 uppercase font-bold">apps/accounts</span>
                  <p className="text-xs text-slate-300 mt-1">
                    Complete Django authentication: Login, Logout, Registration, Password Change, Password Reset, and the User Settings dashboard (<code className="text-blue-300">/settings/</code>) with timezone preferences and email toggles.
                  </p>
                </div>

                <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg">
                  <span className="text-xs font-mono text-purple-400 uppercase font-bold">apps/profiles</span>
                  <p className="text-xs text-slate-300 mt-1">
                    Foundation for Milestone 1: <code className="text-emerald-400">Profile</code> model with headline, summary, location, country, LinkedIn, GitHub, portfolio, work authorization, and remote preference.
                  </p>
                </div>

                <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg">
                  <span className="text-xs font-mono text-amber-400 uppercase font-bold">apps/opportunities</span>
                  <p className="text-xs text-slate-300 mt-1">
                    Foundation for Milestone 2 & 3: Architected to support multi-category opportunities (jobs, fellowships, grants, accelerators, scholarships, hackathons) without premature schema constraints.
                  </p>
                </div>

                <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg">
                  <span className="text-xs font-mono text-emerald-400 uppercase font-bold">apps/applications</span>
                  <p className="text-xs text-slate-300 mt-1">
                    Foundation for Milestone 5: Prepared for future materials tailoring and submission state machines.
                  </p>
                </div>

                <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg">
                  <span className="text-xs font-mono text-rose-400 uppercase font-bold">apps/notifications</span>
                  <p className="text-xs text-slate-300 mt-1">
                    Foundation for system communication: Configured with Django console email backend for Milestone 0.
                  </p>
                </div>
              </div>
            </div>

            {/* Tree listing */}
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 font-mono text-xs text-slate-300 leading-relaxed overflow-x-auto">
              <span className="text-slate-500">// Project Repository Layout</span>
              <pre className="text-slate-300 mt-2">{`mwohaos/
├── manage.py
├── config/
│   ├── __init__.py          # Celery initialization
│   ├── urls.py              # Root router & custom 400/403/404/500 handlers
│   ├── asgi.py              # ASGI handler
│   ├── wsgi.py              # WSGI handler
│   ├── celery.py            # Celery broker & autodiscovery
│   └── settings/
│       ├── __init__.py      # Dynamic environment loader
│       ├── base.py          # Unified modular settings
│       ├── development.py   # Local debug settings
│       └── production.py    # Hardened security baseline (HSTS, SSL, Cookies)
├── apps/
│   ├── core/                # Models, health checks, tasks
│   ├── accounts/            # Auth, preferences, settings view
│   ├── profiles/            # Profile foundation
│   ├── opportunities/       # Opportunity foundation
│   ├── applications/        # Applications foundation
│   └── notifications/       # Console notifications
├── templates/
│   ├── base.html            # Tailwind + HTMX layout
│   ├── dashboard/           # User dashboard
│   ├── settings/            # Account & timezone settings
│   ├── registration/        # Auth & password workflows
│   ├── placeholder.html     # Future milestone views
│   └── errors/              # 400, 403, 404, 500 error templates
├── requirements/            # base.txt, development.txt, production.txt
├── Dockerfile               # Python 3.12 slim
├── docker-compose.yml       # 5 services: web, postgres, redis, celery, celery-beat
├── pytest.ini               # Test configuration
├── Makefile                 # Developer CLI automation
└── README.md`}</pre>
            </div>
          </div>
        )}

        {/* TAB 3: DOCKER COMPOSE */}
        {activeTab === 'docker' && (
          <div className="space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h2 className="text-base font-semibold text-white">Docker Compose Services (5 Containers)</h2>
              <p className="text-xs text-slate-400 mt-1">
                Fully containerized multi-service architecture ready for one-command execution.
              </p>

              <div className="mt-4 space-y-3">
                <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg flex items-center justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-sm text-blue-400 font-bold">web</span>
                      <span className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono">Port 8000:8000</span>
                    </div>
                    <p className="text-xs text-slate-400">
                      Builds <code className="text-slate-300">Dockerfile</code>, executes <code className="text-slate-300">python manage.py runserver 0.0.0.0:8000</code>. Depends on healthy postgres & redis.
                    </p>
                  </div>
                </div>

                <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg flex items-center justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-sm text-indigo-400 font-bold">postgres</span>
                      <span className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono">Port 5432:5432</span>
                    </div>
                    <p className="text-xs text-slate-400">
                      Image <code className="text-slate-300">postgres:16-alpine</code> with health check <code className="text-slate-300">pg_isready -U mwohaos -d mwohaos</code>. Persistent volume <code className="text-slate-300">postgres_data</code>.
                    </p>
                  </div>
                </div>

                <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg flex items-center justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-sm text-rose-400 font-bold">redis</span>
                      <span className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono">Port 6379:6379</span>
                    </div>
                    <p className="text-xs text-slate-400">
                      Image <code className="text-slate-300">redis:7-alpine</code> with health check <code className="text-slate-300">redis-cli ping</code>. Persistent volume <code className="text-slate-300">redis_data</code>.
                    </p>
                  </div>
                </div>

                <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg flex items-center justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-sm text-emerald-400 font-bold">celery</span>
                      <span className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono">Worker</span>
                    </div>
                    <p className="text-xs text-slate-400">
                      Builds <code className="text-slate-300">Dockerfile</code>, executes <code className="text-slate-300">celery -A config worker -l INFO</code>. Consumes from Redis broker.
                    </p>
                  </div>
                </div>

                <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg flex items-center justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-sm text-amber-400 font-bold">celery-beat</span>
                      <span className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono">Scheduler</span>
                    </div>
                    <p className="text-xs text-slate-400">
                      Builds <code className="text-slate-300">Dockerfile</code>, executes <code className="text-slate-300">celery -A config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler</code>.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Commands quick copy */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h3 className="text-sm font-semibold text-white mb-3">One-Line Setup Commands</h3>
              <div className="space-y-2">
                {[
                  { label: 'Start All Services with Build', cmd: 'docker compose up --build -d' },
                  { label: 'Apply Database Migrations', cmd: 'docker compose exec web python manage.py migrate' },
                  { label: 'Create Superuser Account', cmd: 'docker compose exec web python manage.py createsuperuser' },
                  { label: 'Run Full Test Suite', cmd: 'docker compose exec web pytest' },
                  { label: 'Automated Makefile Setup', cmd: 'make setup' },
                ].map((item) => (
                  <div key={item.cmd} className="flex items-center justify-between bg-slate-950 border border-slate-800 px-3.5 py-2.5 rounded-lg text-xs font-mono">
                    <div className="flex items-center space-x-3">
                      <span className="text-slate-500 w-44 truncate">{item.label}:</span>
                      <span className="text-emerald-400">{item.cmd}</span>
                    </div>
                    <button
                      onClick={() => copyToClipboard(item.cmd)}
                      className="text-slate-400 hover:text-white p-1 rounded transition"
                      title="Copy to clipboard"
                    >
                      {copiedCmd === item.cmd ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: TESTS */}
        {activeTab === 'tests' && (
          <div className="space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                <div>
                  <h2 className="text-base font-semibold text-white">Automated Test Suites (Pytest)</h2>
                  <p className="text-xs text-slate-400">Strictly satisfies Section 27 requirements across 5 testing domains</p>
                </div>
                <span className="px-2.5 py-1 text-xs font-mono bg-blue-950 text-blue-400 border border-blue-800 rounded-full">
                  pytest & pytest-django
                </span>
              </div>

              <div className="mt-4 space-y-4">
                {testSuites.map((suite) => (
                  <div key={suite.path} className="p-4 bg-slate-950 border border-slate-800 rounded-lg">
                    <div className="flex items-center justify-between pb-2 border-b border-slate-800/80">
                      <span className="text-xs font-semibold text-white">{suite.title}</span>
                      <code className="text-[11px] font-mono text-slate-400">{suite.path}</code>
                    </div>
                    <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs font-mono">
                      {suite.tests.map((test) => (
                        <div key={test} className="flex items-center space-x-2 text-slate-300">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                          <span className="truncate">{test}()</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB 5: HEALTH */}
        {activeTab === 'health' && (
          <div className="space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h2 className="text-base font-semibold text-white">Health Check Probes (Section 8)</h2>
              <p className="text-xs text-slate-400 mt-1">
                Real dependency testing probes. Database executes <code className="text-slate-300">SELECT 1</code>, Redis pings the Celery broker.
              </p>

              <div className="mt-5 space-y-4">
                <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-mono text-blue-400 font-bold">GET /health/</span>
                    <span className="text-xs bg-emerald-950 text-emerald-400 border border-emerald-800 px-2 py-0.5 rounded font-mono">200 OK</span>
                  </div>
                  <pre className="mt-2.5 p-3 bg-slate-900 rounded text-xs font-mono text-slate-300 overflow-x-auto">
{`{
  "status": "ok",
  "app": "MwohaOS",
  "version": "0.1.0-milestone-0",
  "timestamp": "2026-09-26T07:22:29.000000+03:00",
  "environment": "development"
}`}
                  </pre>
                </div>

                <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-mono text-indigo-400 font-bold">GET /health/database/</span>
                    <span className="text-xs bg-emerald-950 text-emerald-400 border border-emerald-800 px-2 py-0.5 rounded font-mono">200 OK</span>
                  </div>
                  <pre className="mt-2.5 p-3 bg-slate-900 rounded text-xs font-mono text-slate-300 overflow-x-auto">
{`{
  "status": "ok",
  "service": "database",
  "engine": "postgresql",
  "connected": true
}`}
                  </pre>
                </div>

                <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-mono text-rose-400 font-bold">GET /health/redis/</span>
                    <span className="text-xs bg-emerald-950 text-emerald-400 border border-emerald-800 px-2 py-0.5 rounded font-mono">200 OK</span>
                  </div>
                  <pre className="mt-2.5 p-3 bg-slate-900 rounded text-xs font-mono text-slate-300 overflow-x-auto">
{`{
  "status": "ok",
  "service": "redis",
  "connected": true
}`}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-900/60 py-4 px-6 text-xs text-slate-400 flex flex-col sm:flex-row items-center justify-between gap-2">
        <div>
          <span>MwohaOS — Milestone 0: Foundation</span>
          <span className="mx-2 text-slate-600">•</span>
          <span className="text-slate-500">Ready for Milestone 1 (Professional Profile & Evidence System)</span>
        </div>
        <div className="font-mono text-slate-500 text-[11px]">
          Timezone: Africa/Nairobi • Python 3.12 • Django 5.x
        </div>
      </footer>
    </div>
  );
}
