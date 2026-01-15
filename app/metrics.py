from collections import defaultdict

http_requests = defaultdict(int)
webhook_results = defaultdict(int)

def render_metrics():
    lines = []
    for k, v in http_requests.items():
        path, status = k
        lines.append(f'http_requests_total{{path="{path}",status="{status}"}} {v}')
    for k, v in webhook_results.items():
        lines.append(f'webhook_requests_total{{result="{k}"}} {v}')
    return "\n".join(lines)
