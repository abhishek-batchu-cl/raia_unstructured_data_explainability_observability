# RAIA - Responsible AI Analytics

A sophisticated enterprise-grade React application for evaluating and monitoring Agentic AI systems. RAIA provides comprehensive analysis of AI output quality, performance, robustness, safety, user experience, and regulatory compliance.

![RAIA Dashboard](https://img.shields.io/badge/Status-Active-success)
![React](https://img.shields.io/badge/React-18+-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue)
![Tailwind](https://img.shields.io/badge/Tailwind-3.0+-06B6D4)

## 🎯 Features

### Core Capabilities
- **📊 Dashboard** - Comprehensive AI health monitoring with real-time metrics
- **✅ Output Quality Analysis** - 10 metrics evaluating response quality, correctness, and faithfulness
- **⚡ Performance Metrics** - Latency, throughput, cost analysis, and tool interaction monitoring
- **🛡️ Robustness & Reliability** - Consistency analysis and adversarial testing
- **🔒 Safety & Ethics** - Bias detection, harmful content monitoring, and fairness assessment
- **👥 User Experience** - NPS, CSAT scores, and interaction pattern analysis
- **📋 Compliance Center** - Multi-framework regulatory compliance (EU AI Act, GDPR, HIPAA, DPDP)
- **📈 Evaluation History** - Historical data tracking and trend analysis
- **🔄 Agent Comparison** - Side-by-side comparison of up to 4 agent versions
- **📄 Reports & Export** - Professional report generation in PDF, Excel, JSON, and CSV formats

### UI/UX Features
- 🌓 Dark/Light mode support
- 📱 Fully responsive design (mobile, tablet, desktop)
- ♿ WCAG 2.1 AA accessibility compliant
- 🎨 Beautiful data visualizations with Recharts and D3.js
- ⚡ Fast and optimized performance
- 🎯 Intuitive navigation and filtering

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm 9+
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Installation

1. **Clone the repository**
   ```bash
   cd raia-frontend
   ```

2. **Install dependencies**
   ```bash
   npm install --legacy-peer-deps
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

4. **Open your browser**
   Navigate to [http://localhost:5173](http://localhost:5173)

### Build for Production

```bash
npm run build
```

The optimized build will be created in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## 📁 Project Structure

```
raia-frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # Reusable UI components (shadcn/ui)
│   │   ├── layout/          # Layout components (Navbar, Sidebar)
│   │   ├── charts/          # Reusable chart components
│   │   ├── metrics/         # Metric card components
│   │   └── shared/          # Shared components (Filters, Search)
│   ├── pages/               # Page components (Dashboard, Metrics pages)
│   ├── hooks/               # Custom React hooks
│   ├── lib/                 # Utilities and helpers
│   ├── store/               # Zustand state management stores
│   ├── types/               # TypeScript type definitions
│   ├── data/                # Mock data and constants
│   ├── App.tsx              # Main App component with routing
│   ├── main.tsx             # Application entry point
│   └── index.css            # Global styles and Tailwind imports
├── public/                  # Static assets
├── index.html               # HTML template
├── package.json             # Dependencies and scripts
├── tailwind.config.js       # Tailwind CSS configuration
├── tsconfig.json            # TypeScript configuration
└── vite.config.ts           # Vite configuration
```

## 🛠️ Technology Stack

### Core Framework
- **React 18+** - UI library with TypeScript
- **Vite** - Build tooling and dev server
- **React Router v6** - Client-side routing

### UI & Styling
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Component library (Radix UI primitives)
- **Framer Motion** - Animation library
- **Lucide React** - Icon library

### Data Visualization
- **Recharts** - Primary charting library (line, bar, area, pie, radar)
- **D3.js** - Advanced custom visualizations (Sankey, heatmaps)
- **react-gauge-chart** - Gauge/radial charts

### State Management & Data
- **Zustand** - Lightweight state management
- **TanStack Query (React Query)** - Data fetching and caching
- **date-fns** - Date manipulation

### Utilities
- **zod** - Schema validation
- **clsx / tailwind-merge** - Conditional styling
- **react-hot-toast** - Toast notifications
- **jsPDF + html2canvas** - PDF export
- **xlsx** - Excel export

## 🎨 Brand Identity

### Colors
- **Primary (Indigo)**: `#6366f1` - Trust, intelligence
- **Secondary (Violet)**: `#8b5cf6` - Innovation
- **Success (Emerald)**: `#10b981` - Scores ≥ 80%
- **Warning (Amber)**: `#f59e0b` - Scores 50-79%
- **Critical (Rose)**: `#f43f5e` - Scores < 50%
- **Neutral (Slate)**: `#64748b` - Text and UI elements

### Typography
- **Headings**: Inter Bold
- **Body**: Inter Regular
- **Metrics/Code**: JetBrains Mono

## 📊 Metrics Overview

### Category 1: Output Quality & Accuracy (10 metrics)
- Correctness/Completeness
- Helpfulness
- Coherence & Fluency
- Simplicity
- Relevance
- Collaborativity
- Information Following
- Factual Accuracy
- Hallucination Rate/Faithfulness
- Overall Response Quality

### Category 2: Performance & Efficiency (5 metrics)
- Latency/Response Time
- Throughput
- Cost-per-Interaction
- Success Rate/Task Completion
- Tool Interactions

### Category 3: Robustness & Reliability (3 metrics)
- Consistency
- Error Rate
- Resilience to Adversarial Attacks

### Category 4: Safety & Ethical (4 metrics)
- Bias Detection
- Harmful Content Generation
- Fairness
- Writing Style and Tone

### Category 5: User Experience (2 metrics)
- User Satisfaction (CSAT/NPS)
- Turn Count

### Category 6: Compliance (5 frameworks)
- EU AI Act
- GDPR
- HIPAA
- DPDP (India)
- AICI (Overall)

## 🧪 Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Code Quality

The project uses:
- ESLint for code linting
- TypeScript for type safety
- Prettier (recommended) for code formatting

## 🌐 Browser Support

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)

## 🔒 Security

This application is designed for enterprise use with:
- Type-safe data handling
- Input validation with Zod
- Secure state management
- No sensitive data exposure

## 📈 Performance

Target metrics:
- **First Contentful Paint**: < 1.5s
- **Time to Interactive**: < 3s
- **Lighthouse Score**: > 90

Optimization strategies:
- Code splitting per route
- Lazy loading of heavy components
- Memoization of expensive calculations
- Optimized chart rendering

## 🤝 Contributing

This is an enterprise application. For contributions:

1. Follow the existing code structure
2. Maintain TypeScript strict mode
3. Write meaningful commit messages
4. Test across different screen sizes
5. Ensure accessibility compliance

## 📝 License

Copyright © 2024 RAIA Team. All rights reserved.

## 🙏 Acknowledgments

Built with:
- React Team for the amazing framework
- Tailwind Labs for Tailwind CSS
- Recharts contributors
- shadcn for the component library
- All open-source contributors

---

**🎯 RAIA** - Setting the standard for AI evaluation interfaces
