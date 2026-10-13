import React, { useState, useEffect } from 'react';
import {
  Shield, Terminal, CheckCircle2, AlertTriangle, FileCode, Cpu,
  Layers, Download, RefreshCw, Play, ArrowRight, Lock, ExternalLink,
  Flame, Server, Code2, Check, X, Info, RotateCcw, GitBranch, Sparkles, History
} from 'lucide-react';

const PRESET_SAMPLES = {
  c: `#include <stdio.h>
#include <string.h>

void process_user(char *user_input) {
    char buffer[16];
    // Insecure buffer copy (CWE-120 / CWE-119)
    strcpy(buffer, user_input);
    printf("User: %s\\n", buffer);
}

int main() {
    char input[64] = "A_very_long_input_string_that_will_overflow";
    process_user(input);
    return 0;
}`,
  cpp: `#include <iostream>
#include <cstdio>

void log_message(const char *user_msg) {
    char log_buf[32];
    // Insecure sprintf without bounds checking (CWE-120)
    sprintf(log_buf, "EVENT: %s", user_msg);
    std::cout << log_buf << std::endl;
}

int main() {
    log_message("System alert test");
    return 0;
}`,
  python: `import subprocess
import os

def ping_host(host_ip):
    # Insecure command execution with shell=True (CWE-78 Command Injection)
    command = "ping -c 1 " + host_ip
    subprocess.call(command, shell=True)

if __name__ == "__main__":
    user_input = "127.0.0.1; whoami"
    ping_host(user_input)`,
  javascript: `const http = require('http');

function handleRequest(req, res) {
    const userInput = req.url.split('?q=')[1] || '';
    // Insecure code execution via eval (CWE-95)
    try {
        const result = eval(userInput);
        res.end("Result: " + result);
    } catch(e) {
        res.end("Error");
    }
}`,
  csharp: `using System;
using System.Data.SqlClient;

public class SecuritySample {
    public static void QueryUser(string username) {
        // Insecure dynamic SQL query assembly (CWE-89)
        string query = "SELECT * FROM Users WHERE Username = '" + username + "'";
        Console.WriteLine("Executing: " + query);
    }
}`
};

export default function App() {
  const [activeTab, setActiveTab] = useState('repair'); // Default to the dedicated AI Repair & Verify tab
  const [language, setLanguage] = useState('c');
  const [code, setCode] = useState(PRESET_SAMPLES['c']);
  const [filename, setFilename] = useState('source.c');

  // Real DevGPT Cases
  const [benchmarkCases, setBenchmarkCases] = useState([]);
  const [selectedDevGptCase, setSelectedDevGptCase] = useState('File_01');
  const [caseLoading, setCaseLoading] = useState(false);

  // Scans & Findings
  const [isScanning, setIsScanning] = useState(false);
  const [scanResult, setScanResult] = useState(null);
  const [selectedFinding, setSelectedFinding] = useState(null);

  // Explanation
  const [explanation, setExplanation] = useState(null);
  const [isExplaining, setIsExplaining] = useState(false);

  // Manual Repair & Verification
  const [isRepairing, setIsRepairing] = useState(false);
  const [repairResult, setRepairResult] = useState(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [verifyResult, setVerifyResult] = useState(null);

  // Autonomous Pipeline & Retry Loop
  const [isPipelineRunning, setIsPipelineRunning] = useState(false);
  const [pipelineResponse, setPipelineResponse] = useState(null);
  const [activeAttemptIdx, setActiveAttemptIdx] = useState(0);
  const [maxRetries, setMaxRetries] = useState(3);
  const [selectedModel, setSelectedModel] = useState('');

  // System & Reports
  const [systemHealth, setSystemHealth] = useState(null);
  const [historicalData, setHistoricalData] = useState(null);
  const [selectedCase, setSelectedCase] = useState(null);
  const [caseDetail, setCaseDetail] = useState(null);
  const [reportFeedback, setReportFeedback] = useState(null);
  const [isGeneratingReports, setIsGeneratingReports] = useState(false);
  const [generatedReports, setGeneratedReports] = useState(null);

  // Research Paper & Ground Truth Data (Belozerov et al., 2026)
  const [paperData, setPaperData] = useState(null);
  const [liveMetrics, setLiveMetrics] = useState(null);
  const [selectedRq, setSelectedRq] = useState('rq1');

  // Dynamic Dashboard (real backend data — no hardcoded numbers)
  const [dashboardSummary, setDashboardSummary] = useState(null);
  const [dashboardCharts, setDashboardCharts] = useState(null);
  const [dashboardLoading, setDashboardLoading] = useState(false);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [regenResult, setRegenResult] = useState(null);

  // Manual Auditor Workbench State (Section 5 Requirement)
  const [auditDecisions, setAuditDecisions] = useState([]);
  const [auditSummary, setAuditSummary] = useState(null);
  const [auditCaseId, setAuditCaseId] = useState('File_01');
  const [auditVerdict, setAuditVerdict] = useState('confirmed_vulnerability');
  const [auditModelDetected, setAuditModelDetected] = useState('detected');
  const [auditRepairVerified, setAuditRepairVerified] = useState('successfully_repaired');
  const [auditReviewer, setAuditReviewer] = useState('Deepu (Lead Security Auditor)');
  const [auditNotes, setAuditNotes] = useState('');
  const [auditEvidence, setAuditEvidence] = useState('');
  const [isSubmittingAudit, setIsSubmittingAudit] = useState(false);
  const [auditStatusMessage, setAuditStatusMessage] = useState('');

  useEffect(() => {
    fetchHealth();
    fetchHistoricalBenchmark();
    fetchBenchmarkCases();
    fetchResearchPaperData();
    fetchLiveMetrics();
    fetchAuditDecisions();
    fetchDashboardSummary();
    fetchDashboardCharts();
    // Auto-load File_01 on startup
    loadDevGptCase('File_01');
    handleInspectCase('File_01');
  }, []);

  const fetchDashboardSummary = async () => {
    try {
      const res = await fetch('/api/dashboard/summary');
      if (res.ok) {
        const data = await res.json();
        setDashboardSummary(data);
      }
    } catch (e) {
      console.warn("Could not load dashboard summary:", e);
    }
  };

  const fetchDashboardCharts = async () => {
    try {
      const res = await fetch('/api/dashboard/charts');
      if (res.ok) {
        const data = await res.json();
        setDashboardCharts(data);
      }
    } catch (e) {
      console.warn("Could not load dashboard charts:", e);
    }
  };

  const handleRegenerateReport = async () => {
    setIsRegenerating(true);
    setRegenResult(null);
    try {
      const res = await fetch('/api/benchmark/regenerate', { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setRegenResult(data);
        // Refresh dashboard after regeneration
        await fetchDashboardSummary();
        await fetchDashboardCharts();
        await fetchHistoricalBenchmark();
      } else {
        const err = await res.json().catch(() => ({}));
        setRegenResult({ status: 'error', message: err.detail || res.statusText });
      }
    } catch (e) {
      setRegenResult({ status: 'error', message: e.message });
    } finally {
      setIsRegenerating(false);
    }
  };


  const fetchResearchPaperData = async () => {
    try {
      const res = await fetch('/api/research/paper-data');
      if (res.ok) {
        const data = await res.json();
        setPaperData(data);
      }
    } catch (e) {
      console.warn("Could not load research paper data:", e);
    }
  };

  const fetchLiveMetrics = async () => {
    try {
      const res = await fetch('/api/research/evaluation-metrics');
      if (res.ok) {
        const data = await res.json();
        setLiveMetrics(data);
      }
    } catch (e) {
      console.warn("Could not load live metrics:", e);
    }
  };

  const fetchAuditDecisions = async () => {
    try {
      const res = await fetch('/api/audit/decisions');
      if (res.ok) {
        const data = await res.json();
        setAuditDecisions(data);
      }
      const sumRes = await fetch('/api/audit/summary');
      if (sumRes.ok) {
        const sData = await sumRes.json();
        setAuditSummary(sData);
      }
    } catch (e) {
      console.warn("Could not load audit decisions:", e);
    }
  };

  const handleSaveAuditDecision = async () => {
    setIsSubmittingAudit(true);
    setAuditStatusMessage('');
    try {
      const res = await fetch('/api/audit/decision', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          case_id: auditCaseId,
          verdict: auditVerdict,
          model_detected: auditModelDetected,
          repair_verified: auditRepairVerified,
          reviewer: auditReviewer,
          notes: auditNotes,
          evidence: auditEvidence,
          cwe: selectedFinding?.cwe || 'CWE-Unknown',
          line_no: selectedFinding?.line || 0,
          file_name: filename || 'source.c'
        })
      });
      if (res.ok) {
        setAuditStatusMessage('Audit decision successfully committed to persistent audit log!');
        setAuditNotes('');
        setAuditEvidence('');
        fetchAuditDecisions();
        fetchLiveMetrics();
      } else {
        setAuditStatusMessage('Failed to commit decision.');
      }
    } catch (e) {
      setAuditStatusMessage('Error: ' + e.message);
    } finally {
      setIsSubmittingAudit(false);
    }
  };

  const fetchHealth = async () => {
    try {
      const res = await fetch('/api/health');
      if (res.ok) {
        const data = await res.json();
        setSystemHealth(data);
        if (data.active_model && !selectedModel) {
          setSelectedModel(data.active_model);
        } else if (data.installed_models && data.installed_models.length > 0 && !selectedModel) {
          setSelectedModel(data.installed_models[0]);
        }
      }
    } catch (e) {
      console.warn("Backend health check:", e);
    }
  };

  const fetchHistoricalBenchmark = async () => {
    try {
      const res = await fetch('/api/benchmark/historical');
      if (res.ok) {
        const data = await res.json();
        setHistoricalData(data);
      }
    } catch (e) {
      console.warn("Could not load historical benchmark:", e);
    }
  };

  const fetchBenchmarkCases = async () => {
    try {
      const res = await fetch('/api/benchmark/cases');
      if (res.ok) {
        const data = await res.json();
        setBenchmarkCases(data);
      }
    } catch (e) {
      console.warn("Could not load benchmark cases:", e);
    }
  };

  const loadDevGptCase = async (caseId) => {
    if (caseId === 'custom') {
      setSelectedDevGptCase('custom');
      return;
    }
    setCaseLoading(true);
    setSelectedDevGptCase(caseId);
    setPipelineResponse(null);
    setRepairResult(null);
    setVerifyResult(null);
    setExplanation(null);

    try {
      const res = await fetch(`/api/benchmark/case/${caseId}`);
      if (res.ok) {
        const data = await res.json();
        setCode(data.original_code || '');
        setLanguage(data.language || 'c');
        setFilename(data.target_file || `${caseId}.c`);

        // Build scan result representation from real findings
        const findingsList = data.findings || data.dataset_findings || [];
        setScanResult({
          filename: data.target_file || `${caseId}.c`,
          language: data.language || 'c',
          total_findings: findingsList.length,
          scanners_executed: data.scanners || ['flawfinder'],
          scanners_unavailable: [],
          findings: findingsList
        });

        if (findingsList.length > 0) {
          setSelectedFinding(findingsList[0]);
        } else {
          setSelectedFinding(null);
        }
      }
    } catch (e) {
      console.error("Error loading DevGPT case:", e);
    } finally {
      setCaseLoading(false);
    }
  };

  const handleLanguageChange = (newLang) => {
    setSelectedDevGptCase('custom');
    setLanguage(newLang);
    setCode(PRESET_SAMPLES[newLang] || '// Enter source code here');
    setFilename(`source.${newLang}`);
    setScanResult(null);
    setSelectedFinding(null);
    setExplanation(null);
    setRepairResult(null);
    setVerifyResult(null);
    setPipelineResponse(null);
  };

  const handleRunScan = async () => {
    setIsScanning(true);
    setScanResult(null);
    setSelectedFinding(null);
    setExplanation(null);
    setRepairResult(null);
    setVerifyResult(null);
    setPipelineResponse(null);

    try {
      const res = await fetch('/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language, filename })
      });
      if (res.ok) {
        const data = await res.json();
        setScanResult(data);
        if (data.findings && data.findings.length > 0) {
          setSelectedFinding(data.findings[0]);
        }
      }
    } catch (e) {
      alert("Error scanning code: " + e.message);
    } finally {
      setIsScanning(false);
    }
  };

  const handleExplain = async (finding) => {
    setSelectedFinding(finding);
    setIsExplaining(true);
    setExplanation(null);
    try {
      const res = await fetch('/api/explain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language, finding, model_name: selectedModel || undefined })
      });
      if (res.ok) {
        const data = await res.json();
        setExplanation(data);
      }
    } catch (e) {
      alert("Error generating explanation: " + e.message);
    } finally {
      setIsExplaining(false);
    }
  };

  // Run the full autonomous repair pipeline with the retry loop
  const handleRunPipeline = async () => {
    if (!code.trim()) {
      alert("Source code cannot be empty.");
      return;
    }

    setIsPipelineRunning(true);
    setPipelineResponse(null);
    setActiveAttemptIdx(0);

    try {
      const res = await fetch('/api/pipeline/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code,
          language,
          filename,
          target_finding: selectedFinding,
          all_findings: scanResult?.findings || [],
          model_name: selectedModel || undefined,
          max_attempts: maxRetries
        })
      });

      if (res.ok) {
        const data = await res.json();
        setPipelineResponse(data);
        if (data.attempts && data.attempts.length > 0) {
          setActiveAttemptIdx(data.attempts.length - 1); // select the final attempt by default
        }
      } else {
        const err = await res.json();
        alert("Pipeline error: " + (err.detail || res.statusText));
      }
    } catch (e) {
      alert("Pipeline execution failed: " + e.message);
    } finally {
      setIsPipelineRunning(false);
    }
  };

  // Manual single-step repair
  const handleRepair = async () => {
    if (!code.trim()) return;
    setIsRepairing(true);
    setRepairResult(null);
    setVerifyResult(null);

    try {
      const res = await fetch('/api/repair', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code,
          language,
          findings: scanResult?.findings || [],
          target_finding: selectedFinding,
          model_name: selectedModel || undefined
        })
      });
      if (res.ok) {
        const data = await res.json();
        setRepairResult(data);
      }
    } catch (e) {
      alert("Error generating repair: " + e.message);
    } finally {
      setIsRepairing(false);
    }
  };

  // Manual single-step verification
  const handleVerify = async () => {
    const codeToVerify = pipelineResponse?.final_repaired_code || repairResult?.repaired_code;
    if (!codeToVerify) return;
    setIsVerifying(true);
    setVerifyResult(null);

    try {
      const res = await fetch('/api/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          original_code: code,
          repaired_code: codeToVerify,
          language,
          filename,
          baseline_findings: scanResult?.findings || [],
          target_finding: selectedFinding
        })
      });
      if (res.ok) {
        const data = await res.json();
        setVerifyResult(data);
      }
    } catch (e) {
      alert("Error during verification: " + e.message);
    } finally {
      setIsVerifying(false);
    }
  };

  const handleInspectCase = async (caseId) => {
    setSelectedCase(caseId);
    try {
      const res = await fetch(`/api/benchmark/case/${caseId}`);
      if (res.ok) {
        const data = await res.json();
        setCaseDetail(data);
      }
    } catch (e) {
      console.warn("Could not load case detail:", e);
    }
  };

  const handleSendCaseToRepair = (caseId) => {
    loadDevGptCase(caseId);
    setActiveTab('repair');
  };

  const handleGenerateReport = async () => {
    setIsGeneratingReports(true);
    setReportFeedback("Generating audit reports...");
    setGeneratedReports(null);
    try {
      const res = await fetch('/api/reports/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_name: `ARES Defender Security Audit (${selectedDevGptCase})`,
          language,
          baseline_count: scanResult ? scanResult.total_findings : 0,
          remaining_count: pipelineResponse ? pipelineResponse.final_remaining_findings.length : (verifyResult ? verifyResult.remaining_findings_count : 0),
          reduced_count: pipelineResponse ? (scanResult.total_findings - pipelineResponse.final_remaining_findings.length) : (verifyResult ? verifyResult.findings_reduced : 0),
          reduction_rate: pipelineResponse && pipelineResponse.attempts.length > 0 ? pipelineResponse.attempts[pipelineResponse.attempts.length - 1].reduction_rate : (verifyResult ? verifyResult.reduction_rate : 0),
          compiler_status: pipelineResponse && pipelineResponse.attempts.length > 0 ? pipelineResponse.attempts[pipelineResponse.attempts.length - 1].compiler : (verifyResult ? verifyResult.compiler_verification.status : "N/A"),
          findings: scanResult ? scanResult.findings : []
        })
      });
      if (res.ok) {
        const data = await res.json();
        setGeneratedReports(data);
        setReportFeedback(`Reports generated successfully: ${data.json_report}, ${data.csv_report}, ${data.html_report}`);
      } else {
        const err = await res.json().catch(() => ({}));
        setReportFeedback("Error generating report: " + (err.detail || res.statusText));
      }
    } catch (e) {
      setReportFeedback("Error generating report: " + e.message);
    } finally {
      setIsGeneratingReports(false);
    }
  };

  const handleDownloadReport = async (filename) => {
    if (!filename) return;
    try {
      const res = await fetch(`/api/reports/download/${filename}`);
      if (!res.ok) {
        throw new Error(`Failed to download report (${res.status} ${res.statusText})`);
      }
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert("Error downloading file: " + err.message);
    }
  };

  const currentAttempt = pipelineResponse?.attempts?.[activeAttemptIdx];

  return (
    <div className="flex h-screen bg-[#090d16] text-gray-100 overflow-hidden font-sans">
      {/* Sidebar Navigation */}
      {/* Sidebar Navigation */}
      <aside className="w-72 bg-[#0d131f] border-r border-[#1a2333] flex flex-col justify-between shrink-0">
        <div>
          {/* Logo */}
          <div className="p-5 border-b border-[#1a2333] flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-950">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-extrabold text-base tracking-tight text-white flex items-center gap-1.5">
                Secure Code AI
              </h1>
              <span className="text-[10px] uppercase font-bold tracking-wider text-sky-400 bg-sky-950/70 px-1.5 py-0.5 rounded border border-sky-800/50">
                Detection to Repair
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-3 space-y-1 text-sm font-medium">
            {[
              { id: 'repair', label: 'AI Repair & Verify', icon: Cpu, badge: 'Core' },
              { id: 'research', label: 'Research Insights', icon: FileCode, badge: '2026' },
              { id: 'audit', label: 'Auditor Workbench', icon: CheckCircle2, badge: 'Audit' },
              { id: 'dashboard', label: 'Executive Dashboard', icon: Layers },
              { id: 'analyzer', label: 'Static Analysis', icon: Terminal },
              { id: 'benchmark', label: 'LLM Benchmarks', icon: Flame },
              { id: 'cases', label: 'DevGPT Benchmark (48)', icon: FileCode },
              { id: 'reports', label: 'Audit Reports', icon: Download },
              { id: 'settings', label: 'System Diagnostics', icon: Server }
            ].map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg transition-all ${isActive
                    ? 'bg-sky-600/15 text-sky-400 border border-sky-500/30 font-semibold shadow-sm'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-[#141d2e]'
                    }`}
                >
                  <div className="flex items-center space-x-3 truncate">
                    <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-sky-400' : 'text-gray-500'}`} />
                    <span className="truncate whitespace-nowrap">{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="shrink-0 text-[9px] font-extrabold px-1.5 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-400/30 uppercase ml-2">
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Local Security Status Badge */}
        <div className="p-4 border-t border-[#1a2333] bg-[#0b101a]">
          <div className="flex items-center justify-between text-xs mb-1.5">
            <span className="text-gray-400 font-medium">Local Ollama</span>
            {systemHealth?.ollama_running ? (
              <span className="flex items-center text-emerald-400 font-semibold gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> Online
              </span>
            ) : (
              <span className="flex items-center text-amber-400 font-semibold gap-1">
                <span className="w-2 h-2 rounded-full bg-amber-400"></span> Offline
              </span>
            )}
          </div>
          <div className="text-[11px] text-gray-500 leading-tight">
            Zero Cloud APIs • Zero Keys • Sandboxed
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header */}
        <header className="h-16 bg-[#0d131f] border-b border-[#1a2333] px-6 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-4">
            <h2 className="text-base font-bold text-white tracking-wide flex items-center gap-2">
              {activeTab === 'repair' && (
                <>
                  <Cpu className="w-5 h-5 text-sky-400" />
                  <span>AI Repair & Verification Pipeline</span>
                </>
              )}
              {activeTab === 'research' && (
                <>
                  <FileCode className="w-5 h-5 text-indigo-400" />
                  <span>Research Paper Analysis (Belozerov et al., 2026) — RQ1, RQ2 & RQ3</span>
                </>
              )}
              {activeTab === 'audit' && (
                <>
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  <span>Manual Verification & Ground-Truth Auditor Workbench (Section 5)</span>
                </>
              )}
              {activeTab === 'dashboard' && 'Security Overview & Metrics'}
              {activeTab === 'analyzer' && 'Static Analysis & Finding Detection'}
              {activeTab === 'benchmark' && 'Comparative LLM Benchmark (DevGPT 48 Cases)'}
              {activeTab === 'cases' && 'DevGPT Benchmark Test Cases (48 Samples)'}
              {activeTab === 'reports' && 'Export Security Audit Reports'}
              {activeTab === 'settings' && 'Local System & Scanner Health'}
            </h2>
          </div>

          <div className="flex items-center space-x-3 text-xs">
            <button
              onClick={() => { fetchHealth(); fetchHistoricalBenchmark(); fetchBenchmarkCases(); }}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-[#162032] hover:bg-[#1e2b42] text-gray-300 border border-[#23334d] transition"
            >
              <RefreshCw className="w-3.5 h-3.5 text-sky-400" />
              <span>Refresh Environment</span>
            </button>
            <span className="px-2.5 py-1 rounded bg-emerald-950/60 border border-emerald-800/40 text-emerald-300 font-medium">
              100% Offline Sandbox
            </span>
          </div>
        </header>

        {/* Tab Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">

          {/* ======================================================== */}
          {/* TAB: DEDICATED AI REPAIR & VERIFY (Core Feature) */}
          {/* ======================================================== */}
          {activeTab === 'repair' && (
            <div className="space-y-6 max-w-7xl mx-auto">

              {/* Ollama Alert Bar if offline */}
              {!systemHealth?.ollama_running && (
                <div className="bg-amber-950/40 border border-amber-800/60 rounded-xl p-4 flex items-center justify-between text-xs text-amber-200 shadow-sm">
                  <div className="flex items-center space-x-3">
                    <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />
                    <div>
                      <span className="font-bold text-amber-300">Local AI Agent Notice (Ollama Offline): </span>
                      The local Ollama daemon is currently not running at <code className="bg-amber-900/60 px-1 py-0.5 rounded text-amber-200">http://localhost:11434</code>.
                      To activate local AI repair, launch Ollama in the background (<code>ollama serve</code>) with a coding model (e.g. <code>ollama pull qwen2.5-coder</code>).
                      No cloud APIs or API keys are required.
                    </div>
                  </div>
                  <span className="text-[11px] font-mono text-amber-400 bg-amber-950 px-2 py-1 rounded border border-amber-800">
                    OLLAMA_BASE_URL: localhost:11434
                  </span>
                </div>
              )}

              {/* End-to-End Workflow Diagram / Progress Map */}
              <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-3.5">
                <div className="flex flex-wrap items-center justify-between text-[11px] font-semibold text-gray-400 gap-2">
                  <div className="flex items-center gap-1.5 text-sky-400">
                    <FileCode className="w-3.5 h-3.5" />
                    <span>DevGPT Source ({filename})</span>
                  </div>
                  <ArrowRight className="w-3 h-3 text-gray-600" />
                  <div className="flex items-center gap-1.5 text-amber-400">
                    <Terminal className="w-3.5 h-3.5" />
                    <span>Static Scanners (Flawfinder / Cppcheck)</span>
                  </div>
                  <ArrowRight className="w-3 h-3 text-gray-600" />
                  <div className="flex items-center gap-1.5 text-rose-400">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>Finding ({selectedFinding ? selectedFinding.cwe : 'Select Flaw'})</span>
                  </div>
                  <ArrowRight className="w-3 h-3 text-gray-600" />
                  <div className="flex items-center gap-1.5 text-indigo-400">
                    <Cpu className="w-3.5 h-3.5" />
                    <span>Local AI Agent (Ollama)</span>
                  </div>
                  <ArrowRight className="w-3 h-3 text-gray-600" />
                  <div className="flex items-center gap-1.5 text-teal-400">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Compiler Check ({language === 'c' ? 'gcc' : (language === 'cpp' ? 'g++' : 'dotnet')})</span>
                  </div>
                  <ArrowRight className="w-3 h-3 text-gray-600" />
                  <div className="flex items-center gap-1.5 text-emerald-400">
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>Security Re-Scan & Retry Loop (Max 3)</span>
                  </div>
                </div>
              </div>

              {/* Control Panel: Test Case & Local AI Model Selector */}
              <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
                <div className="flex flex-wrap items-center gap-3">
                  {/* DevGPT Case Selector */}
                  <div className="flex items-center space-x-2">
                    <label className="text-xs font-bold text-gray-300 uppercase tracking-wide">Test Case:</label>
                    <select
                      value={selectedDevGptCase}
                      onChange={(e) => loadDevGptCase(e.target.value)}
                      disabled={caseLoading || isPipelineRunning}
                      className="bg-[#0e1422] border border-[#23334d] text-xs rounded-lg px-3 py-1.5 text-white font-mono outline-none focus:border-sky-500"
                    >
                      <optgroup label="DevGPT Real Benchmark Dataset (48 Samples)">
                        {benchmarkCases.map((c) => (
                          <option key={c.case_id} value={c.case_id}>
                            {c.case_id} — {c.target_file} ({c.primary_cwe})
                          </option>
                        ))}
                      </optgroup>
                      <option value="custom">Custom Code Snippet</option>
                    </select>
                  </div>

                  {/* Language Indicator */}
                  <span className="text-xs font-mono bg-[#182234] px-2.5 py-1.5 rounded text-sky-400 border border-[#23334d] uppercase font-bold">
                    {language}
                  </span>

                  {/* Local Model Selector */}
                  <div className="flex items-center space-x-2">
                    <label className="text-xs font-bold text-gray-300 uppercase tracking-wide">Local LLM:</label>
                    <select
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      disabled={isPipelineRunning}
                      className="bg-[#0e1422] border border-[#23334d] text-xs rounded-lg px-3 py-1.5 text-emerald-300 font-mono outline-none focus:border-emerald-500"
                    >
                      {systemHealth?.installed_models && systemHealth.installed_models.length > 0 ? (
                        systemHealth.installed_models.map((m) => (
                          <option key={m} value={m}>{m}</option>
                        ))
                      ) : (
                        <>
                          <option value="qwen2.5-coder">qwen2.5-coder (Default)</option>
                          <option value="deepseek-coder">deepseek-coder</option>
                          <option value="codellama">codellama</option>
                          <option value="starcoder2">starcoder2</option>
                        </>
                      )}
                    </select>
                  </div>

                  {/* Max Retries Selector */}
                  <div className="flex items-center space-x-2">
                    <label className="text-xs font-bold text-gray-300 uppercase tracking-wide">Max Retries:</label>
                    <select
                      value={maxRetries}
                      onChange={(e) => setMaxRetries(Number(e.target.value))}
                      disabled={isPipelineRunning}
                      className="bg-[#0e1422] border border-[#23334d] text-xs rounded-lg px-2.5 py-1.5 text-gray-200 font-mono outline-none focus:border-sky-500"
                    >
                      <option value={1}>1 Attempt</option>
                      <option value={2}>2 Attempts</option>
                      <option value={3}>3 Attempts (Recommended)</option>
                    </select>
                  </div>
                </div>

                {/* Primary Action Button */}
                <div className="flex items-center space-x-2">
                  <button
                    onClick={handleRunPipeline}
                    disabled={isPipelineRunning || !code.trim()}
                    className="flex items-center space-x-2 px-5 py-2.5 rounded-lg bg-gradient-to-r from-sky-600 via-indigo-600 to-emerald-600 hover:from-sky-500 hover:to-emerald-500 disabled:opacity-50 text-white text-xs font-extrabold transition shadow-lg shadow-sky-950"
                  >
                    {isPipelineRunning ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        <span>Executing Repair & Verification Loop...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4" />
                        <span>Run Autonomous AI Repair & Verification (Retry Loop)</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* TARGET SECURITY FINDING IDENTIFICATION CARD */}
              {selectedFinding && (
                <div className="bg-[#111827] border-2 border-rose-500/40 rounded-xl overflow-hidden shadow-lg">
                  <div className="bg-gradient-to-r from-rose-950/80 to-[#1e1322] px-5 py-3 border-b border-rose-500/30 flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="w-3 h-3 rounded-full bg-rose-500 animate-pulse"></span>
                      <h3 className="font-extrabold text-sm text-white flex items-center gap-2">
                        <span className="text-rose-400 font-mono uppercase bg-rose-900/60 px-2 py-0.5 rounded border border-rose-700">
                          {selectedFinding.cwe}
                        </span>
                        <span>{selectedFinding.title || selectedFinding.rule}</span>
                      </h3>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="px-2 py-0.5 rounded text-[11px] font-bold uppercase bg-rose-950 text-rose-300 border border-rose-800">
                        Severity: {selectedFinding.severity}
                      </span>
                      <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-[#141d2e] text-sky-300 border border-sky-800 font-mono">
                        Scanner: {selectedFinding.scanner}
                      </span>
                      <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-[#141d2e] text-amber-300 border border-amber-800 font-mono">
                        Line: {selectedFinding.line}
                      </span>
                    </div>
                  </div>

                  <div className="p-4 grid grid-cols-1 lg:grid-cols-2 gap-4 text-xs">
                    <div>
                      <div className="text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">Finding Description & Vulnerability Impact</div>
                      <p className="text-gray-300 leading-relaxed bg-[#0e1422] p-3 rounded-lg border border-[#1f2937]">
                        {selectedFinding.description}
                      </p>
                      <div className="mt-2.5 flex items-center gap-4 text-[11px] text-gray-400">
                        <span><strong>Rule:</strong> <code className="text-sky-300">{selectedFinding.rule}</code></span>
                        <span><strong>Target File:</strong> <code className="text-gray-300">{selectedFinding.file || filename}</code></span>
                      </div>
                    </div>

                    <div>
                      <div className="text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">Vulnerable Code Context</div>
                      <pre className="bg-[#070b12] text-rose-200/90 font-mono text-[11px] p-3 rounded-lg border border-[#1f2937] overflow-x-auto max-h-28">
                        <code>{selectedFinding.code_snippet || `Line ${selectedFinding.line}: ${selectedFinding.description}`}</code>
                      </pre>
                    </div>
                  </div>

                  {/* Multiple Findings Switcher */}
                  {scanResult && scanResult.findings && scanResult.findings.length > 1 && (
                    <div className="px-4 py-2 bg-[#0e1422] border-t border-[#1f2937] flex items-center space-x-2 overflow-x-auto text-xs">
                      <span className="text-[11px] text-gray-400 font-bold shrink-0">Switch Targeted Finding ({scanResult.findings.length}):</span>
                      {scanResult.findings.map((f, i) => (
                        <button
                          key={f.id || i}
                          onClick={() => setSelectedFinding(f)}
                          className={`px-2.5 py-1 rounded text-[11px] font-mono transition shrink-0 ${selectedFinding?.id === f.id
                            ? 'bg-rose-600 text-white font-bold'
                            : 'bg-[#182234] text-gray-400 hover:text-gray-200'
                            }`}
                        >
                          L{f.line} {f.cwe} ({f.scanner})
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* PIPELINE EXECUTION VERDICT BANNER */}
              {pipelineResponse && (
                <div className={`p-4 rounded-xl border flex items-center justify-between shadow-lg ${pipelineResponse.final_status === 'VERIFIED'
                  ? 'bg-emerald-950/70 border-emerald-600 text-emerald-200'
                  : (pipelineResponse.final_status === 'FAILED_SECURITY_RESCAN'
                    ? 'bg-amber-950/70 border-amber-600 text-amber-200'
                    : (pipelineResponse.final_status === 'COMPILATION_FAILED'
                      ? 'bg-rose-950/70 border-rose-600 text-rose-200'
                      : 'bg-red-950/70 border-red-600 text-red-200'))
                  }`}>
                  <div className="flex items-center space-x-3">
                    {pipelineResponse.final_status === 'VERIFIED' ? (
                      <CheckCircle2 className="w-7 h-7 text-emerald-400 shrink-0" />
                    ) : (
                      <AlertTriangle className="w-7 h-7 text-amber-400 shrink-0" />
                    )}
                    <div>
                      <div className="font-extrabold text-sm tracking-wide flex items-center gap-2">
                        <span>FINAL PIPELINE STATUS:</span>
                        <span className="px-2.5 py-0.5 rounded text-xs font-black uppercase tracking-wider bg-black/40 border">
                          {pipelineResponse.final_status}
                        </span>
                        <span className="text-xs font-normal text-gray-300">
                          (Completed in {pipelineResponse.total_attempts} attempt{pipelineResponse.total_attempts > 1 ? 's' : ''})
                        </span>
                      </div>
                      <p className="text-xs text-gray-300 mt-1">{pipelineResponse.summary}</p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <button
                      onClick={handleGenerateReport}
                      className="px-3.5 py-2 rounded-lg bg-[#141d2e] hover:bg-[#1e2b42] text-white text-xs font-bold border border-[#23334d] flex items-center gap-1.5 transition"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>Export Audit Report</span>
                    </button>
                  </div>
                </div>
              )}

              {/* RETRY LOOP ATTEMPT SELECTOR TABS */}
              {pipelineResponse && pipelineResponse.attempts && pipelineResponse.attempts.length > 0 && (
                <div className="flex items-center space-x-2 border-b border-[#1f2937] pb-2">
                  <span className="text-xs font-bold text-gray-400 uppercase tracking-wide mr-2 flex items-center gap-1">
                    <History className="w-4 h-4 text-sky-400" />
                    <span>Repair Attempts:</span>
                  </span>
                  {pipelineResponse.attempts.map((att, idx) => (
                    <button
                      key={att.attempt}
                      onClick={() => setActiveAttemptIdx(idx)}
                      className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-bold transition ${activeAttemptIdx === idx
                        ? 'bg-sky-600 text-white shadow'
                        : 'bg-[#111827] text-gray-400 hover:text-gray-200 border border-[#1f2937]'
                        }`}
                    >
                      <span>Attempt #{att.attempt}</span>
                      <span className={`text-[10px] px-1.5 py-0.2 rounded font-mono ${att.status === 'VERIFIED'
                        ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                        : 'bg-rose-950 text-rose-300 border border-rose-800'
                        }`}>
                        {att.status}
                      </span>
                    </button>
                  ))}
                </div>
              )}

              {/* ACTIVE ATTEMPT DETAILS: AI STRUCTURED ANALYSIS */}
              {currentAttempt && currentAttempt.ai_output && (
                <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-5 space-y-4">
                  <div className="flex items-center justify-between border-b border-[#1f2937] pb-3">
                    <div className="flex items-center space-x-2">
                      <Cpu className="w-5 h-5 text-indigo-400" />
                      <h4 className="font-extrabold text-sm text-white">
                        Local AI Agent Analysis (Attempt #{currentAttempt.attempt})
                      </h4>
                    </div>
                    <span className="text-xs font-mono text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800">
                      Model: {pipelineResponse.model_used}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                    <div className="bg-[#0e1422] p-3.5 rounded-lg border border-[#1f2937] space-y-1">
                      <div className="font-bold text-rose-400 uppercase tracking-wide text-[10px]">Identified Root Cause</div>
                      <p className="text-gray-300 leading-relaxed">{currentAttempt.ai_output.root_cause}</p>
                    </div>
                    <div className="bg-[#0e1422] p-3.5 rounded-lg border border-[#1f2937] space-y-1">
                      <div className="font-bold text-amber-400 uppercase tracking-wide text-[10px]">Security Impact</div>
                      <p className="text-gray-300 leading-relaxed">{currentAttempt.ai_output.security_impact}</p>
                    </div>
                    <div className="bg-[#0e1422] p-3.5 rounded-lg border border-[#1f2937] space-y-1">
                      <div className="font-bold text-emerald-400 uppercase tracking-wide text-[10px]">Repair Strategy</div>
                      <p className="text-gray-300 leading-relaxed">{currentAttempt.ai_output.repair_strategy}</p>
                    </div>
                  </div>

                  {currentAttempt.ai_output.changes && currentAttempt.ai_output.changes.length > 0 && (
                    <div className="bg-[#0e1422] p-3 rounded-lg border border-[#1f2937] text-xs">
                      <span className="font-bold text-sky-400 uppercase text-[10px] block mb-1">Specific Modifications Applied:</span>
                      <ul className="list-disc list-inside space-y-0.5 text-gray-300">
                        {currentAttempt.ai_output.changes.map((ch, idx) => (
                          <li key={idx}>{ch}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* SIDE-BY-SIDE CODE COMPARISON (🔴 Vulnerable vs 🟢 Repaired) */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* Original Code */}
                <div className="bg-[#111827] border border-[#1f2937] rounded-xl overflow-hidden flex flex-col h-[520px]">
                  <div className="px-4 py-2.5 bg-[#0e1422] border-b border-[#1f2937] flex items-center justify-between text-xs text-rose-400 font-mono">
                    <span className="flex items-center gap-1.5 font-bold">
                      <AlertTriangle className="w-4 h-4 text-rose-500" />
                      🔴 Original Vulnerable Baseline ({filename})
                    </span>
                    <span className="text-[11px] text-gray-500">
                      Baseline Findings: {scanResult?.total_findings || 0}
                    </span>
                  </div>
                  <pre className="flex-1 w-full bg-[#070b12] text-rose-100/90 font-mono text-xs p-4 overflow-auto leading-relaxed border-0 select-text">
                    <code>{code}</code>
                  </pre>
                </div>

                {/* AI Repaired Code */}
                <div className="bg-[#111827] border border-[#1f2937] rounded-xl overflow-hidden flex flex-col h-[520px]">
                  <div className="px-4 py-2.5 bg-[#0e1422] border-b border-[#1f2937] flex items-center justify-between text-xs text-emerald-400 font-mono">
                    <span className="flex items-center gap-1.5 font-bold">
                      <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                      🟢 AI Repaired Code {currentAttempt ? `(Attempt #${currentAttempt.attempt})` : ''}
                    </span>
                    {currentAttempt && (
                      <span className={`text-[11px] px-2 py-0.5 rounded font-bold ${currentAttempt.status === 'VERIFIED'
                        ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                        : 'bg-rose-950 text-rose-300 border border-rose-800'
                        }`}>
                        Remaining Findings: {currentAttempt.remaining_findings_count}
                      </span>
                    )}
                  </div>
                  <pre className="flex-1 w-full bg-[#070b12] text-emerald-100/90 font-mono text-xs p-4 overflow-auto leading-relaxed border-0 select-text">
                    <code>
                      {currentAttempt
                        ? currentAttempt.repaired_code
                        : (repairResult
                          ? repairResult.repaired_code
                          : "// Click 'Run Autonomous AI Repair & Verification' to synthesize and verify safe code.")}
                    </code>
                  </pre>
                </div>
              </div>

              {/* VERIFICATION RESULTS: COMPILER & SECURITY RE-SCAN */}
              {currentAttempt && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Compiler / Syntax Verification */}
                  <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-4 space-y-3">
                    <div className="flex items-center justify-between border-b border-[#1f2937] pb-2">
                      <div className="flex items-center space-x-2">
                        <Terminal className="w-4 h-4 text-sky-400" />
                        <h4 className="font-bold text-xs text-white uppercase tracking-wider">
                          Compiler / Syntax Verification
                        </h4>
                      </div>
                      <span className={`px-2.5 py-0.5 rounded text-xs font-black uppercase ${currentAttempt.compiler === 'PASS'
                        ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                        : (currentAttempt.compiler === 'FAIL'
                          ? 'bg-rose-950 text-rose-300 border border-rose-800'
                          : 'bg-gray-800 text-gray-300 border border-gray-700')
                        }`}>
                        {currentAttempt.compiler === 'PASS' && '✓ '}
                        {currentAttempt.compiler === 'FAIL' && '✗ '}
                        {currentAttempt.compiler}
                      </span>
                    </div>

                    <div className="text-xs space-y-1">
                      <div className="flex items-center justify-between text-gray-400 text-[11px]">
                        <span>Compiler: <strong>{language === 'c' ? 'gcc' : (language === 'cpp' ? 'g++' : 'dotnet/csc')}</strong></span>
                        <span>Exit Code: <strong>{currentAttempt.compiler_exit_code}</strong></span>
                      </div>
                      <pre className="bg-[#070b12] p-2.5 rounded font-mono text-[11px] text-gray-300 overflow-x-auto max-h-24">
                        <code>{currentAttempt.compiler_output || 'Compilation succeeded cleanly without errors.'}</code>
                      </pre>
                    </div>
                  </div>

                  {/* Security Re-Scan Results */}
                  <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-4 space-y-3">
                    <div className="flex items-center justify-between border-b border-[#1f2937] pb-2">
                      <div className="flex items-center space-x-2">
                        <Shield className="w-4 h-4 text-emerald-400" />
                        <h4 className="font-bold text-xs text-white uppercase tracking-wider">
                          Security Re-Scan
                        </h4>
                      </div>
                      <span className={`px-2.5 py-0.5 rounded text-xs font-black uppercase ${currentAttempt.targeted_finding_resolved
                        ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                        : 'bg-amber-950 text-amber-300 border border-amber-800'
                        }`}>
                        {currentAttempt.targeted_finding_resolved ? '✓ Target Finding Resolved' : '✗ Finding Still Present'}
                      </span>
                    </div>

                    <div className="grid grid-cols-4 gap-2 text-center text-xs">
                      <div className="bg-[#0e1422] p-2 rounded border border-[#1f2937]">
                        <div className="text-[10px] text-gray-400">Baseline</div>
                        <div className="font-bold text-rose-400">{currentAttempt.baseline_findings_count}</div>
                      </div>
                      <div className="bg-[#0e1422] p-2 rounded border border-[#1f2937]">
                        <div className="text-[10px] text-gray-400">Remaining</div>
                        <div className="font-bold text-amber-400">{currentAttempt.remaining_findings_count}</div>
                      </div>
                      <div className="bg-[#0e1422] p-2 rounded border border-[#1f2937]">
                        <div className="text-[10px] text-gray-400">Reduced</div>
                        <div className="font-bold text-emerald-400">+{currentAttempt.findings_reduced}</div>
                      </div>
                      <div className="bg-[#0e1422] p-2 rounded border border-[#1f2937]">
                        <div className="text-[10px] text-gray-400">Reduction</div>
                        <div className="font-bold text-sky-400">{currentAttempt.reduction_rate}%</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* AGENT RETRY FEEDBACK (if attempt failed and fed into next attempt) */}
              {currentAttempt && currentAttempt.feedback_to_ai && (
                <div className="bg-[#141d2e] border border-indigo-500/30 rounded-xl p-4 text-xs space-y-2">
                  <div className="flex items-center space-x-2 text-indigo-400 font-bold uppercase text-[11px]">
                    <RotateCcw className="w-4 h-4" />
                    <span>Iterative Feedback Injected into Local AI for Next Attempt:</span>
                  </div>
                  <pre className="bg-[#0a0f18] p-3 rounded font-mono text-[11px] text-indigo-200 overflow-x-auto">
                    <code>{currentAttempt.feedback_to_ai}</code>
                  </pre>
                </div>
              )}

              {/* Step-by-Step Manual Trigger Toolbar (Optional auxiliary controls) */}
              <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-4 flex flex-wrap items-center justify-between gap-3 text-xs">
                <span className="text-gray-400 font-semibold">Auxiliary Step-by-Step Controls:</span>
                <div className="flex items-center space-x-3">
                  <button
                    onClick={handleRepair}
                    disabled={isRepairing || isPipelineRunning}
                    className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-indigo-600/80 hover:bg-indigo-600 disabled:opacity-50 text-white font-bold transition"
                  >
                    <Cpu className="w-3.5 h-3.5" />
                    <span>{isRepairing ? 'Generating Repair...' : 'Single Step: AI Repair'}</span>
                  </button>

                  <button
                    onClick={handleVerify}
                    disabled={(!repairResult && !pipelineResponse) || isVerifying || isPipelineRunning}
                    className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-emerald-600/80 hover:bg-emerald-600 disabled:opacity-50 text-white font-bold transition"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>{isVerifying ? 'Verifying...' : 'Single Step: Verify (Compiler + Re-Scan)'}</span>
                  </button>
                </div>
              </div>

            </div>
          )}

          {/* ======================================================== */}
          {/* TAB 1: DASHBOARD OVERVIEW */}
          {/* ======================================================== */}
          {activeTab === 'dashboard' && (
            <div className="space-y-6">
              {/* Regenerate / Refresh Controls */}
              <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-4 flex flex-wrap items-center justify-between gap-3 text-xs">
                <div className="space-y-0.5">
                  <div className="font-bold text-white text-sm">Live Evaluation Dashboard</div>
                  <div className="text-gray-400">
                    All metrics computed from <code className="text-sky-300">evaluation_report.json</code> and audit DB — no hardcoded values.
                    {dashboardSummary?.live_flawfinder_ran === false && (
                      <span className="ml-2 text-amber-400 font-semibold">⚠ Live flawfinder scan not yet run.</span>
                    )}
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => { fetchDashboardSummary(); fetchDashboardCharts(); }}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#162032] hover:bg-[#1e2b42] text-gray-300 border border-[#23334d] transition"
                  >
                    <RefreshCw className="w-3.5 h-3.5 text-sky-400" />
                    <span>Refresh</span>
                  </button>
                  <button
                    onClick={handleRegenerateReport}
                    disabled={isRegenerating}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-700/60 hover:bg-amber-700 disabled:opacity-50 text-amber-200 border border-amber-700/50 transition font-semibold"
                  >
                    {isRegenerating ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5 fill-current" />}
                    <span>{isRegenerating ? 'Running Evaluator...' : 'Re-Run Evaluation (Fix Flawfinder)'}</span>
                  </button>
                </div>
              </div>

              {/* Regen Result */}
              {regenResult && (
                <div className={`p-3 rounded-lg border text-xs font-mono ${regenResult.status === 'completed' ? 'bg-emerald-950/40 border-emerald-700 text-emerald-300' : 'bg-rose-950/40 border-rose-700 text-rose-300'}`}>
                  <div className="font-bold mb-1">Evaluation Result: {regenResult.status?.toUpperCase()}</div>
                  {regenResult.report_summary && (
                    <div className="text-gray-300 space-y-0.5">
                      <div>Total Cases: <strong>{regenResult.report_summary.total_cases}</strong></div>
                      <div>Total Recorded Findings: <strong>{regenResult.report_summary.total_orig_findings}</strong></div>
                      <div>Live Flawfinder Hits (Original): <strong className="text-rose-300">{regenResult.report_summary.total_orig_flawfinder_hits}</strong></div>
                    </div>
                  )}
                  {regenResult.note && <div className="mt-1 text-gray-400">{regenResult.note}</div>}
                  {regenResult.message && <div className="mt-1">{regenResult.message}</div>}
                </div>
              )}

              {/* Summary Stat Cards — ALL DYNAMIC */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-[#111827] border border-[#1f2937] p-5 rounded-xl space-y-1">
                  <div className="flex items-center justify-between text-gray-400 text-xs font-semibold uppercase">
                    <span>DevGPT Benchmark</span>
                    <FileCode className="w-4 h-4 text-sky-400" />
                  </div>
                  <div className="text-2xl font-black text-white">
                    {dashboardSummary?.total_dataset_cases ?? benchmarkCases.length ?? '—'} Cases
                  </div>
                  <p className="text-[11px] text-gray-500">
                    {dashboardSummary?.cases_with_source_code != null
                      ? `${dashboardSummary.cases_with_source_code} with source code`
                      : 'C, C++, and C# real samples'}
                  </p>
                </div>

                <div className="bg-[#111827] border border-[#1f2937] p-5 rounded-xl space-y-1">
                  <div className="flex items-center justify-between text-gray-400 text-xs font-semibold uppercase">
                    <span>Baseline Flawfinder Hits</span>
                    <AlertTriangle className="w-4 h-4 text-rose-400" />
                  </div>
                  <div className="text-2xl font-black text-rose-400">
                    {dashboardSummary?.baseline_flawfinder_hits != null
                      ? (dashboardSummary.baseline_flawfinder_hits > 0
                          ? `${dashboardSummary.baseline_flawfinder_hits} Hits`
                          : 'Not Scanned')
                      : '—'}
                  </div>
                  <p className="text-[11px] text-gray-500">
                    {dashboardSummary?.live_flawfinder_ran
                      ? `Recorded findings: ${dashboardSummary.dataset_recorded_findings}`
                      : 'Click Re-Run Evaluation to scan'}
                  </p>
                </div>

                <div className="bg-[#111827] border border-[#1f2937] p-5 rounded-xl space-y-1">
                  <div className="flex items-center justify-between text-gray-400 text-xs font-semibold uppercase">
                    <span>Active Scanners</span>
                    <Terminal className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div className="text-2xl font-black text-emerald-400">
                    {systemHealth?.scanners?.filter(s => s.installed).length ?? '—'} Active
                  </div>
                  <p className="text-[11px] text-gray-500">
                    {systemHealth?.scanners?.filter(s => s.installed).map(s => s.name).join(', ') || 'No scanners detected'}
                  </p>
                </div>

                <div className="bg-[#111827] border border-[#1f2937] p-5 rounded-xl space-y-1">
                  <div className="flex items-center justify-between text-gray-400 text-xs font-semibold uppercase">
                    <span>Best Reduction Rate</span>
                    <Cpu className="w-4 h-4 text-indigo-400" />
                  </div>
                  <div className="text-xl font-bold text-indigo-300 truncate">
                    {dashboardSummary?.best_flawfinder_reduction ?? 'N/A'}
                  </div>
                  <p className="text-[11px] text-gray-500">
                    {dashboardSummary?.live_flawfinder_ran ? 'Live flawfinder comparison' : 'Run evaluation first'}
                  </p>
                </div>
              </div>

              {/* Empty state if no evaluation data */}
              {!dashboardSummary?.evaluation_ran && (
                <div className="bg-[#0e1422] border border-dashed border-[#23334d] rounded-xl p-10 flex flex-col items-center text-center gap-3">
                  <Layers className="w-10 h-10 text-gray-600" />
                  <div className="text-gray-400 font-semibold text-sm">No Evaluation Data</div>
                  <p className="text-xs text-gray-500 max-w-md">
                    No evaluation_report.json found or it has no cases. Click <strong>Re-Run Evaluation</strong> above to generate real baseline metrics.
                  </p>
                </div>
              )}

              {/* Quick Launch Banner */}
              <div className="bg-gradient-to-r from-sky-950/70 via-[#131b2e] to-indigo-950/70 border border-sky-800/40 rounded-xl p-6 flex items-center justify-between">
                <div className="space-y-1">
                  <h3 className="font-extrabold text-base text-white">Start Autonomous AI Repair & Verification</h3>
                  <p className="text-xs text-gray-300 max-w-xl">
                    Run the complete loop: parse real DevGPT vulnerability samples, detect flaws via static scanners,
                    synthesize minimal safe code using local Ollama, compile with gcc/g++, and re-scan with automatic 3-attempt retry.
                  </p>
                </div>
                <button
                  onClick={() => setActiveTab('repair')}
                  className="px-5 py-2.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-bold text-xs shadow-lg transition flex items-center gap-2 shrink-0"
                >
                  <span>Open AI Repair & Verify</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>

              {/* Historical Model Leaderboard — DYNAMIC from dashboardCharts */}
              <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="font-bold text-sm text-white flex items-center gap-2">
                    <Flame className="w-4 h-4 text-amber-400" />
                    <span>DevGPT Benchmark Leaderboard (Historical LLM Models)</span>
                  </h3>
                  <span className="text-xs text-gray-400 font-mono">
                    Baseline: {dashboardSummary?.baseline_flawfinder_hits > 0
                      ? `${dashboardSummary.baseline_flawfinder_hits} Live Flawfinder Hits`
                      : dashboardSummary?.dataset_recorded_findings > 0
                        ? `${dashboardSummary.dataset_recorded_findings} Recorded Findings (live scan pending)`
                        : 'No baseline yet'}
                  </span>
                </div>

                {/* Show note about data source */}
                {dashboardSummary?.baseline_flawfinder_hits === 0 && (
                  <div className="bg-amber-950/30 border border-amber-800/40 rounded-lg p-3 text-xs text-amber-300">
                    ⚠ Live flawfinder baseline is 0. This means the evaluator was previously run with a broken flawfinder command.
                    Click <strong>Re-Run Evaluation</strong> to get real results. Reduction rates below show N/A until baseline is populated.
                  </div>
                )}

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs text-gray-300">
                    <thead className="bg-[#0e1422] text-gray-400 uppercase text-[11px] font-semibold border-b border-[#1f2937]">
                      <tr>
                        <th className="px-4 py-3">Rank</th>
                        <th className="px-4 py-3">Model</th>
                        <th className="px-4 py-3">Baseline</th>
                        <th className="px-4 py-3">Remaining Flaws</th>
                        <th className="px-4 py-3">Flaws Eliminated</th>
                        <th className="px-4 py-3">Reduction Rate</th>
                        <th className="px-4 py-3">Compiled OK</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#1b2536]">
                      {dashboardCharts?.model_comparison_chart?.length > 0
                        ? dashboardCharts.model_comparison_chart
                            .sort((a, b) => (b.fixed_cases || 0) - (a.fixed_cases || 0))
                            .map((m, idx) => (
                              <tr key={m.model} className="hover:bg-[#141d2e] transition">
                                <td className="px-4 py-3 font-bold text-amber-400">
                                  {idx === 0 ? '🥇' : idx === 1 ? '🥈' : '🥉'} {idx + 1}
                                </td>
                                <td className="px-4 py-3 font-mono font-bold text-white">{m.model}</td>
                                <td className="px-4 py-3">{m.baseline > 0 ? m.baseline : 'N/A'}</td>
                                <td className="px-4 py-3 font-bold text-emerald-400">
                                  {m.baseline > 0 ? m.remaining : 'N/A'}
                                </td>
                                <td className="px-4 py-3 font-bold text-sky-400">
                                  {m.baseline > 0 ? `+${m.reduced}` : 'N/A'}
                                </td>
                                <td className="px-4 py-3 font-bold text-sky-400">
                                  {m.reduction_rate != null ? `${m.reduction_rate}%` : 'N/A'}
                                </td>
                                <td className="px-4 py-3">
                                  {m.compile_ok} / {dashboardSummary?.total_dataset_cases ?? 48}
                                </td>
                              </tr>
                            ))
                        : (
                          <tr>
                            <td colSpan={7} className="px-4 py-6 text-center text-gray-500">
                              No evaluation data available. Run Re-Run Evaluation to generate results.
                            </td>
                          </tr>
                        )
                      }
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Scanner Usage Chart */}
              {dashboardCharts?.scanner_chart?.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-5 space-y-3">
                    <h3 className="font-bold text-sm text-white flex items-center gap-2">
                      <Terminal className="w-4 h-4 text-sky-400" />
                      <span>Scanner Usage Across Dataset</span>
                    </h3>
                    <div className="space-y-2">
                      {dashboardCharts.scanner_chart.map(s => (
                        <div key={s.scanner} className="flex items-center gap-3 text-xs">
                          <span className="w-28 text-gray-300 font-mono truncate">{s.scanner}</span>
                          <div className="flex-1 bg-[#0e1422] rounded-full h-2 overflow-hidden">
                            <div
                              className="bg-sky-500 h-full rounded-full"
                              style={{ width: `${Math.round((s.cases / (dashboardSummary?.total_dataset_cases || 48)) * 100)}%` }}
                            />
                          </div>
                          <span className="text-gray-400 w-16 text-right">{s.cases} cases</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-5 space-y-3">
                    <h3 className="font-bold text-sm text-white flex items-center gap-2">
                      <Code2 className="w-4 h-4 text-indigo-400" />
                      <span>Language Distribution</span>
                    </h3>
                    <div className="space-y-2">
                      {dashboardCharts?.language_chart?.map(l => (
                        <div key={l.language} className="flex items-center gap-3 text-xs">
                          <span className="w-20 text-gray-300 font-mono uppercase">{l.language}</span>
                          <div className="flex-1 bg-[#0e1422] rounded-full h-2 overflow-hidden">
                            <div
                              className="bg-indigo-500 h-full rounded-full"
                              style={{ width: `${Math.round((l.cases / (dashboardSummary?.total_dataset_cases || 48)) * 100)}%` }}
                            />
                          </div>
                          <span className="text-gray-400 w-16 text-right">{l.cases} cases</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Audit Summary */}
              {dashboardSummary?.manual_audit?.total_decisions_logged > 0 && (
                <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-5 space-y-3">
                  <h3 className="font-bold text-sm text-white flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span>Manual Audit Workbench Summary</span>
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                    <div className="bg-[#0e1422] p-3 rounded-lg text-center">
                      <div className="text-gray-400">Total Decisions</div>
                      <div className="text-xl font-black text-white mt-1">{dashboardSummary.manual_audit.total_decisions_logged}</div>
                    </div>
                    <div className="bg-[#0e1422] p-3 rounded-lg text-center">
                      <div className="text-gray-400">Cases Reviewed</div>
                      <div className="text-xl font-black text-emerald-400 mt-1">{dashboardSummary.manual_audit.distinct_cases_reviewed}</div>
                    </div>
                    {Object.entries(dashboardSummary.manual_audit.verdicts || {}).map(([v, c]) => (
                      <div key={v} className="bg-[#0e1422] p-3 rounded-lg text-center">
                        <div className="text-gray-400 truncate">{v.replace(/_/g, ' ')}</div>
                        <div className="text-xl font-black text-sky-400 mt-1">{c}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            </div>
          )}


          {/* ======================================================== */}
          {/* TAB 2: CODE ANALYZER */}
          {/* ======================================================== */}
          {activeTab === 'analyzer' && (
            <div className="space-y-4">
              <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-4 flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-bold text-gray-300 uppercase">Language:</span>
                  {['c', 'cpp', 'csharp', 'python', 'javascript'].map((lang) => (
                    <button
                      key={lang}
                      onClick={() => handleLanguageChange(lang)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold uppercase transition ${language === lang
                        ? 'bg-sky-600 text-white shadow'
                        : 'bg-[#162032] text-gray-400 hover:text-gray-200'
                        }`}
                    >
                      {lang}
                    </button>
                  ))}
                </div>

                <div className="flex items-center space-x-3">
                  <button
                    onClick={handleRunScan}
                    disabled={isScanning}
                    className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-bold transition shadow-lg shadow-emerald-950"
                  >
                    {isScanning ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        <span>Running Scanners...</span>
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4 fill-white" />
                        <span>Scan Code for Vulnerabilities</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* Editor */}
                <div className="bg-[#111827] border border-[#1f2937] rounded-xl overflow-hidden flex flex-col h-[520px]">
                  <div className="px-4 py-2.5 bg-[#0e1422] border-b border-[#1f2937] flex items-center justify-between text-xs text-gray-400 font-mono">
                    <span className="flex items-center gap-2">
                      <Code2 className="w-4 h-4 text-sky-400" />
                      source.{language}
                    </span>
                    <span className="text-[11px] text-gray-500">Edit or paste source code</span>
                  </div>
                  <textarea
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    className="flex-1 w-full bg-[#070b12] text-gray-200 font-mono text-xs p-4 outline-none resize-none leading-relaxed border-0 select-text"
                    spellCheck="false"
                  />
                </div>

                {/* Findings */}
                <div className="bg-[#111827] border border-[#1f2937] rounded-xl overflow-hidden flex flex-col h-[520px]">
                  <div className="px-4 py-2.5 bg-[#0e1422] border-b border-[#1f2937] flex items-center justify-between text-xs text-gray-400">
                    <span className="font-bold text-gray-200 flex items-center gap-1.5">
                      <AlertTriangle className="w-4 h-4 text-amber-400" />
                      Scanner Findings ({scanResult?.total_findings || 0})
                    </span>
                    {scanResult && (
                      <span className="text-[11px] text-gray-500">
                        Scanners: {scanResult.scanners_executed.join(', ') || 'none'}
                      </span>
                    )}
                  </div>

                  <div className="flex-1 overflow-y-auto p-3 space-y-2.5">
                    {!scanResult && (
                      <div className="h-full flex flex-col items-center justify-center text-center p-6 text-gray-500 text-xs">
                        <Terminal className="w-10 h-10 mb-2 text-gray-600" />
                        <p className="font-semibold text-gray-400">No scan executed yet</p>
                        <p className="mt-1">Click "Scan Code for Vulnerabilities" to run local static security analysis.</p>
                      </div>
                    )}

                    {scanResult && scanResult.findings.length === 0 && (
                      <div className="h-full flex flex-col items-center justify-center text-center p-6 text-emerald-400 text-xs">
                        <CheckCircle2 className="w-10 h-10 mb-2 text-emerald-500" />
                        <p className="font-bold text-sm">Clean! No Vulnerabilities Flagged</p>
                        <p className="mt-1 text-gray-400">The installed scanners detected 0 security violations in this snippet.</p>
                      </div>
                    )}

                    {scanResult && scanResult.findings.map((f, idx) => (
                      <div
                        key={f.id || idx}
                        onClick={() => handleExplain(f)}
                        className={`p-3 rounded-lg border text-xs cursor-pointer transition ${selectedFinding?.id === f.id
                          ? 'bg-[#192437] border-sky-500/60 shadow'
                          : 'bg-[#0e1422] border-[#1d2738] hover:border-gray-600'
                          }`}
                      >
                        <div className="flex items-center justify-between mb-1.5">
                          <span className="font-bold text-gray-200 flex items-center gap-1.5">
                            <span className={`w-2 h-2 rounded-full ${f.severity === 'critical' ? 'bg-rose-500' : (f.severity === 'high' ? 'bg-orange-500' : 'bg-amber-400')
                              }`}></span>
                            Line {f.line}: {f.title}
                          </span>
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-rose-950/80 text-rose-300 border border-rose-800/40">
                            {f.cwe}
                          </span>
                        </div>
                        <p className="text-gray-400 text-[11px] line-clamp-2">{f.description}</p>
                        <div className="mt-2 flex items-center justify-between text-[10px] text-gray-500 font-mono">
                          <span>Scanner: {f.scanner} ({f.rule})</span>
                          <span className="text-sky-400 flex items-center gap-1">Click to analyze <ArrowRight className="w-3 h-3" /></span>
                        </div>
                      </div>
                    ))}
                  </div>

                  {scanResult && scanResult.total_findings > 0 && (
                    <div className="p-3 bg-[#0e1422] border-t border-[#1f2937] flex justify-end">
                      <button
                        onClick={() => setActiveTab('repair')}
                        className="flex items-center space-x-2 px-3.5 py-1.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold transition"
                      >
                        <span>Proceed to AI Repair & Verification</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* ======================================================== */}
          {/* TAB: RESEARCH PAPER & EMPIRICAL METHODOLOGY (RQ1, RQ2, RQ3) */}
          {/* ======================================================== */}
          {activeTab === 'research' && (
            <div className="space-y-6 max-w-7xl mx-auto">
              {/* Academic Publication Banner */}
              <div className="relative overflow-hidden bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-indigo-900/60 rounded-2xl p-6 shadow-xl">
                <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-indigo-500/20 text-indigo-300 border border-indigo-400/30">
                        Empirical Software Engineering (2026) 31:93
                      </span>
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-emerald-500/20 text-emerald-300 border border-emerald-400/30">
                        Peer-Reviewed Ground Truth
                      </span>
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-sky-500/20 text-sky-300 border border-sky-400/30">
                        DOI: 10.1007/s10664-026-10812-8
                      </span>
                    </div>
                    <h2 className="text-xl md:text-2xl font-black text-white tracking-tight">
                      Secure coding with AI – from detection to repair
                    </h2>
                    <p className="text-xs text-gray-300">
                      Vladislav Belozerov, Peter J. Barclay, and Ashkan Sami • <span className="text-indigo-300 font-medium">Edinburgh Napier University & Shiraz University</span>
                    </p>
                  </div>
                  <div className="shrink-0 flex md:flex-col items-center md:items-end justify-between gap-2 border-t md:border-t-0 md:border-l border-indigo-800/40 pt-3 md:pt-0 md:pl-6 text-right">
                    <div className="text-[11px] text-gray-400">Evaluated Dataset:</div>
                    <div className="text-sm font-bold font-mono text-emerald-400">2,315 DevGPT Files</div>
                    <div className="text-[10px] text-gray-400">48 Confirmed Vulnerable Files (56 Flaws)</div>
                  </div>
                </div>
              </div>

              {/* RQ Switcher Bar */}
              <div className="flex items-center space-x-2 border-b border-[#1f2937] pb-3">
                {[
                  { id: 'rq1', label: 'RQ1: Security of GPT Code', desc: 'Dataset & CWE Distribution' },
                  { id: 'rq2', label: 'RQ2: LLM Detection & Repair', desc: 'Model Benchmark Comparison' },
                  { id: 'rq3', label: 'RQ3: User vs. GPT Provenance', desc: 'Code Origin Vulnerability Bias' }
                ].map((rq) => (
                  <button
                    key={rq.id}
                    onClick={() => setSelectedRq(rq.id)}
                    className={`px-4 py-2.5 rounded-xl text-left transition ${selectedRq === rq.id
                      ? 'bg-indigo-600/20 border border-indigo-500/40 text-white shadow'
                      : 'bg-[#111827] border border-[#1f2937] text-gray-400 hover:text-gray-200'
                      }`}
                  >
                    <div className="text-xs font-bold">{rq.label}</div>
                    <div className="text-[10px] text-gray-500">{rq.desc}</div>
                  </button>
                ))}
              </div>

              {/* RQ1 VIEW */}
              {selectedRq === 'rq1' && (
                <div className="space-y-6">
                  {/* Summary Metric Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-4">
                      <div className="text-xs text-gray-400">Total Analyzed Files</div>
                      <div className="text-2xl font-black text-white mt-1">2,315</div>
                      <div className="text-[10px] text-gray-500 mt-1">325 C • 990 C++ • 1,000 C#</div>
                    </div>
                    <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-4">
                      <div className="text-xs text-gray-400">Candidate Files Flagged</div>
                      <div className="text-2xl font-black text-amber-400 mt-1">114</div>
                      <div className="text-[10px] text-gray-500 mt-1">Flagged by ≥1 static tool</div>
                    </div>
                    <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-4">
                      <div className="text-xs text-gray-400">Manually Confirmed Flaws</div>
                      <div className="text-2xl font-black text-rose-400 mt-1">56</div>
                      <div className="text-[10px] text-gray-500 mt-1">In 48 files across 23 CWE types</div>
                    </div>
                    <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-4">
                      <div className="text-xs text-gray-400">Triangulated Scanners</div>
                      <div className="text-2xl font-black text-sky-400 mt-1">4 Tools</div>
                      <div className="text-[10px] text-gray-500 mt-1">Flawfinder, Semgrep, Snyk, Cppcheck</div>
                    </div>
                  </div>

                  {/* Language Vulnerability Density (Table 9 in Paper) */}
                  <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-5">
                    <h3 className="font-bold text-sm text-white mb-3 flex items-center gap-2">
                      <Terminal className="w-4 h-4 text-sky-400" />
                      <span>Language Vulnerability Density (Table 9 of Belozerov et al.)</span>
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="p-4 rounded-lg bg-rose-950/20 border border-rose-900/40">
                        <div className="flex justify-between items-center mb-1">
                          <span className="font-bold text-rose-400">C Language</span>
                          <span className="text-[10px] text-rose-300 font-mono">Least Secure</span>
                        </div>
                        <div className="text-xl font-bold text-white">10.4 LOC / Detection</div>
                        <div className="text-[11px] text-gray-400 mt-1">325 files • 7,449 LOC • 716 scanner detections</div>
                      </div>
                      <div className="p-4 rounded-lg bg-amber-950/20 border border-amber-900/40">
                        <div className="flex justify-between items-center mb-1">
                          <span className="font-bold text-amber-400">C++ Language</span>
                          <span className="text-[10px] text-amber-300 font-mono">Intermediate</span>
                        </div>
                        <div className="text-xl font-bold text-white">83.8 LOC / Detection</div>
                        <div className="text-[11px] text-gray-400 mt-1">990 files • 19,869 LOC • 237 scanner detections</div>
                      </div>
                      <div className="p-4 rounded-lg bg-emerald-950/20 border border-emerald-900/40">
                        <div className="flex justify-between items-center mb-1">
                          <span className="font-bold text-emerald-400">C# Language</span>
                          <span className="text-[10px] text-emerald-300 font-mono">Most Secure</span>
                        </div>
                        <div className="text-xl font-bold text-white">2,937.5 LOC / Detection</div>
                        <div className="text-[11px] text-gray-400 mt-1">1,000 files • 17,625 LOC • 6 scanner detections</div>
                      </div>
                    </div>
                  </div>

                  {/* CWE Top-25 Distribution Table (Table 8 in Paper) */}
                  <div className="bg-[#111827] border border-[#1f2937] rounded-xl overflow-hidden">
                    <div className="px-5 py-4 bg-[#141d2e] border-b border-[#1f2937] flex items-center justify-between">
                      <h3 className="font-bold text-sm text-white">CWE Distribution of Confirmed Vulnerabilities (Table 8)</h3>
                      <span className="text-xs text-gray-400">66 total occurrences across 23 CWE types</span>
                    </div>
                    <div className="overflow-x-auto max-h-80 overflow-y-auto">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-[#0b101a] text-gray-400 text-[11px] uppercase tracking-wider sticky top-0">
                          <tr>
                            <th className="px-4 py-2.5">CWE ID</th>
                            <th className="px-4 py-2.5">Weakness Description</th>
                            <th className="px-4 py-2.5 text-center">Occurrences</th>
                            <th className="px-4 py-2.5 text-center">CWE Top 25 Rank</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-[#1f2937] text-gray-300">
                          {(paperData?.cwe_distribution || []).map((row, idx) => (
                            <tr key={idx} className="hover:bg-[#162032] transition">
                              <td className="px-4 py-2 font-mono font-bold text-indigo-400">{row.cwe}</td>
                              <td className="px-4 py-2">{row.description}</td>
                              <td className="px-4 py-2 text-center font-bold text-white">{row.count}</td>
                              <td className="px-4 py-2 text-center">
                                {row.top_25_rank ? (
                                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-950 text-rose-300 border border-rose-800">
                                    Rank #{row.top_25_rank}
                                  </span>
                                ) : (
                                  <span className="text-gray-500 text-[11px]">—</span>
                                )}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

              {/* RQ2 VIEW */}
              {selectedRq === 'rq2' && (
                <div className="space-y-6">
                  {/* Paper Reference Results vs Local Measured Results */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Published Paper Reference */}
                    <div className="bg-[#111827] border border-indigo-900/50 rounded-xl p-5 space-y-4">
                      <div className="flex items-center justify-between">
                        <h4 className="font-bold text-sm text-white flex items-center gap-2">
                          <Flame className="w-4 h-4 text-indigo-400" />
                          <span>Published Paper Findings (Table 12)</span>
                        </h4>
                        <span className="text-[10px] text-indigo-300 bg-indigo-950 px-2 py-0.5 rounded border border-indigo-800">
                          Belozerov et al. (2026)
                        </span>
                      </div>
                      <p className="text-xs text-gray-400">
                        September 2025 experiment evaluating 56 confirmed vulnerabilities across 48 DevGPT files.
                      </p>

                      <div className="space-y-3">
                        <div className="p-3 bg-[#0d131f] rounded-lg border border-[#1a2333]">
                          <div className="flex justify-between items-center text-xs mb-1">
                            <span className="font-bold text-white">GPT-4.1 (2025-04-14)</span>
                            <span className="text-emerald-400 font-mono font-bold">Detected: 82.14% • Repaired: 75.00%</span>
                          </div>
                          <div className="w-full bg-gray-800 h-2 rounded-full overflow-hidden flex">
                            <div className="bg-emerald-500 h-full" style={{ width: '82.14%' }}></div>
                          </div>
                          <div className="text-[10px] text-gray-500 mt-1">Detected 46/56 • Fixed 42/56 vulnerabilities</div>
                        </div>

                        <div className="p-3 bg-[#0d131f] rounded-lg border border-[#1a2333]">
                          <div className="flex justify-between items-center text-xs mb-1">
                            <span className="font-bold text-white">GPT-5 (2025-08-07)</span>
                            <span className="text-emerald-400 font-mono font-bold">Detected: 78.57% • Repaired: 78.57%</span>
                          </div>
                          <div className="w-full bg-gray-800 h-2 rounded-full overflow-hidden flex">
                            <div className="bg-sky-500 h-full" style={{ width: '78.57%' }}></div>
                          </div>
                          <div className="text-[10px] text-gray-500 mt-1">Detected 44/56 • Fixed 44/56 vulnerabilities</div>
                        </div>

                        <div className="p-3 bg-[#0d131f] rounded-lg border border-[#1a2333]">
                          <div className="flex justify-between items-center text-xs mb-1">
                            <span className="font-bold text-white">Claude Opus 4.1 (2025-08-05)</span>
                            <span className="text-emerald-400 font-mono font-bold">Detected: 80.36% • Repaired: 76.79%</span>
                          </div>
                          <div className="w-full bg-gray-800 h-2 rounded-full overflow-hidden flex">
                            <div className="bg-indigo-500 h-full" style={{ width: '80.36%' }}></div>
                          </div>
                          <div className="text-[10px] text-gray-500 mt-1">Detected 45/56 • Fixed 43/56 vulnerabilities</div>
                        </div>

                        <div className="p-3 bg-[#0d131f] rounded-lg border border-[#1a2333]">
                          <div className="flex justify-between items-center text-xs mb-1">
                            <span className="font-bold text-amber-300">GPT-4o (Oct 2024 Experiment)</span>
                            <span className="text-amber-400 font-mono font-bold">Detected: 56.25% • Repaired: 53.13%</span>
                          </div>
                          <div className="w-full bg-gray-800 h-2 rounded-full overflow-hidden flex">
                            <div className="bg-amber-500 h-full" style={{ width: '56.25%' }}></div>
                          </div>
                          <div className="text-[10px] text-gray-500 mt-1">Detected 18/32 • Fixed 17/32 vulnerabilities (snapshot_20231012)</div>
                        </div>
                      </div>
                    </div>

                    {/* Local Measured Execution Metrics */}
                    <div className="bg-[#111827] border border-emerald-900/50 rounded-xl p-5 space-y-4">
                      <div className="flex items-center justify-between">
                        <h4 className="font-bold text-sm text-white flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                          <span>Locally Measured Execution Records</span>
                        </h4>
                        <span className="text-[10px] text-emerald-300 bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800">
                          Live Environment
                        </span>
                      </div>
                      <p className="text-xs text-gray-400">
                        Derived from the 48 DevGPT case files and live verification re-scan executions.
                      </p>

                      <div className="space-y-3">
                        {Object.entries(liveMetrics?.models_evaluated || {}).map(([mName, mStats]) => (
                          <div key={mName} className="p-3 bg-[#0d131f] rounded-lg border border-[#1a2333]">
                            <div className="flex justify-between items-center text-xs mb-1">
                              <span className="font-bold text-white font-mono">{mName.split('-')[0]}</span>
                              <span className="text-sky-400 font-mono font-bold">Fix Rate: {mStats.repair_success_rate}%</span>
                            </div>
                            <div className="grid grid-cols-3 gap-2 mt-2 text-[11px] text-gray-400">
                              <div>Compile OK: <strong className="text-emerald-400">{mStats.compilation_success_rate}%</strong></div>
                              <div>Fixed Samples: <strong className="text-white">{mStats.fixed_cases}/48</strong></div>
                              <div>Residual Hits: <strong className="text-amber-400">{mStats.remaining_hits}</strong></div>
                            </div>
                          </div>
                        ))}
                      </div>

                      <div className="p-3 bg-indigo-950/20 border border-indigo-900/40 rounded-lg text-xs text-gray-300">
                        <strong className="text-indigo-400">Scientific Distinction:</strong> The paper's human-curated repair rate reflects whether the root cause was fixed without regression. Local automated metrics evaluate static scanner flaw reduction and compiler syntax validation.
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* RQ3 VIEW */}
              {selectedRq === 'rq3' && (
                <div className="space-y-6">
                  <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-5">
                    <h3 className="font-bold text-sm text-white mb-2">
                      Vulnerability Origin: User Prompts vs. GPT Responses (Tables 17 & 18)
                    </h3>
                    <p className="text-xs text-gray-400 mb-4">
                      Investigating whether vulnerabilities originate primarily from developer-provided inputs or AI code generation.
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="p-5 bg-gradient-to-br from-[#121929] to-[#0c121d] border border-blue-900/40 rounded-xl space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-xs font-bold text-blue-400 uppercase tracking-wider">User-Provided Code</span>
                          <span className="text-sm font-black text-white">44.64%</span>
                        </div>
                        <div className="text-3xl font-black text-white">25 Vulnerabilities</div>
                        <p className="text-xs text-gray-400">Occurred across 23 DevGPT discussion files.</p>
                        <div className="text-[11px] text-emerald-400 font-medium">
                          Model Fix Rate: <strong className="text-white">88% (GPT-4.1) • 84% (GPT-5) • 76% (Claude)</strong>
                        </div>
                      </div>

                      <div className="p-5 bg-gradient-to-br from-[#191429] to-[#0d0c1d] border border-purple-900/40 rounded-xl space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-xs font-bold text-purple-400 uppercase tracking-wider">GPT-Generated Code</span>
                          <span className="text-sm font-black text-white">55.36%</span>
                        </div>
                        <div className="text-3xl font-black text-white">31 Vulnerabilities</div>
                        <p className="text-xs text-gray-400">Occurred across 25 DevGPT discussion files.</p>
                        <div className="text-[11px] text-sky-400 font-medium">
                          Model Fix Rate: <strong className="text-white">74.19% (GPT-4.1) • 74.19% (GPT-5) • 80.65% (Claude)</strong>
                        </div>
                      </div>
                    </div>

                    <div className="mt-5 p-4 bg-[#0a0f1a] border border-[#1b2537] rounded-xl text-xs text-gray-300 leading-relaxed">
                      <strong className="text-white">Research Conclusion (Belozerov et al., Section 7):</strong> Vulnerabilities occurred significantly in both user inputs and GPT outputs. AI-generated code is not inherently safer than human code. Moreover, LLMs showed higher success fixing human-written code than fixing their own generated code, highlighting self-correction limits.
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ======================================================== */}
          {/* TAB: MANUAL VERIFICATION WORKBENCH (Section 5 Requirement) */}
          {/* ======================================================== */}
          {activeTab === 'audit' && (
            <div className="space-y-6 max-w-7xl mx-auto">
              {/* Header Box */}
              <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className="font-bold text-base text-white flex items-center gap-2">
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                    <span>Expert Manual Verification & Audit Trail (Section 5)</span>
                  </h3>
                  <p className="text-xs text-gray-400 mt-1">
                    Static scanners and LLMs produce candidate findings. As mandated by research methodology, human experts must review and record persistent verification decisions.
                  </p>
                </div>
                <div className="flex items-center gap-3 text-xs">
                  <div className="bg-[#0b101a] px-3 py-2 rounded-lg border border-[#1f2937]">
                    <span className="text-gray-400">Total Logged Decisions: </span>
                    <strong className="text-emerald-400 font-mono">{auditSummary?.total_decisions_logged ?? auditDecisions.length}</strong>
                  </div>
                </div>
              </div>

              {/* Reviewer Action Card */}
              <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-5 space-y-4">
                <h4 className="font-bold text-sm text-white flex items-center gap-2">
                  <span>Record Auditor Decision</span>
                </h4>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs">
                  <div>
                    <label className="block text-gray-400 mb-1 font-medium">Select DevGPT Case</label>
                    <select
                      value={auditCaseId}
                      onChange={(e) => {
                        setAuditCaseId(e.target.value);
                        loadDevGptCase(e.target.value);
                      }}
                      className="w-full bg-[#0a0f1a] border border-[#222f44] rounded-lg px-3 py-2 text-white outline-none font-mono"
                    >
                      {Array.from({ length: 48 }, (_, i) => {
                        const cid = `File_${String(i + 1).padStart(2, '0')}`;
                        return <option key={cid} value={cid}>{cid}</option>;
                      })}
                    </select>
                  </div>

                  <div>
                    <label className="block text-gray-400 mb-1 font-medium">Vulnerability Verdict</label>
                    <select
                      value={auditVerdict}
                      onChange={(e) => setAuditVerdict(e.target.value)}
                      className="w-full bg-[#0a0f1a] border border-[#222f44] rounded-lg px-3 py-2 text-white outline-none"
                    >
                      <option value="confirmed_vulnerability">Confirmed Vulnerability</option>
                      <option value="false_positive">False Positive (Scanner Noise)</option>
                      <option value="uncertain">Uncertain / Requires Review</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-gray-400 mb-1 font-medium">LLM Detection Outcome</label>
                    <select
                      value={auditModelDetected}
                      onChange={(e) => setAuditModelDetected(e.target.value)}
                      className="w-full bg-[#0a0f1a] border border-[#222f44] rounded-lg px-3 py-2 text-white outline-none"
                    >
                      <option value="detected">Detected by Model</option>
                      <option value="missed">Not Detected by Model</option>
                      <option value="unspecified">Unspecified / Untested</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-gray-400 mb-1 font-medium">Repair Outcome</label>
                    <select
                      value={auditRepairVerified}
                      onChange={(e) => setAuditRepairVerified(e.target.value)}
                      className="w-full bg-[#0a0f1a] border border-[#222f44] rounded-lg px-3 py-2 text-white outline-none"
                    >
                      <option value="successfully_repaired">Successfully Repaired</option>
                      <option value="failed_repair">Not Successfully Repaired</option>
                      <option value="unspecified">Not Yet Evaluated</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                  <div>
                    <label className="block text-gray-400 mb-1 font-medium">Auditor Identifier</label>
                    <input
                      type="text"
                      value={auditReviewer}
                      onChange={(e) => setAuditReviewer(e.target.value)}
                      className="w-full bg-[#0a0f1a] border border-[#222f44] rounded-lg px-3 py-2 text-white outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-gray-400 mb-1 font-medium">Evidence / Code Snippet</label>
                    <input
                      type="text"
                      placeholder="e.g. Line 57 strcpy(b, user_input) lacks bounds check"
                      value={auditEvidence}
                      onChange={(e) => setAuditEvidence(e.target.value)}
                      className="w-full bg-[#0a0f1a] border border-[#222f44] rounded-lg px-3 py-2 text-white outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-gray-400 mb-1 text-xs font-medium">Auditor Rationale & Ground-Truth Notes</label>
                  <textarea
                    rows={2}
                    placeholder="Enter scientific justification for confirmed vulnerability or false-positive status..."
                    value={auditNotes}
                    onChange={(e) => setAuditNotes(e.target.value)}
                    className="w-full bg-[#0a0f1a] border border-[#222f44] rounded-lg p-2.5 text-xs text-white outline-none resize-none font-mono"
                  />
                </div>

                <div className="flex items-center justify-between pt-2">
                  {auditStatusMessage ? (
                    <span className="text-xs text-emerald-400 font-medium">{auditStatusMessage}</span>
                  ) : <span></span>}
                  <button
                    onClick={handleSaveAuditDecision}
                    disabled={isSubmittingAudit}
                    className="px-5 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md shadow-emerald-950 transition flex items-center gap-2"
                  >
                    <Check className="w-4 h-4" />
                    <span>Commit Decision to SQLite Audit Trail</span>
                  </button>
                </div>
              </div>

              {/* Persistent Audit Records Table */}
              <div className="bg-[#111827] border border-[#1f2937] rounded-xl overflow-hidden">
                <div className="px-5 py-3.5 bg-[#141d2e] border-b border-[#1f2937] flex items-center justify-between">
                  <h4 className="font-bold text-sm text-white">Audited Decisions History (SQLite Backend)</h4>
                  <span className="text-xs text-gray-400 font-mono">{auditDecisions.length} Entries</span>
                </div>
                <div className="overflow-x-auto max-h-72 overflow-y-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-[#0b101a] text-gray-400 text-[11px] uppercase tracking-wider sticky top-0">
                      <tr>
                        <th className="px-4 py-2.5">Case ID</th>
                        <th className="px-4 py-2.5">Verdict</th>
                        <th className="px-4 py-2.5">Model Detection</th>
                        <th className="px-4 py-2.5">Repair Status</th>
                        <th className="px-4 py-2.5">Reviewer</th>
                        <th className="px-4 py-2.5">Timestamp</th>
                        <th className="px-4 py-2.5">Notes</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#1f2937] text-gray-300">
                      {auditDecisions.map((dec) => (
                        <tr key={dec.id} className="hover:bg-[#162032] transition">
                          <td className="px-4 py-2.5 font-mono font-bold text-sky-400">{dec.case_id}</td>
                          <td className="px-4 py-2.5">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${dec.verdict === 'confirmed_vulnerability'
                              ? 'bg-rose-950 text-rose-300 border border-rose-800'
                              : (dec.verdict === 'false_positive' ? 'bg-amber-950 text-amber-300 border border-amber-800' : 'bg-gray-800 text-gray-300')
                              }`}>
                              {dec.verdict.replace('_', ' ')}
                            </span>
                          </td>
                          <td className="px-4 py-2.5 font-mono text-[11px]">{dec.model_detected}</td>
                          <td className="px-4 py-2.5 font-mono text-[11px] text-emerald-400">{dec.repair_verified}</td>
                          <td className="px-4 py-2.5 text-gray-400">{dec.reviewer}</td>
                          <td className="px-4 py-2.5 text-gray-500 font-mono text-[10px]">{dec.timestamp.slice(0, 19).replace('T', ' ')}</td>
                          <td className="px-4 py-2.5 text-gray-400 max-w-xs truncate">{dec.notes || '—'}</td>
                        </tr>
                      ))}
                      {auditDecisions.length === 0 && (
                        <tr>
                          <td colSpan={7} className="text-center py-6 text-gray-500">
                            No manual audit records yet. Submit a decision above to populate the audit trail.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* ======================================================== */}
          {/* TAB 4: BENCHMARK & RESEARCH */}
          {/* ======================================================== */}
          {activeTab === 'benchmark' && (
            <div className="space-y-6">
              <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-5">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-bold text-base text-white flex items-center gap-2">
                    <Flame className="w-5 h-5 text-amber-400" />
                    <span>HISTORICAL LLM BENCHMARK (MSc DevGPT Results)</span>
                  </h3>
                  <span className="text-xs text-sky-400 font-mono bg-sky-950 px-2 py-0.5 rounded border border-sky-800">
                    48 Cases • 74 Baseline Flaws
                  </span>
                </div>
                <p className="text-xs text-gray-400 leading-relaxed">
                  These results document the empirical study conducted on 48 real-world vulnerability samples from DevGPT snapshots.
                  Frontier LLMs were evaluated under identical multi-scanner constraints (flawfinder, cppcheck, semgrep, snyk).
                </p>
              </div>

              <div className="bg-[#111827] border border-[#1f2937] rounded-xl overflow-hidden">
                <div className="overflow-x-auto max-h-[500px]">
                  <table className="w-full text-left text-xs text-gray-300">
                    <thead className="bg-[#0e1422] text-gray-400 uppercase text-[11px] font-semibold sticky top-0 border-b border-[#1f2937]">
                      <tr>
                        <th className="px-4 py-3">Case</th>
                        <th className="px-4 py-3">Target File</th>
                        <th className="px-4 py-3">Baseline Hits</th>
                        <th className="px-4 py-3">Claude Hits</th>
                        <th className="px-4 py-3">GPT-4.1 Hits</th>
                        <th className="px-4 py-3">GPT-5 Hits</th>
                        <th className="px-4 py-3">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#1b2536]">
                      {historicalData?.cases?.map((c) => (
                        <tr key={c.case} className="hover:bg-[#141d2e] transition">
                          <td className="px-4 py-2.5 font-bold text-sky-400">{c.case}</td>
                          <td className="px-4 py-2.5 font-mono text-gray-400">{c.original_file || 'N/A'}</td>
                          <td className="px-4 py-2.5">
                            <span className="px-2 py-0.5 rounded bg-rose-950 text-rose-300 font-bold border border-rose-900">
                              {c.orig_flawfinder_count}
                            </span>
                          </td>
                          <td className="px-4 py-2.5 font-mono">{c.models['claude-opus-4-1-20250805']?.flawfinder_count ?? '-'}</td>
                          <td className="px-4 py-2.5 font-mono">{c.models['gpt-4.1-2025-04-14']?.flawfinder_count ?? '-'}</td>
                          <td className="px-4 py-2.5 font-mono font-bold text-emerald-400">{c.models['gpt-5-2025-08-07']?.flawfinder_count ?? '-'}</td>
                          <td className="px-4 py-2.5">
                            <button
                              onClick={() => handleSendCaseToRepair(c.case)}
                              className="text-[11px] text-sky-400 hover:text-sky-300 font-semibold underline"
                            >
                              Load in Repair & Verify
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* ======================================================== */}
          {/* TAB 5: TEST CASES (48 SAMPLES EXPLORER) */}
          {/* ======================================================== */}
          {activeTab === 'cases' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-base text-white">DevGPT Benchmark Explorer (48 Cases)</h3>
                  <p className="text-xs text-gray-400">Select any real test case to inspect original code, recorded findings, or send to AI Repair & Verify.</p>
                </div>
                {selectedCase && (
                  <span className="text-xs font-mono text-sky-400 bg-sky-950 px-3 py-1 rounded border border-sky-800">
                    Active: {selectedCase}
                  </span>
                )}
              </div>

              {/* Case selector chips */}
              <div className="flex flex-wrap gap-1.5 p-3 bg-[#111827] border border-[#1f2937] rounded-xl max-h-36 overflow-y-auto">
                {Array.from({ length: 48 }, (_, i) => {
                  const cId = `File_${String(i + 1).padStart(2, '0')}`;
                  const isSel = selectedCase === cId;
                  return (
                    <button
                      key={cId}
                      onClick={() => handleInspectCase(cId)}
                      className={`px-2.5 py-1 rounded text-xs font-mono font-semibold transition ${isSel
                        ? 'bg-sky-600 text-white shadow'
                        : 'bg-[#162032] text-gray-400 hover:text-gray-200'
                        }`}
                    >
                      {cId}
                    </button>
                  );
                })}
              </div>

              {/* Selected Case Detail */}
              {caseDetail && (
                <div className="space-y-4">
                  <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-4 flex items-center justify-between">
                    <div>
                      <h4 className="font-bold text-sm text-white">Case: {caseDetail.case_id} ({caseDetail.target_file})</h4>
                      <p className="text-xs text-gray-400">Recorded Findings in Dataset: {caseDetail.dataset_findings?.length || 0}</p>
                    </div>
                    <button
                      onClick={() => handleSendCaseToRepair(caseDetail.case_id)}
                      className="px-4 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold transition flex items-center gap-1.5 shadow"
                    >
                      <Cpu className="w-3.5 h-3.5" />
                      <span>Send to AI Repair & Verify Pipeline</span>
                    </button>
                  </div>

                  <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-4">
                    <h4 className="font-bold text-xs text-gray-300 uppercase mb-2 flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-amber-400" />
                      Recorded Scanner Findings in Dataset
                    </h4>
                    <div className="space-y-2">
                      {caseDetail.dataset_findings?.map((df, idx) => (
                        <div key={idx} className="bg-[#0e1422] p-2.5 rounded border border-[#1f2937] text-xs flex items-center justify-between">
                          <div>
                            <span className="font-bold text-sky-400">[{df.scanner}]</span> Line {df.line}: {df.description || df.rule}
                          </div>
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800">
                            {df.cwe}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-[#111827] border border-[#1f2937] rounded-xl overflow-hidden flex flex-col h-[400px]">
                      <div className="px-4 py-2 bg-[#0e1422] border-b border-[#1f2937] text-xs font-mono text-rose-400">
                        Original Code ({caseDetail.target_file})
                      </div>
                      <pre className="flex-1 p-3 text-xs font-mono overflow-auto bg-[#070b12] text-gray-300 select-text">
                        <code>{caseDetail.original_code}</code>
                      </pre>
                    </div>

                    <div className="bg-[#111827] border border-[#1f2937] rounded-xl overflow-hidden flex flex-col h-[400px]">
                      <div className="px-4 py-2 bg-[#0e1422] border-b border-[#1f2937] text-xs font-mono text-emerald-400">
                        Historical GPT-5 Repaired Code (Flaws Reduced: {caseDetail.historical_repairs?.['gpt-5-2025-08-07']?.reduction || 0})
                      </div>
                      <pre className="flex-1 p-3 text-xs font-mono overflow-auto bg-[#070b12] text-emerald-100/90 select-text">
                        <code>{caseDetail.historical_repairs?.['gpt-5-2025-08-07']?.code || '// No historical repair'}</code>
                      </pre>
                    </div>
                  </div>
                </div>
              )}

              {/* If no case is selected yet */}
              {!caseDetail && (
                <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-12 text-center space-y-3">
                  <div className="w-12 h-12 rounded-xl bg-sky-950/60 border border-sky-800 text-sky-400 flex items-center justify-center mx-auto">
                    <FileCode className="w-6 h-6" />
                  </div>
                  <h4 className="font-bold text-base text-white">Select a Test Case Above</h4>
                  <p className="text-xs text-gray-400 max-w-md mx-auto">
                    Click on any case from <code className="text-sky-300 font-mono">File_01</code> to <code className="text-sky-300 font-mono">File_48</code> to inspect the original source code, scanner findings, and historical benchmark repairs.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* ======================================================== */}
          {/* TAB 6: AUDIT REPORTS */}
          {/* ======================================================== */}
          {activeTab === 'reports' && (
            <div className="max-w-2xl mx-auto space-y-6">
              <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-6 text-center space-y-4">
                <div className="w-12 h-12 rounded-2xl bg-sky-950 border border-sky-800 text-sky-400 flex items-center justify-center mx-auto">
                  <Download className="w-6 h-6" />
                </div>
                <h3 className="font-extrabold text-lg text-white">Generate Comprehensive Security Audit Reports</h3>
                <p className="text-xs text-gray-400 leading-relaxed">
                  Export complete security findings, CWE classifications, AI explanations, original vs repaired code,
                  compiler verification results, and quantitative reduction rates into JSON, CSV, and HTML formats.
                </p>

                <button
                  onClick={handleGenerateReport}
                  disabled={isGeneratingReports}
                  className="px-6 py-2.5 rounded-lg bg-sky-600 hover:bg-sky-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-xs font-bold transition shadow-lg shadow-sky-950 inline-flex items-center gap-2"
                >
                  {isGeneratingReports && <RefreshCw className="w-3.5 h-3.5 animate-spin" />}
                  <span>{isGeneratingReports ? "Generating Reports..." : "Generate Audit Reports Now"}</span>
                </button>

                {reportFeedback && (
                  <div className={`p-3 bg-[#0e1422] border rounded-lg text-xs font-mono mt-4 ${
                    reportFeedback.toLowerCase().includes("error")
                      ? "border-red-900/50 text-red-400"
                      : "border-[#1f2937] text-emerald-400"
                  }`}>
                    {reportFeedback}
                  </div>
                )}

                {generatedReports && (
                  <div className="pt-2 space-y-3">
                    <p className="text-xs font-semibold text-gray-300">
                      Download Your Audit Files:
                    </p>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      <button
                        onClick={() => handleDownloadReport(generatedReports.json_report)}
                        className="flex items-center justify-center space-x-2 px-4 py-2.5 rounded-lg bg-[#141d2e] hover:bg-[#1e2b42] text-white text-xs font-bold border border-[#23334d] hover:border-sky-500/50 transition shadow-sm"
                      >
                        <FileCode className="w-4 h-4 text-sky-400" />
                        <span>Download JSON</span>
                      </button>
                      <button
                        onClick={() => handleDownloadReport(generatedReports.csv_report)}
                        className="flex items-center justify-center space-x-2 px-4 py-2.5 rounded-lg bg-[#141d2e] hover:bg-[#1e2b42] text-white text-xs font-bold border border-[#23334d] hover:border-emerald-500/50 transition shadow-sm"
                      >
                        <Layers className="w-4 h-4 text-emerald-400" />
                        <span>Download CSV</span>
                      </button>
                      <button
                        onClick={() => handleDownloadReport(generatedReports.html_report)}
                        className="flex items-center justify-center space-x-2 px-4 py-2.5 rounded-lg bg-[#141d2e] hover:bg-[#1e2b42] text-white text-xs font-bold border border-[#23334d] hover:border-indigo-500/50 transition shadow-sm"
                      >
                        <ExternalLink className="w-4 h-4 text-indigo-400" />
                        <span>Download HTML</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ======================================================== */}
          {/* TAB 7: SYSTEM HEALTH & SCANNERS */}
          {/* ======================================================== */}
          {activeTab === 'settings' && (
            <div className="space-y-6 max-w-4xl mx-auto">
              {/* Ollama Section */}
              <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-5 space-y-3">
                <div className="flex items-center justify-between border-b border-[#1f2937] pb-3">
                  <div className="flex items-center space-x-2">
                    <Server className="w-5 h-5 text-indigo-400" />
                    <h3 className="font-bold text-sm text-white">Local Ollama Runtime Status</h3>
                  </div>
                  <span className={`px-2.5 py-0.5 rounded text-xs font-bold uppercase ${systemHealth?.ollama_running
                    ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                    : 'bg-amber-950 text-amber-300 border border-amber-800'
                    }`}>
                    {systemHealth?.ollama_running ? 'Online' : 'Offline'}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4 text-xs">
                  <div>
                    <span className="text-gray-400 block mb-1">Ollama URL:</span>
                    <code className="text-sky-400 font-mono bg-[#0e1422] px-2 py-1 rounded border border-[#1f2937] block">
                      {systemHealth?.ollama_url || 'http://localhost:11434'}
                    </code>
                  </div>
                  <div>
                    <span className="text-gray-400 block mb-1">Active Model:</span>
                    <code className="text-emerald-400 font-mono bg-[#0e1422] px-2 py-1 rounded border border-[#1f2937] block">
                      {systemHealth?.active_model || selectedModel || 'qwen2.5-coder'}
                    </code>
                  </div>
                </div>

                <div>
                  <span className="text-gray-400 text-xs block mb-1.5 font-semibold">Installed Local Models:</span>
                  {systemHealth?.installed_models && systemHealth.installed_models.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {systemHealth.installed_models.map((m) => (
                        <span key={m} className="px-2.5 py-1 rounded bg-[#0e1422] border border-[#23334d] text-xs font-mono text-gray-200">
                          {m}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <div className="bg-[#0e1422] p-3 rounded-lg border border-[#1f2937] text-xs text-amber-300/90 leading-relaxed">
                      No models currently reported by Ollama. Run:
                      <code className="block mt-1 bg-black/40 p-2 rounded text-emerald-300 font-mono">
                        ollama pull qwen2.5-coder
                      </code>
                    </div>
                  )}
                </div>
              </div>

              {/* Scanners Health */}
              <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-5 space-y-3">
                <div className="flex items-center space-x-2 border-b border-[#1f2937] pb-3">
                  <Shield className="w-5 h-5 text-emerald-400" />
                  <h3 className="font-bold text-sm text-white">Local Static Security Scanners</h3>
                </div>

                <div className="space-y-2.5">
                  {systemHealth?.scanners?.map((s) => (
                    <div key={s.name} className="flex items-center justify-between p-3 bg-[#0e1422] rounded-lg border border-[#1f2937] text-xs">
                      <div>
                        <div className="font-bold text-gray-200">{s.name}</div>
                        <div className="text-[11px] text-gray-400">Languages: {s.supported_languages.join(', ')}</div>
                      </div>
                      <span className={`px-2.5 py-1 rounded text-xs font-semibold ${s.installed
                        ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                        : 'bg-gray-800 text-gray-400 border border-gray-700'
                        }`}>
                        {s.status_message}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Compilers Health */}
              <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-5 space-y-3">
                <div className="flex items-center space-x-2 border-b border-[#1f2937] pb-3">
                  <Terminal className="w-5 h-5 text-sky-400" />
                  <h3 className="font-bold text-sm text-white">Language Compilers & Syntax Checkers</h3>
                </div>

                <div className="space-y-2.5">
                  {systemHealth?.compilers?.map((c) => (
                    <div key={c.language} className="flex items-center justify-between p-3 bg-[#0e1422] rounded-lg border border-[#1f2937] text-xs">
                      <div>
                        <div className="font-bold text-gray-200 uppercase">{c.language} ({c.tool_name})</div>
                        <div className="text-[11px] text-gray-400">{c.version || (c.installed ? 'Available' : 'Not found in PATH')}</div>
                      </div>
                      <span className={`px-2.5 py-1 rounded text-xs font-semibold ${c.installed
                        ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                        : 'bg-gray-800 text-gray-400 border border-gray-700'
                        }`}>
                        {c.installed ? 'PASS / Available' : 'UNAVAILABLE'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

        </div>
      </main>
    </div>
  );
}
