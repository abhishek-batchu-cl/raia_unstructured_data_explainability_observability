import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';
import {
  HelpCircle,
  Info,
  TrendingUp,
  TrendingDown,
  Minus,
  Crown,
  Zap,
  DollarSign,
  Target,
  Clock,
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

export default function Compare() {
  const [agent1, setAgent1] = useState<string>('gpt-4');
  const [agent2, setAgent2] = useState<string>('claude-3-sonnet');
  const [timeRange, setTimeRange] = useState<string>('7d');

  // Fetch runs for both agents
  const { data: runsData1 } = useQuery({
    queryKey: ['runs', agent1, timeRange],
    queryFn: () => api.getRecentRuns({ limit: 100 }),
  });

  const { data: runsData2 } = useQuery({
    queryKey: ['runs', agent2, timeRange],
    queryFn: () => api.getRecentRuns({ limit: 100 }),
  });

  // Filter runs by agent and time range
  const agent1Runs = useMemo(() => {
    if (!runsData1?.runs) return [];
    const startTime = getStartTime(timeRange);
    return runsData1.runs.filter(
      (r: any) =>
        r.agent_id === agent1 && new Date(r.timestamp) >= new Date(startTime)
    );
  }, [runsData1, agent1, timeRange]);

  const agent2Runs = useMemo(() => {
    if (!runsData2?.runs) return [];
    const startTime = getStartTime(timeRange);
    return runsData2.runs.filter(
      (r: any) =>
        r.agent_id === agent2 && new Date(r.timestamp) >= new Date(startTime)
    );
  }, [runsData2, agent2, timeRange]);

  // Calculate stats for both agents
  const stats1 = useMemo(() => calculateStats(agent1Runs), [agent1Runs]);
  const stats2 = useMemo(() => calculateStats(agent2Runs), [agent2Runs]);

  // Prepare radar chart data for multi-dimensional comparison
  const radarData = useMemo(() => {
    return [
      {
        metric: 'Precision',
        [agent1]: stats1.avgPrecision * 100,
        [agent2]: stats2.avgPrecision * 100,
      },
      {
        metric: 'Faithfulness',
        [agent1]: stats1.avgFaithfulness * 100,
        [agent2]: stats2.avgFaithfulness * 100,
      },
      {
        metric: 'Speed',
        [agent1]: Math.max(0, 100 - stats1.avgLatency * 10), // Invert latency for visualization
        [agent2]: Math.max(0, 100 - stats2.avgLatency * 10),
      },
      {
        metric: 'Cost Efficiency',
        [agent1]: Math.max(0, 100 - stats1.avgCost * 100), // Invert cost for visualization
        [agent2]: Math.max(0, 100 - stats2.avgCost * 100),
      },
      {
        metric: 'Success Rate',
        [agent1]: stats1.successRate,
        [agent2]: stats2.successRate,
      },
    ];
  }, [stats1, stats2, agent1, agent2]);

  // Prepare time series data for trend comparison
  const trendData = useMemo(() => {
    const dates = new Set([
      ...agent1Runs.map((r: any) => r.timestamp?.split('T')[0]),
      ...agent2Runs.map((r: any) => r.timestamp?.split('T')[0]),
    ]);

    return Array.from(dates)
      .sort()
      .map((date) => {
        const runs1OnDate = agent1Runs.filter(
          (r: any) => r.timestamp?.split('T')[0] === date
        );
        const runs2OnDate = agent2Runs.filter(
          (r: any) => r.timestamp?.split('T')[0] === date
        );

        const avg1 =
          runs1OnDate.length > 0
            ? runs1OnDate.reduce((acc: number, r: any) => acc + (r.precision || 0), 0) /
              runs1OnDate.length
            : null;
        const avg2 =
          runs2OnDate.length > 0
            ? runs2OnDate.reduce((acc: number, r: any) => acc + (r.precision || 0), 0) /
              runs2OnDate.length
            : null;

        return {
          date: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          [agent1]: avg1 !== null ? (avg1 * 100).toFixed(1) : null,
          [agent2]: avg2 !== null ? (avg2 * 100).toFixed(1) : null,
        };
      });
  }, [agent1Runs, agent2Runs, agent1, agent2]);

  // Determine winner for each metric
  const winners = useMemo(() => {
    return {
      precision: stats1.avgPrecision > stats2.avgPrecision ? agent1 : agent2,
      faithfulness: stats1.avgFaithfulness > stats2.avgFaithfulness ? agent1 : agent2,
      latency: stats1.avgLatency < stats2.avgLatency ? agent1 : agent2, // Lower is better
      cost: stats1.avgCost < stats2.avgCost ? agent1 : agent2, // Lower is better
      successRate: stats1.successRate > stats2.successRate ? agent1 : agent2,
    };
  }, [stats1, stats2, agent1, agent2]);

  // Overall winner (most wins)
  const overallWinner = useMemo(() => {
    const wins1 = Object.values(winners).filter((w) => w === agent1).length;
    const wins2 = Object.values(winners).filter((w) => w === agent2).length;
    if (wins1 > wins2) return agent1;
    if (wins2 > wins1) return agent2;
    return 'tie';
  }, [winners, agent1, agent2]);

  const availableAgents = ['gpt-4', 'gpt-3.5-turbo', 'claude-3-opus', 'claude-3-sonnet', 'gemini-pro'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-3xl font-bold text-white">Compare Agents</h1>
          <Tooltip text="Compare the performance of different AI agents side-by-side across multiple metrics. Select two agents and a time range to see detailed comparisons of precision, faithfulness, speed, cost, and success rate. The radar chart shows multi-dimensional performance at a glance, while the trend chart reveals how performance changes over time.">
            <HelpCircle className="w-5 h-5 text-slate-400" />
          </Tooltip>
        </div>
        <p className="text-slate-400 mt-1">Side-by-side comparison of agent performance</p>
      </div>

      {/* Agent Selection */}
      <div className="card p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Agent 1 */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Agent 1
            </label>
            <select
              value={agent1}
              onChange={(e) => setAgent1(e.target.value)}
              className="w-full px-4 py-2 bg-dark-800 border border-dark-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {availableAgents.map((agent) => (
                <option key={agent} value={agent}>
                  {agent}
                </option>
              ))}
            </select>
          </div>

          {/* Agent 2 */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Agent 2
            </label>
            <select
              value={agent2}
              onChange={(e) => setAgent2(e.target.value)}
              className="w-full px-4 py-2 bg-dark-800 border border-dark-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {availableAgents.map((agent) => (
                <option key={agent} value={agent}>
                  {agent}
                </option>
              ))}
            </select>
          </div>

          {/* Time Range */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Time Range
            </label>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="w-full px-4 py-2 bg-dark-800 border border-dark-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
            </select>
          </div>
        </div>
      </div>

      {/* Overall Winner Banner */}
      {overallWinner !== 'tie' && (
        <div className="card p-6 bg-gradient-to-r from-yellow-500/10 to-orange-500/10 border-2 border-yellow-500/30">
          <div className="flex items-center gap-3">
            <Crown className="w-6 h-6 text-yellow-400" />
            <div>
              <h3 className="text-lg font-semibold text-white">Overall Winner: {overallWinner}</h3>
              <p className="text-sm text-slate-300 mt-1">
                {overallWinner} wins in {Object.values(winners).filter((w) => w === overallWinner).length} out of 5 metrics
              </p>
            </div>
          </div>
        </div>
      )}

      {overallWinner === 'tie' && (
        <div className="card p-6 bg-primary-500/5 border-2 border-primary-500/30">
          <div className="flex items-center gap-3">
            <Minus className="w-6 h-6 text-primary-400" />
            <div>
              <h3 className="text-lg font-semibold text-white">It's a Tie!</h3>
              <p className="text-sm text-slate-300 mt-1">
                Both agents perform equally across the selected metrics
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Explanation Card */}
      <div className="card p-6 bg-primary-500/5 border-2 border-primary-500/30">
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-primary-400 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-primary-300">How Agent Comparison Works</h3>
            <p className="text-xs text-slate-400 mt-1">
              Agent comparison shows side-by-side performance across 5 key dimensions:
            </p>
            <ul className="mt-2 space-y-1 text-xs text-slate-400">
              <li><strong>Precision:</strong> Accuracy of retrieved documents (higher is better, target: &gt;80%)</li>
              <li><strong>Faithfulness:</strong> How well answers stick to sources (higher is better, target: &gt;90%)</li>
              <li><strong>Speed:</strong> Average latency per query (lower is better, target: &lt;2s)</li>
              <li><strong>Cost Efficiency:</strong> Average cost per query (lower is better)</li>
              <li><strong>Success Rate:</strong> Percentage of queries with precision &gt;70%</li>
            </ul>
            <p className="text-xs text-slate-400 mt-2">
              Use the radar chart for at-a-glance multi-dimensional comparison, and the trend chart to see how performance evolves over time. Winner badges highlight which agent performs better in each metric.
            </p>
          </div>
        </div>
      </div>

      {/* Side-by-Side Metric Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Precision */}
        <MetricCard
          title="Precision"
          icon={Target}
          value1={stats1.avgPrecision}
          value2={stats2.avgPrecision}
          agent1={agent1}
          agent2={agent2}
          winner={winners.precision}
          format="percentage"
          higherIsBetter={true}
          tooltip="Precision measures the accuracy of retrieved documents. A higher precision means the agent retrieves more relevant documents and fewer irrelevant ones. Target: &gt;80%"
        />

        {/* Faithfulness */}
        <MetricCard
          title="Faithfulness"
          icon={Zap}
          value1={stats1.avgFaithfulness}
          value2={stats2.avgFaithfulness}
          agent1={agent1}
          agent2={agent2}
          winner={winners.faithfulness}
          format="percentage"
          higherIsBetter={true}
          tooltip="Faithfulness measures how well answers stick to the source documents. Higher faithfulness means less hallucination and more grounded answers. Target: &gt;90%"
        />

        {/* Latency */}
        <MetricCard
          title="Speed (Latency)"
          icon={Clock}
          value1={stats1.avgLatency}
          value2={stats2.avgLatency}
          agent1={agent1}
          agent2={agent2}
          winner={winners.latency}
          format="seconds"
          higherIsBetter={false}
          tooltip="Average time to complete a query from start to finish. Lower latency means faster responses. Fast: &lt;1s, Medium: 1-2s, Slow: &gt;2s"
        />

        {/* Cost */}
        <MetricCard
          title="Cost Efficiency"
          icon={DollarSign}
          value1={stats1.avgCost}
          value2={stats2.avgCost}
          agent1={agent1}
          agent2={agent2}
          winner={winners.cost}
          format="dollars"
          higherIsBetter={false}
          tooltip="Average cost per query in dollars. Lower cost means more efficient token usage. Consider the trade-off between cost and quality when selecting an agent."
        />

        {/* Success Rate */}
        <MetricCard
          title="Success Rate"
          icon={TrendingUp}
          value1={stats1.successRate}
          value2={stats2.successRate}
          agent1={agent1}
          agent2={agent2}
          winner={winners.successRate}
          format="percentage"
          higherIsBetter={true}
          tooltip="Percentage of queries where precision exceeded 70%. Higher success rate indicates more consistent performance. Target: &gt;80%"
        />
      </div>

      {/* Radar Chart - Multi-Dimensional Comparison */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-semibold text-white">Multi-Dimensional Performance</h2>
            <Tooltip text="Radar chart showing all 5 metrics at once. The larger the colored area, the better the overall performance. Compare shapes to see where each agent excels or needs improvement.">
              <HelpCircle className="w-4 h-4 text-slate-400" />
            </Tooltip>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={400}>
          <RadarChart data={radarData}>
            <PolarGrid stroke="#1e293b" />
            <PolarAngleAxis dataKey="metric" tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: '#64748b' }} />
            <Radar
              name={agent1}
              dataKey={agent1}
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.3}
            />
            <Radar
              name={agent2}
              dataKey={agent2}
              stroke="#8b5cf6"
              fill="#8b5cf6"
              fillOpacity={0.3}
            />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />
            <RechartsTooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                border: '1px solid #1e293b',
                borderRadius: '8px',
                color: '#e2e8f0',
              }}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Performance Trend Chart */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-semibold text-white">Performance Trend (Precision Over Time)</h2>
            <Tooltip text="Line chart showing how precision changes over the selected time period. Track performance trends, identify regressions, and see which agent maintains consistent quality.">
              <HelpCircle className="w-4 h-4 text-slate-400" />
            </Tooltip>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={trendData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 11 }} />
            <YAxis stroke="#64748b" domain={[0, 100]} />
            <RechartsTooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                border: '1px solid #1e293b',
                borderRadius: '8px',
                color: '#e2e8f0',
              }}
              formatter={(value: any) => [`${value}%`, '']}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey={agent1}
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ fill: '#3b82f6', r: 4 }}
              name={agent1}
            />
            <Line
              type="monotone"
              dataKey={agent2}
              stroke="#8b5cf6"
              strokeWidth={2}
              dot={{ fill: '#8b5cf6', r: 4 }}
              name={agent2}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Detailed Stats Table */}
      <div className="card p-6">
        <div className="flex items-center gap-2 mb-4">
          <h2 className="text-lg font-semibold text-white">Detailed Statistics</h2>
          <Tooltip text="Complete breakdown of all metrics for both agents. Compare total runs, averages, and success rates to make informed decisions about which agent to use.">
            <HelpCircle className="w-4 h-4 text-slate-400" />
          </Tooltip>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="border-b border-dark-700">
              <tr>
                <th className="text-left py-3 px-4 text-slate-400 font-semibold">Metric</th>
                <th className="text-center py-3 px-4 text-slate-400 font-semibold">{agent1}</th>
                <th className="text-center py-3 px-4 text-slate-400 font-semibold">{agent2}</th>
                <th className="text-center py-3 px-4 text-slate-400 font-semibold">Difference</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-700">
              <tr>
                <td className="py-3 px-4 text-slate-300">Total Runs</td>
                <td className="py-3 px-4 text-center text-white font-semibold">{stats1.total}</td>
                <td className="py-3 px-4 text-center text-white font-semibold">{stats2.total}</td>
                <td className="py-3 px-4 text-center text-slate-400">{stats1.total - stats2.total}</td>
              </tr>
              <tr>
                <td className="py-3 px-4 text-slate-300">Avg Precision</td>
                <td className="py-3 px-4 text-center text-white font-semibold">
                  {(stats1.avgPrecision * 100).toFixed(1)}%
                </td>
                <td className="py-3 px-4 text-center text-white font-semibold">
                  {(stats2.avgPrecision * 100).toFixed(1)}%
                </td>
                <td className="py-3 px-4 text-center">
                  <DifferenceIndicator
                    value={(stats1.avgPrecision - stats2.avgPrecision) * 100}
                    higherIsBetter={true}
                    format="percentage"
                  />
                </td>
              </tr>
              <tr>
                <td className="py-3 px-4 text-slate-300">Avg Faithfulness</td>
                <td className="py-3 px-4 text-center text-white font-semibold">
                  {(stats1.avgFaithfulness * 100).toFixed(1)}%
                </td>
                <td className="py-3 px-4 text-center text-white font-semibold">
                  {(stats2.avgFaithfulness * 100).toFixed(1)}%
                </td>
                <td className="py-3 px-4 text-center">
                  <DifferenceIndicator
                    value={(stats1.avgFaithfulness - stats2.avgFaithfulness) * 100}
                    higherIsBetter={true}
                    format="percentage"
                  />
                </td>
              </tr>
              <tr>
                <td className="py-3 px-4 text-slate-300">Avg Latency</td>
                <td className="py-3 px-4 text-center text-white font-semibold">
                  {stats1.avgLatency.toFixed(2)}s
                </td>
                <td className="py-3 px-4 text-center text-white font-semibold">
                  {stats2.avgLatency.toFixed(2)}s
                </td>
                <td className="py-3 px-4 text-center">
                  <DifferenceIndicator
                    value={stats1.avgLatency - stats2.avgLatency}
                    higherIsBetter={false}
                    format="seconds"
                  />
                </td>
              </tr>
              <tr>
                <td className="py-3 px-4 text-slate-300">Avg Cost</td>
                <td className="py-3 px-4 text-center text-white font-semibold">
                  ${stats1.avgCost.toFixed(4)}
                </td>
                <td className="py-3 px-4 text-center text-white font-semibold">
                  ${stats2.avgCost.toFixed(4)}
                </td>
                <td className="py-3 px-4 text-center">
                  <DifferenceIndicator
                    value={stats1.avgCost - stats2.avgCost}
                    higherIsBetter={false}
                    format="dollars"
                  />
                </td>
              </tr>
              <tr>
                <td className="py-3 px-4 text-slate-300">Success Rate</td>
                <td className="py-3 px-4 text-center text-white font-semibold">
                  {stats1.successRate.toFixed(1)}%
                </td>
                <td className="py-3 px-4 text-center text-white font-semibold">
                  {stats2.successRate.toFixed(1)}%
                </td>
                <td className="py-3 px-4 text-center">
                  <DifferenceIndicator
                    value={stats1.successRate - stats2.successRate}
                    higherIsBetter={true}
                    format="percentage"
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// Helper component for metric comparison cards
function MetricCard({
  title,
  icon: Icon,
  value1,
  value2,
  agent1,
  agent2,
  winner,
  format,
  higherIsBetter,
  tooltip,
}: {
  title: string;
  icon: any;
  value1: number;
  value2: number;
  agent1: string;
  agent2: string;
  winner: string;
  format: 'percentage' | 'seconds' | 'dollars';
  higherIsBetter: boolean;
  tooltip: string;
}) {
  const formatValue = (value: number) => {
    if (format === 'percentage') return `${(value * 100).toFixed(1)}%`;
    if (format === 'seconds') return `${value.toFixed(2)}s`;
    if (format === 'dollars') return `$${value.toFixed(4)}`;
    return value.toFixed(2);
  };

  const getColor = (value: number, isWinner: boolean) => {
    if (isWinner) return 'text-success-500';
    if (format === 'percentage') {
      if (value >= 0.8) return 'text-success-500';
      if (value >= 0.6) return 'text-warning-500';
      return 'text-critical-500';
    }
    return 'text-slate-300';
  };

  return (
    <div className="card p-6 border border-primary-500/20">
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="flex items-center gap-2">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{title}</p>
            <Tooltip text={tooltip}>
              <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
            </Tooltip>
          </div>
        </div>
        <Icon className="w-5 h-5 text-primary-400" />
      </div>

      <div className="space-y-3">
        {/* Agent 1 */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400">{agent1}</span>
            {winner === agent1 && <Crown className="w-3 h-3 text-yellow-400" />}
          </div>
          <span className={`text-lg font-bold ${getColor(value1, winner === agent1)}`}>
            {formatValue(value1)}
          </span>
        </div>

        {/* Agent 2 */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400">{agent2}</span>
            {winner === agent2 && <Crown className="w-3 h-3 text-yellow-400" />}
          </div>
          <span className={`text-lg font-bold ${getColor(value2, winner === agent2)}`}>
            {formatValue(value2)}
          </span>
        </div>

        {/* Difference */}
        <div className="pt-2 border-t border-dark-700">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500">Difference</span>
            <DifferenceIndicator
              value={value1 - value2}
              higherIsBetter={higherIsBetter}
              format={format}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

// Helper component for difference indicators
function DifferenceIndicator({
  value,
  higherIsBetter,
  format,
}: {
  value: number;
  higherIsBetter: boolean;
  format: 'percentage' | 'seconds' | 'dollars';
}) {
  const isPositive = value > 0;
  const isNegative = value < 0;
  const isNeutral = value === 0;

  // Determine if this is "good" based on direction and what's better
  const isGood = higherIsBetter ? isPositive : isNegative;
  const isBad = higherIsBetter ? isNegative : isPositive;

  const formatValue = (val: number) => {
    const absVal = Math.abs(val);
    if (format === 'percentage') return `${absVal.toFixed(1)}%`;
    if (format === 'seconds') return `${absVal.toFixed(2)}s`;
    if (format === 'dollars') return `$${absVal.toFixed(4)}`;
    return absVal.toFixed(2);
  };

  if (isNeutral) {
    return (
      <div className="flex items-center gap-1 text-slate-400">
        <Minus className="w-3 h-3" />
        <span className="text-xs font-semibold">0</span>
      </div>
    );
  }

  return (
    <div className={`flex items-center gap-1 ${isGood ? 'text-success-500' : isBad ? 'text-critical-500' : 'text-slate-400'}`}>
      {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
      <span className="text-xs font-semibold">{formatValue(value)}</span>
    </div>
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
    default:
      return new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString();
  }
}

// Estimate latency based on agent type (in seconds)
function estimateLatency(agentId: string): number {
  const latencyMap: Record<string, number> = {
    'gpt-4': 2.5,
    'gpt-3.5-turbo': 1.2,
    'claude-3-opus': 3.0,
    'claude-3-sonnet': 1.8,
    'gemini-pro': 2.0,
  };
  return latencyMap[agentId] || 1.5;
}

// Estimate cost based on agent type (in USD per query)
function estimateCost(agentId: string, query: string = ''): number {
  const queryLength = query.length || 100;
  const estimatedTokens = Math.ceil(queryLength / 4) + 500; // rough estimate

  const costPer1kTokens: Record<string, number> = {
    'gpt-4': 0.03,
    'gpt-3.5-turbo': 0.002,
    'claude-3-opus': 0.015,
    'claude-3-sonnet': 0.003,
    'gemini-pro': 0.0025,
  };

  const rate = costPer1kTokens[agentId] || 0.01;
  return (estimatedTokens / 1000) * rate;
}

function calculateStats(runs: any[]) {
  if (runs.length === 0) {
    return {
      total: 0,
      avgPrecision: 0,
      avgFaithfulness: 0,
      avgLatency: 0,
      avgCost: 0,
      successRate: 0,
    };
  }

  const total = runs.length;
  const avgPrecision = runs.reduce((acc, r) => acc + (r.precision || 0), 0) / total;
  const avgFaithfulness = runs.reduce((acc, r) => acc + (r.faithfulness || 0), 0) / total;

  // Calculate latency from actual data or estimates
  const avgLatency = runs.reduce((acc, r) => {
    return acc + (r.latency || estimateLatency(r.agent_id));
  }, 0) / total;

  // Calculate cost from actual data or estimates
  const avgCost = runs.reduce((acc, r) => {
    return acc + (r.cost || estimateCost(r.agent_id, r.query));
  }, 0) / total;

  const successful = runs.filter((r) => r.precision && r.precision > 0.7).length;
  const successRate = (successful / total) * 100;

  return {
    total,
    avgPrecision,
    avgFaithfulness,
    avgLatency,
    avgCost,
    successRate,
  };
}
