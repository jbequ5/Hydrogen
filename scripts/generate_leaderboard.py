"""Generate beautiful per-challenge leaderboards.

Creates HTML dashboards showing wallet/hotkey and score for each challenge.
Run this periodically to update the public leaderboards.
"""

import json
import os
from datetime import datetime

from hydrogen.landscape.causal_knowledge_base import CausalKnowledgeBase


CHALLENGES = [
    "poisson_2d_v1",
    "darcy_2d_v1",
    "burgers_v1",
    "heat_v1",
    "elasticity_2d_v1",
    "ns_2d_laminar_v1",
]


def generate_leaderboard_html(challenge_id: str, scores: list) -> str:
    """Generate a clean, modern HTML leaderboard for one challenge."""
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Hydrogen Leaderboard - {challenge_id}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            margin: 0;
            padding: 40px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        h1 {{
            color: #60a5fa;
            margin-bottom: 8px;
        }}
        .subtitle {{
            color: #94a3b8;
            margin-bottom: 32px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: #1e2937;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.3);
        }}
        th, td {{
            padding: 16px 24px;
            text-align: left;
        }}
        th {{
            background: #334155;
            color: #cbd5e1;
            font-weight: 600;
        }}
        tr:nth-child(even) {{
            background: #1e2937;
        }}
        tr:hover {{
            background: #334155;
        }}
        .rank {{
            font-weight: 700;
            color: #60a5fa;
            width: 60px;
        }}
        .wallet {{
            font-family: ui-monospace, monospace;
            color: #e0f2fe;
        }}
        .score {{
            font-weight: 600;
            color: #4ade80;
        }}
        .updated {{
            margin-top: 24px;
            color: #64748b;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Hydrogen Leaderboard</h1>
        <div class="subtitle">Challenge: {challenge_id}</div>

        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Wallet / Hotkey</th>
                    <th>Score</th>
                </tr>
            </thead>
            <tbody>
    """

    for i, entry in enumerate(scores[:50], 1):  # Top 50
        wallet = entry.get("wallet", entry.get("hotkey", "unknown"))[:12] + "..."
        score = entry.get("score", 0)
        html += f"""
                <tr>
                    <td class="rank">#{i}</td>
                    <td class="wallet">{wallet}</td>
                    <td class="score">{score:.4f}</td>
                </tr>
        """

    html += f"""
            </tbody>
        </table>

        <div class="updated">
            Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
        </div>
    </div>
</body>
</html>
    """
    return html


def main():
    output_dir = "./data/leaderboards"
    os.makedirs(output_dir, exist_ok=True)

    # In a real system this would come from on-chain scores or validator logs
    # For now we generate placeholder beautiful leaderboards
    for challenge_id in CHALLENGES:
        # Placeholder data - replace with real scores later
        placeholder_scores = [
            {"wallet": f"5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKuty", "score": 0.124 + i*0.001}
            for i in range(20)
        ]

        html = generate_leaderboard_html(challenge_id, placeholder_scores)

        filepath = os.path.join(output_dir, f"{challenge_id}_leaderboard.html")
        with open(filepath, "w") as f:
            f.write(html)

        print(f"Generated leaderboard: {filepath}")

    print(f"\nLeaderboards saved to: {output_dir}")


if __name__ == "__main__":
    main()
