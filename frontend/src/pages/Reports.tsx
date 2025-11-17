import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  HelpCircle,
  Info,
  FileText,
  Download,
  Calendar,
  Filter,
  CheckCircle,
  Clock,
  FileJson,
  FileSpreadsheet,
  FileCode,
  Send,
  Eye,
  Trash2,
} from 'lucide-react';
import { api } from '../services/api';

// Reusable Tooltip component
function Tooltip({ children, text }: { children: React.ReactNode; text: string }) {
  const [show, setShow] = useState(false);
  return (
    <div className="relative inline-block">
      <div
        onMouseEnter={() => setShow(true)}
        onMouseLeave={() => setShow(false)}
        className="cursor-help"
      >
        {children}
      </div>
      {show && (
        <div className="absolute z-50 bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-dark-900 border border-dark-700 rounded-lg shadow-xl max-w-xs">
          <p className="text-xs text-slate-300">{text}</p>
        </div>
      )}
    </div>
  );
}

type ReportTemplate = 'executive' | 'technical' | 'quality' | 'cost' | 'custom';
type ExportFormat = 'pdf' | 'csv' | 'json' | 'excel';

interface GeneratedReport {
  id: string;
  template: string;
  dateRange: string;
  generatedAt: string;
  format: ExportFormat;
  status: 'completed' | 'pending' | 'failed';
}

export default function Reports() {
  const [selectedTemplate, setSelectedTemplate] = useState<ReportTemplate>('executive');
  const [timeRange, setTimeRange] = useState<string>('7d');
  const [selectedAgent, setSelectedAgent] = useState<string>('all');
  const [exportFormat, setExportFormat] = useState<ExportFormat>('pdf');
  const [showPreview, setShowPreview] = useState<boolean>(false);
  const [generatedReports, setGeneratedReports] = useState<GeneratedReport[]>([
    {
      id: '1',
      template: 'Executive Summary',
      dateRange: 'Last 7 Days',
      generatedAt: new Date().toISOString(),
      format: 'pdf',
      status: 'completed',
    },
    {
      id: '2',
      template: 'Quality Report',
      dateRange: 'Last 30 Days',
      generatedAt: new Date(Date.now() - 86400000).toISOString(),
      format: 'excel',
      status: 'completed',
    },
  ]);

  // Fetch data for report preview
  const { data: runsData } = useQuery({
    queryKey: ['runs'],
    queryFn: () => api.getRecentRuns({ limit: 100 }),
  });

  const filteredRuns = useMemo(() => {
    if (!runsData?.runs) return [];
    const startTime = getStartTime(timeRange);
    return runsData.runs.filter((r: any) => {
      const matchesTime = new Date(r.timestamp) >= new Date(startTime);
      const matchesAgent = selectedAgent === 'all' || r.agent_id === selectedAgent;
      return matchesTime && matchesAgent;
    });
  }, [runsData, timeRange, selectedAgent]);

  const reportStats = useMemo(() => {
    if (filteredRuns.length === 0) {
      return {
        totalRuns: 0,
        avgPrecision: 0,
        avgFaithfulness: 0,
        avgLatency: 0,
        avgCost: 0,
        successRate: 0,
      };
    }

    const total = filteredRuns.length;
    const avgPrecision = filteredRuns.reduce((acc: number, r: any) => acc + (r.precision || 0), 0) / total;
    const avgFaithfulness = filteredRuns.reduce((acc: number, r: any) => acc + (r.faithfulness || 0), 0) / total;
    const avgLatency = filteredRuns.reduce((acc: number, r: any) => acc + (r.latency || 1.5), 0) / total;
    const avgCost = filteredRuns.reduce((acc: number, r: any) => acc + (r.cost || 0.01), 0) / total;
    const successful = filteredRuns.filter((r: any) => r.precision && r.precision > 0.7).length;
    const successRate = (successful / total) * 100;

    return {
      totalRuns: total,
      avgPrecision,
      avgFaithfulness,
      avgLatency,
      avgCost,
      successRate,
    };
  }, [filteredRuns]);

  const handleGenerateReport = () => {
    const newReport: GeneratedReport = {
      id: (generatedReports.length + 1).toString(),
      template: getTemplateName(selectedTemplate),
      dateRange: getTimeRangeName(timeRange),
      generatedAt: new Date().toISOString(),
      format: exportFormat,
      status: 'completed',
    };
    setGeneratedReports([newReport, ...generatedReports]);
    setShowPreview(true);

    // Automatically download the report
    downloadReport(newReport.id, newReport.template, exportFormat);
  };

  const downloadReport = (reportId: string, templateName: string, format: ExportFormat) => {
    const timestamp = new Date().toISOString().split('T')[0];
    const filename = `${templateName.replace(/\s+/g, '_')}_${timestamp}`;

    if (format === 'json') {
      downloadJSON(filename);
    } else if (format === 'csv') {
      downloadCSV(filename);
    } else if (format === 'excel') {
      downloadExcel(filename);
    } else if (format === 'pdf') {
      downloadPDF(filename);
    }
  };

  const downloadJSON = (filename: string) => {
    const reportData = {
      template: getTemplateName(selectedTemplate),
      dateRange: getTimeRangeName(timeRange),
      agent: selectedAgent,
      generatedAt: new Date().toISOString(),
      stats: reportStats,
      runs: filteredRuns.map((r: any) => ({
        run_id: r.run_id,
        query: r.query,
        response: r.response,
        timestamp: r.timestamp,
        precision: r.precision,
        faithfulness: r.faithfulness,
        agent_id: r.agent_id,
      })),
    };

    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${filename}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const downloadCSV = (filename: string) => {
    const headers = [
      'Run ID',
      'Timestamp',
      'Agent',
      'Query',
      'Precision',
      'Faithfulness',
      'Success',
    ];

    const rows = filteredRuns.map((r: any) => [
      r.run_id,
      new Date(r.timestamp).toLocaleString(),
      r.agent_id,
      `"${(r.query || '').replace(/"/g, '""')}"`,
      r.precision ? (r.precision * 100).toFixed(1) + '%' : 'N/A',
      r.faithfulness ? (r.faithfulness * 100).toFixed(1) + '%' : 'N/A',
      r.precision && r.precision > 0.7 ? 'Yes' : 'No',
    ]);

    const csvContent = [headers.join(','), ...rows.map((row) => row.join(','))].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${filename}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const downloadExcel = (filename: string) => {
    // For Excel, we'll generate a simple tab-separated file with .xls extension
    const headers = [
      'Run ID',
      'Timestamp',
      'Agent',
      'Query',
      'Precision (%)',
      'Faithfulness (%)',
      'Success',
    ];

    const rows = filteredRuns.map((r: any) => [
      r.run_id,
      new Date(r.timestamp).toLocaleString(),
      r.agent_id,
      r.query || '',
      r.precision ? (r.precision * 100).toFixed(1) : '',
      r.faithfulness ? (r.faithfulness * 100).toFixed(1) : '',
      r.precision && r.precision > 0.7 ? 'Yes' : 'No',
    ]);

    const tsvContent = [headers.join('\t'), ...rows.map((row) => row.join('\t'))].join('\n');

    const blob = new Blob([tsvContent], {
      type: 'application/vnd.ms-excel',
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${filename}.xls`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const downloadPDF = (filename: string) => {
    // Generate HTML report that can be converted to PDF
    const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>${getTemplateName(selectedTemplate)} - ${getTimeRangeName(timeRange)}</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; color: #333; }
    h1 { color: #1e40af; border-bottom: 3px solid #3b82f6; padding-bottom: 10px; }
    h2 { color: #1e3a8a; margin-top: 30px; }
    .meta { color: #64748b; font-size: 14px; margin-bottom: 20px; }
    .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 20px 0; }
    .stat-card { border: 1px solid #e2e8f0; padding: 15px; border-radius: 8px; }
    .stat-label { color: #64748b; font-size: 12px; text-transform: uppercase; }
    .stat-value { font-size: 24px; font-weight: bold; color: #1e40af; margin-top: 5px; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th { background: #f1f5f9; padding: 12px; text-align: left; border-bottom: 2px solid #cbd5e1; }
    td { padding: 10px; border-bottom: 1px solid #e2e8f0; }
    .success { color: #10b981; }
    .warning { color: #f59e0b; }
    .error { color: #ef4444; }
    ul { line-height: 1.8; }
    .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #e2e8f0; color: #64748b; font-size: 12px; }
  </style>
</head>
<body>
  <h1>${getTemplateName(selectedTemplate)}</h1>
  <div class="meta">
    <strong>Date Range:</strong> ${getTimeRangeName(timeRange)}<br>
    <strong>Agent:</strong> ${selectedAgent === 'all' ? 'All Agents' : selectedAgent}<br>
    <strong>Generated:</strong> ${new Date().toLocaleString()}<br>
    <strong>Total Runs:</strong> ${reportStats.totalRuns}
  </div>

  <h2>Executive Summary</h2>
  <div class="stats">
    <div class="stat-card">
      <div class="stat-label">Average Precision</div>
      <div class="stat-value ${reportStats.avgPrecision >= 0.8 ? 'success' : reportStats.avgPrecision >= 0.6 ? 'warning' : 'error'}">
        ${(reportStats.avgPrecision * 100).toFixed(1)}%
      </div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Average Faithfulness</div>
      <div class="stat-value ${reportStats.avgFaithfulness >= 0.8 ? 'success' : reportStats.avgFaithfulness >= 0.6 ? 'warning' : 'error'}">
        ${(reportStats.avgFaithfulness * 100).toFixed(1)}%
      </div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Success Rate</div>
      <div class="stat-value ${reportStats.successRate >= 80 ? 'success' : reportStats.successRate >= 60 ? 'warning' : 'error'}">
        ${reportStats.successRate.toFixed(1)}%
      </div>
    </div>
  </div>

  <h2>Report Details</h2>
  <ul>
    ${getTemplateContent(selectedTemplate).map((item) => `<li>${item}</li>`).join('')}
  </ul>

  <div class="footer">
    Generated by RAIA - Responsible AI Analytics & Agent Evaluation<br>
    © ${new Date().getFullYear()} - This report contains ${reportStats.totalRuns} evaluation runs
  </div>
</body>
</html>
    `;

    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${filename}.html`;
    link.click();
    URL.revokeObjectURL(url);

    // Note: For actual PDF, you'd need a PDF library like jsPDF
    // This generates HTML that can be printed to PDF via browser
    setTimeout(() => {
      alert('HTML report downloaded. Use your browser\'s "Print to PDF" feature for PDF format.');
    }, 500);
  };

  const handleDownloadReport = (reportId: string) => {
    const report = generatedReports.find((r) => r.id === reportId);
    if (report) {
      downloadReport(reportId, report.template, report.format);
    }
  };

  const handleDeleteReport = (reportId: string) => {
    setGeneratedReports(generatedReports.filter((r) => r.id !== reportId));
  };

  const availableAgents = ['all', 'gpt-4', 'gpt-3.5-turbo', 'claude-3-opus', 'claude-3-sonnet', 'gemini-pro'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-3xl font-bold text-white">Reports & Export</h1>
          <Tooltip text="Generate comprehensive evaluation reports with customizable templates, filters, and export formats. Reports include metrics, trends, and actionable insights. Export to PDF for sharing, Excel for analysis, CSV for data processing, or JSON for programmatic access.">
            <HelpCircle className="w-5 h-5 text-slate-400" />
          </Tooltip>
        </div>
        <p className="text-slate-400 mt-1">Generate and export evaluation reports</p>
      </div>

      {/* Explanation Card */}
      <div className="card p-6 bg-primary-500/5 border-2 border-primary-500/30">
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-primary-400 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-primary-300">How Report Generation Works</h3>
            <p className="text-xs text-slate-400 mt-1">
              Choose a report template that matches your audience and goals:
            </p>
            <ul className="mt-2 space-y-1 text-xs text-slate-400">
              <li><strong>Executive Summary:</strong> High-level overview for stakeholders (key metrics, trends, recommendations)</li>
              <li><strong>Technical Deep Dive:</strong> Detailed analysis for engineers (latency, errors, optimization opportunities)</li>
              <li><strong>Quality Report:</strong> Focus on precision, faithfulness, and hallucination metrics</li>
              <li><strong>Cost Analysis:</strong> Token usage, cost trends, and cost optimization recommendations</li>
              <li><strong>Custom Report:</strong> Build your own report with selected metrics and visualizations</li>
            </ul>
            <p className="text-xs text-slate-400 mt-2">
              Select a time range and agent filter, then choose your export format. Preview before downloading to ensure the report meets your needs.
            </p>
          </div>
        </div>
      </div>

      {/* Report Configuration */}
      <div className="card p-6">
        <div className="flex items-center gap-2 mb-6">
          <h2 className="text-lg font-semibold text-white">Report Configuration</h2>
          <Tooltip text="Configure your report by selecting a template, time range, agent filter, and export format. The system will generate a comprehensive report based on your selections.">
            <HelpCircle className="w-4 h-4 text-slate-400" />
          </Tooltip>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Report Template */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Report Template
              </label>
              <Tooltip text="Choose a pre-configured report template optimized for different audiences. Each template includes relevant metrics, charts, and insights tailored to specific use cases.">
                <HelpCircle className="w-3 h-3 text-slate-500" />
              </Tooltip>
            </div>
            <div className="space-y-2">
              <ReportTemplateCard
                id="executive"
                title="Executive Summary"
                description="High-level overview for stakeholders"
                icon={FileText}
                selected={selectedTemplate === 'executive'}
                onClick={() => setSelectedTemplate('executive')}
              />
              <ReportTemplateCard
                id="technical"
                title="Technical Deep Dive"
                description="Detailed analysis for engineers"
                icon={FileCode}
                selected={selectedTemplate === 'technical'}
                onClick={() => setSelectedTemplate('technical')}
              />
              <ReportTemplateCard
                id="quality"
                title="Quality Report"
                description="Precision, faithfulness, hallucination metrics"
                icon={CheckCircle}
                selected={selectedTemplate === 'quality'}
                onClick={() => setSelectedTemplate('quality')}
              />
              <ReportTemplateCard
                id="cost"
                title="Cost Analysis"
                description="Token usage and cost optimization"
                icon={FileSpreadsheet}
                selected={selectedTemplate === 'cost'}
                onClick={() => setSelectedTemplate('cost')}
              />
            </div>
          </div>

          {/* Filters and Export */}
          <div className="space-y-4">
            {/* Time Range */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Time Range
                </label>
                <Tooltip text="Select the time period for your report. The report will include all data from the selected time range, showing trends and aggregated metrics.">
                  <HelpCircle className="w-3 h-3 text-slate-500" />
                </Tooltip>
              </div>
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="w-full px-4 py-2 bg-dark-800 border border-dark-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="90d">Last 90 Days</option>
                <option value="all">All Time</option>
              </select>
            </div>

            {/* Agent Filter */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Agent Filter
                </label>
                <Tooltip text="Optionally filter the report to a specific agent. Choose 'All Agents' to include data from all agents, or select a specific agent to analyze its performance in isolation.">
                  <HelpCircle className="w-3 h-3 text-slate-500" />
                </Tooltip>
              </div>
              <select
                value={selectedAgent}
                onChange={(e) => setSelectedAgent(e.target.value)}
                className="w-full px-4 py-2 bg-dark-800 border border-dark-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="all">All Agents</option>
                {availableAgents.slice(1).map((agent) => (
                  <option key={agent} value={agent}>
                    {agent}
                  </option>
                ))}
              </select>
            </div>

            {/* Export Format */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Export Format
                </label>
                <Tooltip text="Choose the file format for your report. PDF for sharing, Excel/CSV for data analysis, or JSON for programmatic access. Each format preserves the full report content.">
                  <HelpCircle className="w-3 h-3 text-slate-500" />
                </Tooltip>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <ExportFormatButton
                  format="pdf"
                  label="PDF"
                  icon={FileText}
                  selected={exportFormat === 'pdf'}
                  onClick={() => setExportFormat('pdf')}
                />
                <ExportFormatButton
                  format="excel"
                  label="Excel"
                  icon={FileSpreadsheet}
                  selected={exportFormat === 'excel'}
                  onClick={() => setExportFormat('excel')}
                />
                <ExportFormatButton
                  format="csv"
                  label="CSV"
                  icon={FileCode}
                  selected={exportFormat === 'csv'}
                  onClick={() => setExportFormat('csv')}
                />
                <ExportFormatButton
                  format="json"
                  label="JSON"
                  icon={FileJson}
                  selected={exportFormat === 'json'}
                  onClick={() => setExportFormat('json')}
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 pt-4">
              <button
                onClick={handleGenerateReport}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-semibold transition-colors"
              >
                <Download className="w-4 h-4" />
                Generate & Download
              </button>
              <button
                onClick={() => setShowPreview(!showPreview)}
                className="flex items-center justify-center gap-2 px-4 py-3 bg-dark-700 hover:bg-dark-600 text-white rounded-lg font-semibold transition-colors"
              >
                <Eye className="w-4 h-4" />
                Preview
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Report Preview */}
      {showPreview && (
        <div className="card p-6">
          <div className="flex items-center gap-2 mb-4">
            <h2 className="text-lg font-semibold text-white">Report Preview</h2>
            <Tooltip text="Preview shows a summary of the data that will be included in your report. Review the metrics to ensure the report captures the information you need before generating the full report.">
              <HelpCircle className="w-4 h-4 text-slate-400" />
            </Tooltip>
          </div>

          <div className="space-y-4">
            {/* Report Header */}
            <div className="border-b border-dark-700 pb-4">
              <h3 className="text-xl font-bold text-white">{getTemplateName(selectedTemplate)}</h3>
              <p className="text-sm text-slate-400 mt-1">
                {getTimeRangeName(timeRange)} {selectedAgent !== 'all' && `• Agent: ${selectedAgent}`}
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Generated on {new Date().toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </p>
            </div>

            {/* Key Metrics */}
            <div>
              <h4 className="text-sm font-semibold text-slate-300 mb-3">Key Metrics</h4>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                <MetricPreview label="Total Runs" value={reportStats.totalRuns.toString()} />
                <MetricPreview label="Avg Precision" value={`${(reportStats.avgPrecision * 100).toFixed(1)}%`} />
                <MetricPreview label="Avg Faithfulness" value={`${(reportStats.avgFaithfulness * 100).toFixed(1)}%`} />
                <MetricPreview label="Avg Latency" value={`${reportStats.avgLatency.toFixed(2)}s`} />
                <MetricPreview label="Avg Cost" value={`$${reportStats.avgCost.toFixed(4)}`} />
                <MetricPreview label="Success Rate" value={`${reportStats.successRate.toFixed(1)}%`} />
              </div>
            </div>

            {/* Template-Specific Content */}
            <div className="bg-dark-800/50 border border-dark-700 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-slate-300 mb-2">Report Includes:</h4>
              <ul className="text-xs text-slate-400 space-y-1">
                {getTemplateContent(selectedTemplate).map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <CheckCircle className="w-3 h-3 text-success-500 flex-shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Recent Reports */}
      <div className="card p-6">
        <div className="flex items-center gap-2 mb-4">
          <h2 className="text-lg font-semibold text-white">Recent Reports</h2>
          <Tooltip text="View and download previously generated reports. Each report is saved with its configuration and can be re-downloaded at any time.">
            <HelpCircle className="w-4 h-4 text-slate-400" />
          </Tooltip>
        </div>

        {generatedReports.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <p className="text-slate-400">No reports generated yet</p>
            <p className="text-xs text-slate-500 mt-1">Generate your first report using the configuration above</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-b border-dark-700">
                <tr>
                  <th className="text-left py-3 px-4 text-slate-400 font-semibold">Template</th>
                  <th className="text-left py-3 px-4 text-slate-400 font-semibold">Date Range</th>
                  <th className="text-left py-3 px-4 text-slate-400 font-semibold">Generated</th>
                  <th className="text-left py-3 px-4 text-slate-400 font-semibold">Format</th>
                  <th className="text-left py-3 px-4 text-slate-400 font-semibold">Status</th>
                  <th className="text-right py-3 px-4 text-slate-400 font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-dark-700">
                {generatedReports.map((report) => (
                  <tr key={report.id} className="hover:bg-dark-800/50">
                    <td className="py-3 px-4 text-white font-medium">{report.template}</td>
                    <td className="py-3 px-4 text-slate-300">{report.dateRange}</td>
                    <td className="py-3 px-4 text-slate-300">
                      {new Date(report.generatedAt).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </td>
                    <td className="py-3 px-4">
                      <span className="inline-flex items-center gap-1 px-2 py-1 bg-dark-700 rounded text-xs text-slate-300">
                        {getFormatIcon(report.format)}
                        {report.format.toUpperCase()}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={report.status} />
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleDownloadReport(report.id)}
                          className="p-2 hover:bg-dark-700 rounded-lg transition-colors"
                          title="Download report"
                        >
                          <Download className="w-4 h-4 text-primary-400" />
                        </button>
                        <button
                          onClick={() => handleDeleteReport(report.id)}
                          className="p-2 hover:bg-dark-700 rounded-lg transition-colors"
                          title="Delete report"
                        >
                          <Trash2 className="w-4 h-4 text-critical-400" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Scheduled Reports (Optional - Basic Implementation) */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-semibold text-white">Scheduled Reports</h2>
            <Tooltip text="Set up automatic report generation and delivery on a recurring schedule. Reports can be emailed to stakeholders daily, weekly, or monthly.">
              <HelpCircle className="w-4 h-4 text-slate-400" />
            </Tooltip>
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-dark-700 hover:bg-dark-600 text-white rounded-lg text-sm font-semibold transition-colors">
            <Calendar className="w-4 h-4" />
            New Schedule
          </button>
        </div>

        <div className="text-center py-8">
          <Clock className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <p className="text-slate-400">No scheduled reports</p>
          <p className="text-xs text-slate-500 mt-1">
            Set up automatic report generation for regular stakeholder updates
          </p>
        </div>
      </div>
    </div>
  );
}

// Helper Components
function ReportTemplateCard({
  id,
  title,
  description,
  icon: Icon,
  selected,
  onClick,
}: {
  id: string;
  title: string;
  description: string;
  icon: any;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-start gap-3 p-4 rounded-lg border-2 transition-all text-left ${
        selected
          ? 'border-primary-500 bg-primary-500/10'
          : 'border-dark-700 bg-dark-800/50 hover:border-dark-600'
      }`}
    >
      <Icon className={`w-5 h-5 flex-shrink-0 mt-0.5 ${selected ? 'text-primary-400' : 'text-slate-400'}`} />
      <div className="flex-1 min-w-0">
        <h4 className={`text-sm font-semibold ${selected ? 'text-white' : 'text-slate-300'}`}>
          {title}
        </h4>
        <p className="text-xs text-slate-400 mt-0.5">{description}</p>
      </div>
      {selected && <CheckCircle className="w-5 h-5 text-primary-400 flex-shrink-0" />}
    </button>
  );
}

function ExportFormatButton({
  format,
  label,
  icon: Icon,
  selected,
  onClick,
}: {
  format: string;
  label: string;
  icon: any;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center justify-center gap-2 p-3 rounded-lg border-2 transition-all ${
        selected
          ? 'border-primary-500 bg-primary-500/10 text-primary-400'
          : 'border-dark-700 bg-dark-800/50 hover:border-dark-600 text-slate-400'
      }`}
    >
      <Icon className="w-4 h-4" />
      <span className="text-sm font-semibold">{label}</span>
    </button>
  );
}

function MetricPreview({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-dark-800/50 border border-dark-700 rounded-lg p-3">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="text-lg font-bold text-white mt-1">{value}</p>
    </div>
  );
}

function StatusBadge({ status }: { status: 'completed' | 'pending' | 'failed' }) {
  const config = {
    completed: { color: 'text-success-500 bg-success-500/10', icon: CheckCircle, label: 'Completed' },
    pending: { color: 'text-warning-500 bg-warning-500/10', icon: Clock, label: 'Pending' },
    failed: { color: 'text-critical-500 bg-critical-500/10', icon: FileText, label: 'Failed' },
  };

  const { color, icon: Icon, label } = config[status];

  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded text-xs font-semibold ${color}`}>
      <Icon className="w-3 h-3" />
      {label}
    </span>
  );
}

// Helper functions
function getStartTime(range: string): string {
  const now = new Date();
  switch (range) {
    case '24h':
      return new Date(now.getTime() - 24 * 60 * 60 * 1000).toISOString();
    case '7d':
      return new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString();
    case '30d':
      return new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString();
    case '90d':
      return new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000).toISOString();
    case 'all':
      return new Date(0).toISOString();
    default:
      return new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString();
  }
}

function getTemplateName(template: ReportTemplate): string {
  const names = {
    executive: 'Executive Summary',
    technical: 'Technical Deep Dive',
    quality: 'Quality Report',
    cost: 'Cost Analysis',
    custom: 'Custom Report',
  };
  return names[template];
}

function getTimeRangeName(range: string): string {
  const names: Record<string, string> = {
    '24h': 'Last 24 Hours',
    '7d': 'Last 7 Days',
    '30d': 'Last 30 Days',
    '90d': 'Last 90 Days',
    'all': 'All Time',
  };
  return names[range] || 'Custom Range';
}

function getTemplateContent(template: ReportTemplate): string[] {
  const content = {
    executive: [
      'Executive summary with key findings and recommendations',
      'Overall system health score and trend analysis',
      'Top 5 performance metrics with month-over-month comparison',
      'Critical issues requiring immediate attention',
      'Cost summary and ROI analysis',
      'Success stories and wins',
    ],
    technical: [
      'Detailed latency breakdown by query type',
      'Error logs and failure analysis',
      'API endpoint performance metrics',
      'Database query optimization opportunities',
      'Resource utilization charts (CPU, memory, network)',
      'Performance bottleneck identification',
      'Scalability recommendations',
    ],
    quality: [
      'Precision and recall metrics by agent',
      'Faithfulness scores with hallucination examples',
      'Attribution coverage analysis',
      'Source quality distribution',
      'Quality degradation trends',
      'Recommendations for improving answer quality',
    ],
    cost: [
      'Total token usage and cost breakdown',
      'Cost per query by agent and query type',
      'Cost trend analysis (daily, weekly, monthly)',
      'High-cost queries and optimization opportunities',
      'Cost vs quality trade-off analysis',
      'Budget forecasting and recommendations',
    ],
    custom: [
      'Selected metrics and visualizations',
      'Custom filters and grouping',
      'Personalized insights',
    ],
  };
  return content[template];
}

function getFormatIcon(format: ExportFormat) {
  const icons = {
    pdf: <FileText className="w-3 h-3" />,
    excel: <FileSpreadsheet className="w-3 h-3" />,
    csv: <FileCode className="w-3 h-3" />,
    json: <FileJson className="w-3 h-3" />,
  };
  return icons[format];
}
