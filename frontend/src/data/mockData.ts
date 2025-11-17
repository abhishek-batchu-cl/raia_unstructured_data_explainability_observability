import { format, subDays, subWeeks } from 'date-fns';
import type {
  Evaluation,
  Agent,
  Metric,
  CategoryScore,
  Alert,
  ComplianceFramework,
  PerformanceMetrics,
  UserExperienceMetrics,
} from '../types';

// Helper function to generate random score
function randomScore(min: number, max: number): number {
  return Math.random() * (max - min) + min;
}

// Helper function to generate random integer
function randomInt(min: number, max: number): number {
  return Math.floor(randomScore(min, max + 1));
}

// Generate agents
export const mockAgents: Agent[] = [
  {
    id: 'agent-1',
    name: 'RAIA Assistant',
    version: 'v1.0',
    description: 'Initial release of the AI assistant',
    releaseDate: new Date('2024-07-01'),
  },
  {
    id: 'agent-2',
    name: 'RAIA Assistant',
    version: 'v1.1',
    description: 'Minor improvements and bug fixes',
    releaseDate: new Date('2024-08-15'),
  },
  {
    id: 'agent-3',
    name: 'RAIA Assistant',
    version: 'v2.0',
    description: 'Major update with enhanced capabilities',
    releaseDate: new Date('2024-09-20'),
  },
  {
    id: 'agent-4',
    name: 'RAIA Assistant',
    version: 'v2.1',
    description: 'Performance optimizations and safety improvements',
    releaseDate: new Date('2024-10-10'),
  },
];

// Output Quality metrics definitions
const outputQualityMetrics = [
  {
    id: 'correctness',
    name: 'Correctness/Completeness',
    definition: 'Measures how accurate and complete the response is',
    owner: 'Pramila',
    scoringMethod: '1-5' as const,
  },
  {
    id: 'helpfulness',
    name: 'Helpfulness',
    definition: 'Evaluates how helpful the response is to the user',
    owner: 'Pramila',
    scoringMethod: '1-5' as const,
  },
  {
    id: 'coherence',
    name: 'Coherence & Fluency',
    definition: 'Assesses how well-structured and fluent the response is',
    owner: 'Pramila',
    scoringMethod: '1-5' as const,
  },
  {
    id: 'simplicity',
    name: 'Simplicity',
    definition: 'Measures how simple and understandable the response is',
    owner: 'Pramila',
    scoringMethod: '1-5' as const,
  },
  {
    id: 'relevance',
    name: 'Relevance',
    definition: 'Evaluates how relevant the response is to the query',
    owner: 'Pramila',
    scoringMethod: '1-5' as const,
  },
  {
    id: 'collaborativity',
    name: 'Collaborativity',
    definition: 'Measures collaborative nature of interactions',
    owner: 'Pramila',
    scoringMethod: '1-5' as const,
  },
  {
    id: 'info-following',
    name: 'Information Following',
    definition: 'Assesses adherence to provided instructions',
    owner: 'Pramila',
    scoringMethod: '1-5' as const,
  },
  {
    id: 'factual-accuracy',
    name: 'Factual Accuracy',
    definition: 'Measures factual correctness of the response',
    owner: 'Nipun',
    scoringMethod: '0-100' as const,
  },
  {
    id: 'hallucination-rate',
    name: 'Hallucination Rate/Faithfulness',
    definition: 'Inverse measure of factual errors and hallucinations',
    owner: 'Nipun',
    scoringMethod: '0-100' as const,
  },
  {
    id: 'overall-quality',
    name: 'Overall Response Quality',
    definition: 'Composite score of overall response quality',
    owner: 'Nipun',
    scoringMethod: '1-5' as const,
  },
];

// Performance metrics definitions
const performanceMetrics = [
  {
    id: 'latency',
    name: 'Latency/Response Time',
    definition: 'Time taken to generate a response',
    owner: 'Mukund',
    scoringMethod: 'ms' as const,
  },
  {
    id: 'throughput',
    name: 'Throughput',
    definition: 'Number of requests processed per minute',
    owner: 'Pramila',
    scoringMethod: '0-100' as const,
  },
  {
    id: 'cost',
    name: 'Cost-per-Interaction',
    definition: 'Average cost per user interaction',
    owner: 'Mukund',
    scoringMethod: 'dollar' as const,
  },
  {
    id: 'success-rate',
    name: 'Success Rate/Task Completion',
    definition: 'Percentage of successfully completed tasks',
    owner: 'Pramila',
    scoringMethod: '0-100' as const,
  },
  {
    id: 'tool-interactions',
    name: 'Tool Interactions',
    definition: 'Number of tool calls made',
    owner: 'Mukund',
    scoringMethod: 'count' as const,
  },
];

// Robustness metrics definitions
const robustnessMetrics = [
  {
    id: 'consistency',
    name: 'Consistency',
    definition: 'Variance in responses for similar inputs',
    owner: 'Pramila',
    scoringMethod: '1-5' as const,
  },
  {
    id: 'error-rate',
    name: 'Error Rate',
    definition: 'Percentage of interactions with errors',
    owner: 'Pramila',
    scoringMethod: '0-100' as const,
  },
  {
    id: 'adversarial-resilience',
    name: 'Resilience to Adversarial Attacks',
    definition: 'Resistance to malicious inputs and jailbreaks',
    owner: 'Pramila',
    scoringMethod: '1-5' as const,
  },
];

// Safety metrics definitions
const safetyMetrics = [
  {
    id: 'bias-detection',
    name: 'Bias Detection',
    definition: 'Detection of biases in responses',
    owner: 'Pramila',
    scoringMethod: '1-5' as const,
  },
  {
    id: 'harmful-content',
    name: 'Harmful Content Generation',
    definition: 'Rate of harmful or inappropriate content',
    owner: 'Pramila',
    scoringMethod: '1-5' as const,
  },
  {
    id: 'fairness',
    name: 'Fairness',
    definition: 'Equitable treatment across user groups',
    owner: 'Pramila',
    scoringMethod: '1-5' as const,
  },
  {
    id: 'tone',
    name: 'Writing Style and Tone',
    definition: 'Appropriateness of tone and style',
    owner: 'Pramila',
    scoringMethod: '1-5' as const,
  },
];

// User Experience metrics definitions
const uxMetrics = [
  {
    id: 'user-satisfaction',
    name: 'User Satisfaction (CSAT/NPS)',
    definition: 'Overall user satisfaction score',
    owner: 'Chetan',
    scoringMethod: '1-5' as const,
  },
  {
    id: 'turn-count',
    name: 'Turn Count',
    definition: 'Average number of turns per conversation',
    owner: 'Chetan',
    scoringMethod: 'count' as const,
  },
];

// Function to generate metrics for a category
function generateMetrics(
  metricDefinitions: typeof outputQualityMetrics,
  category: string,
  version: string
): Metric[] {
  // Scores improve with version
  const versionMultiplier = {
    'v1.0': 0.7,
    'v1.1': 0.8,
    'v2.0': 0.9,
    'v2.1': 1.0,
  }[version] || 1.0;

  return metricDefinitions.map((def) => {
    let score: number;

    if (def.scoringMethod === '1-5') {
      score = randomScore(3, 5) * versionMultiplier;
      score = Math.min(5, Math.max(1, score));
    } else if (def.scoringMethod === '0-100') {
      score = randomScore(60, 95) * versionMultiplier;
      score = Math.min(100, Math.max(0, score));
    } else if (def.scoringMethod === 'ms') {
      score = randomScore(200, 800) / versionMultiplier; // Lower is better
    } else if (def.scoringMethod === 'dollar') {
      score = randomScore(0.05, 0.25) / versionMultiplier; // Lower is better
    } else {
      // count
      score = randomScore(2, 8);
    }

    return {
      id: def.id,
      name: def.name,
      category: category as any,
      score,
      scoringMethod: def.scoringMethod,
      owner: def.owner,
      definition: def.definition,
      calculationMethod: 'Automated evaluation using AI models',
    };
  });
}

// Function to calculate category score from metrics
function calculateCategoryScore(metrics: Metric[]): number {
  const validMetrics = metrics.filter(
    (m) => m.scoringMethod === '1-5' || m.scoringMethod === '0-100'
  );

  const sum = validMetrics.reduce((acc, metric) => {
    if (metric.scoringMethod === '1-5') {
      return acc + (metric.score / 5) * 100;
    }
    return acc + metric.score;
  }, 0);

  return sum / validMetrics.length;
}

// Generate category scores
function generateCategoryScores(version: string): CategoryScore[] {
  const outputQuality = generateMetrics(outputQualityMetrics, 'output_quality', version);
  const performance = generateMetrics(performanceMetrics, 'performance', version);
  const robustness = generateMetrics(robustnessMetrics, 'robustness', version);
  const safety = generateMetrics(safetyMetrics, 'safety', version);
  const ux = generateMetrics(uxMetrics, 'user_experience', version);

  return [
    {
      category: 'output_quality',
      score: calculateCategoryScore(outputQuality),
      metrics: outputQuality,
      trend: 'up' as const,
      percentChange: randomScore(1, 5),
    },
    {
      category: 'performance',
      score: calculateCategoryScore(performance),
      metrics: performance,
      trend: 'up' as const,
      percentChange: randomScore(2, 6),
    },
    {
      category: 'robustness',
      score: calculateCategoryScore(robustness),
      metrics: robustness,
      trend: 'stable' as const,
      percentChange: 0,
    },
    {
      category: 'safety',
      score: calculateCategoryScore(safety),
      metrics: safety,
      trend: 'up' as const,
      percentChange: randomScore(1, 4),
    },
    {
      category: 'user_experience',
      score: calculateCategoryScore(ux),
      metrics: ux,
      trend: 'up' as const,
      percentChange: randomScore(3, 7),
    },
  ];
}

// Generate evaluations
export function generateMockEvaluations(): Evaluation[] {
  const evaluations: Evaluation[] = [];
  let idCounter = 1;

  // Generate 50 evaluations over 3 months
  for (let i = 0; i < 50; i++) {
    const daysAgo = Math.floor((i / 50) * 90);
    const timestamp = subDays(new Date(), daysAgo);

    // Determine which agent version based on date
    let agentVersion = 'v1.0';
    let agentId = 'agent-1';

    if (daysAgo < 10) {
      agentVersion = 'v2.1';
      agentId = 'agent-4';
    } else if (daysAgo < 30) {
      agentVersion = 'v2.0';
      agentId = 'agent-3';
    } else if (daysAgo < 60) {
      agentVersion = 'v1.1';
      agentId = 'agent-2';
    }

    const categoryScores = generateCategoryScores(agentVersion);
    const overallScore =
      categoryScores.reduce((acc, cat) => acc + cat.score, 0) / categoryScores.length;

    // Generate alerts for low scores
    const alerts: Alert[] = [];
    categoryScores.forEach((cat) => {
      cat.metrics.forEach((metric) => {
        const normalizedScore =
          metric.scoringMethod === '1-5' ? (metric.score / 5) * 100 : metric.score;

        if (normalizedScore < 50 && Math.random() > 0.7) {
          alerts.push({
            id: `alert-${idCounter++}`,
            severity: 'critical',
            message: `${metric.name} score is critically low: ${normalizedScore.toFixed(1)}`,
            metricId: metric.id,
            timestamp,
            dismissed: false,
          });
        } else if (normalizedScore < 70 && Math.random() > 0.8) {
          alerts.push({
            id: `alert-${idCounter++}`,
            severity: 'warning',
            message: `${metric.name} score needs attention: ${normalizedScore.toFixed(1)}`,
            metricId: metric.id,
            timestamp,
            dismissed: false,
          });
        }
      });
    });

    evaluations.push({
      id: `eval-${String(idCounter++).padStart(3, '0')}`,
      timestamp,
      agentId,
      agentVersion,
      overallScore,
      categoryScores,
      alerts,
      status: 'completed',
    });
  }

  return evaluations.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
}

// Generate compliance frameworks
export function generateComplianceFrameworks(): ComplianceFramework[] {
  return [
    {
      id: 'eu-ai-act',
      name: 'EU AI Act',
      acronym: 'EU AI Act',
      score: randomScore(72, 80),
      pillars: [
        { name: 'Transparency', score: randomScore(70, 85) },
        { name: 'Fairness', score: randomScore(75, 88) },
        { name: 'Robustness', score: randomScore(68, 82) },
        { name: 'Human Oversight', score: randomScore(72, 86) },
        { name: 'Accuracy', score: randomScore(74, 84) },
      ],
      status: 'at_risk',
    },
    {
      id: 'gdpr',
      name: 'General Data Protection Regulation',
      acronym: 'GDPR',
      score: randomScore(78, 88),
      pillars: [
        { name: 'Data Privacy', score: randomScore(80, 90) },
        { name: 'User Control', score: randomScore(75, 88) },
        { name: 'Lawful Processing', score: randomScore(78, 90) },
        { name: 'Explainability', score: randomScore(72, 85) },
      ],
      status: 'compliant',
    },
    {
      id: 'hipaa',
      name: 'Health Insurance Portability and Accountability Act',
      acronym: 'HIPAA',
      score: randomScore(85, 95),
      pillars: [
        { name: 'Data Protection', score: randomScore(88, 96) },
        { name: 'Privacy', score: randomScore(85, 94) },
        { name: 'Reliability', score: randomScore(82, 92) },
        { name: 'Safety', score: randomScore(87, 95) },
      ],
      status: 'compliant',
    },
    {
      id: 'dpdp',
      name: 'Digital Personal Data Protection Act',
      acronym: 'DPDP (India)',
      score: randomScore(76, 86),
      pillars: [
        { name: 'Consent', score: randomScore(78, 88) },
        { name: 'Fairness', score: randomScore(74, 86) },
        { name: 'Non-harmful Content', score: randomScore(76, 88) },
        { name: 'Transparency', score: randomScore(72, 84) },
      ],
      status: 'compliant',
    },
    {
      id: 'aici',
      name: 'AI Compliance Index',
      acronym: 'AICI',
      score: randomScore(78, 88),
      pillars: [
        { name: 'EU AI Act', score: randomScore(72, 80) },
        { name: 'GDPR', score: randomScore(78, 88) },
        { name: 'HIPAA', score: randomScore(85, 95) },
        { name: 'DPDP', score: randomScore(76, 86) },
      ],
      status: 'compliant',
    },
  ];
}

// Export generated data
export const mockEvaluations = generateMockEvaluations();
export const mockCompliance = generateComplianceFrameworks();
