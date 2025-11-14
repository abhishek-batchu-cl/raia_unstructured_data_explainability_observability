"""
Test all RAIA backend endpoints
Verify that all metrics are available
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, description, headers=None, data=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            print(f"✅ {description}")
            print(f"   GET {endpoint}")
            return True
        else:
            print(f"❌ {description}")
            print(f"   GET {endpoint}")
            print(f"   Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {description}")
        print(f"   GET {endpoint}")
        print(f"   Error: {str(e)}")
        return False


def main():
    """Test all endpoints"""
    print("="*80)
    print("  RAIA Backend Endpoint Verification")
    print("="*80)
    print()

    results = {}

    # Core endpoints
    print("📊 Core Endpoints:")
    results['health'] = test_endpoint("GET", "/health", "System Health")
    results['dashboard'] = test_endpoint("GET", "/api/dashboard", "Dashboard Summary")
    print()

    # Enterprise endpoints (NEW)
    print("🏢 Enterprise Endpoints:")
    results['enterprise_metrics'] = test_endpoint("GET", "/api/metrics/dashboard", "Enterprise Metrics")
    results['recent_runs'] = test_endpoint("GET", "/api/runs?limit=5", "Recent Runs")
    print()

    # Event ingestion endpoints (NEW)
    print("📨 Event Ingestion Endpoints:")
    headers = {"Authorization": "Bearer demo-api-key"}
    results['event_stats'] = test_endpoint("GET", "/api/events/stats", "Event Statistics", headers=headers)
    results['event_health'] = test_endpoint("GET", "/api/events/health", "Event Ingestion Health")
    print()

    # RAG Metrics
    print("🔍 RAG Metrics Endpoints:")
    results['retrieval'] = test_endpoint("GET", "/api/retrieval?limit=5", "Retrieval Metrics")
    results['answer_quality'] = test_endpoint("GET", "/api/answer-quality?limit=5", "Answer Quality")
    results['semantic'] = test_endpoint("GET", "/api/semantic?limit=5", "Semantic Scores")
    print()

    # Agent Metrics
    print("🤖 Agent Metrics Endpoints:")
    results['agent_exec'] = test_endpoint("GET", "/api/agent/executions?limit=5", "Agent Executions")
    results['agent_decisions'] = test_endpoint("GET", "/api/agent/decisions?limit=5", "Agent Decisions")
    results['node_metrics'] = test_endpoint("GET", "/api/node-metrics?limit=5", "Node Metrics")
    results['pipeline'] = test_endpoint("GET", "/api/pipeline?limit=5", "Pipeline Metrics")
    print()

    # Monitoring
    print("📈 Monitoring Endpoints:")
    results['drift'] = test_endpoint("GET", "/api/monitoring/drift?limit=5", "Embedding Drift")
    results['vector_health'] = test_endpoint("GET", "/api/monitoring/vector-health", "Vector Health")
    results['signals'] = test_endpoint("GET", "/api/monitoring/signals?limit=5", "Functional Signals")
    print()

    # What-If Analysis
    print("💡 What-If Analysis Endpoints:")
    results['counterfactuals'] = test_endpoint("GET", "/api/whatif/counterfactuals?limit=5", "Counterfactuals")
    results['sensitivity'] = test_endpoint("GET", "/api/whatif/sensitivity?limit=5", "Sensitivity Analysis")
    results['optimization'] = test_endpoint("GET", "/api/whatif/optimization?limit=5", "Optimization Recommendations")
    print()

    # Analytics
    print("📊 Analytics Endpoints:")
    results['timeseries'] = test_endpoint("GET", "/api/analytics/timeseries?metric_name=precision_at_k&hours=24", "Timeseries Data")
    print()

    # Summary
    print("="*80)
    total = len(results)
    passed = sum(results.values())
    failed = total - passed

    print(f"  Results: {passed}/{total} endpoints working")
    if failed > 0:
        print(f"  ❌ {failed} endpoints failed")
    else:
        print(f"  ✅ All endpoints working!")
    print("="*80)
    print()

    # List failed endpoints
    if failed > 0:
        print("Failed endpoints:")
        for endpoint, success in results.items():
            if not success:
                print(f"  ❌ {endpoint}")
        print()

    # Next steps
    if failed == 0:
        print("🎉 All metrics are available!")
        print()
        print("Next steps:")
        print("1. Start frontend: cd frontend && npm run dev")
        print("2. Access Enterprise Dashboard: http://localhost:5173/enterprise")
        print("3. View API docs: http://localhost:8000/api/docs")
    else:
        print("⚠️  Some endpoints are not available.")
        print("Make sure:")
        print("1. Backend is running: python backend/main.py")
        print("2. Database files exist")
        print("3. All dependencies are installed")


if __name__ == "__main__":
    main()
