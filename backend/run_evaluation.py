import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.evaluation import evaluate


if __name__ == "__main__":
    summary = evaluate()
    print("ITS Agent MVP evaluation complete")
    print(f"route_accuracy={summary['route_accuracy']:.2%}")
    print(f"tool_success_rate={summary['tool_success_rate']:.2%}")
    print(f"average_quality_score={summary['average_quality_score']:.2f}")
