"""Generate beautiful per-challenge + combined leaderboards.

Supports real score data (when wired) and produces modern dark-themed dashboards.
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
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&amp;family=Space+Grotesk:wght@500;600&amp;display=swap');

        body {{
            font-family: 'Inter', system_ui, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            margin: 0;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
        }}
        h1 {{
            font-family: 'Space Grotesk', sans-serif;
            color: #60a5fa;
            font-size: 2.25rem;
            margin-bottom: 8px;
            font-weight: 600;
        }}
        .subtitle {{
            color: #64748b;
            font-size: 1.1rem;
            margin-bottom: 32px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: #1e2937;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
        }}
        th, td {{
            padding: 18px 24px;
            text-align: left;
        }}
        th {{
            background: #334155;
            color: #94a3b8;
            font-weight: 600;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        tr {{
            border-bottom: 1px solid #334155;
        }}
        tr:last-child {{
            border-bottom: none;
        }}
        tr:hover {{
            background: #334155;
        }}
        .rank {{
            font-weight: 700;
            color: #64748b;
            width: 70px;
        }}
        .wallet {{
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            color: #bae6fd;
            font-size: 0.95rem;
        }}
        .score {{
            font-weight: 700;
            color: #4ade80;
            font-size: 1.05rem;
        }}
        .improvement {{
            color: #a5b4fc;
            font-weight: 500;
        }}
        .source {{
            color: #64748b;
            font-size: 0.85rem;
        }}
        .updated {{
            margin-top: 32px;
            color: #475569;
            font-size: 0.9rem;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            margin-bottom: 24px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>Hydrogen Leaderboard</h1>
                <div class="subtitle">{challenge_id}</div>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Wallet / Hotkey</th>
                    <th>Score</th>
                    <th>Improvement</th>
                    <th>Data Source</th>
                </tr>
            </thead>
            <tbody>
    """

    for i, entry in enumerate(scores[:50], 1):
        wallet = str(entry.get("wallet", entry.get("hotkey", "unknown")))[:14] + "..."
        score = entry.get("score", 0)
        improvement = entry.get("improvement", 0)
        source = entry.get("data_source", "unknown")

        html += f"""
                <tr>
                    <td class="rank">#{i}</td>
                    <td class="wallet">{wallet}</td>
                    <td class="score">{score:.4f}</td>
                    <td class="improvement">{improvement:+.4f}</td>
                    <td class="source">{source}</td>
                </tr>
        """

    html += f"""
            </tbody>
        </table>

        <div class="updated">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
        </div>
    </div>
</body>
</html>
    """
    return html


def generate_combined_dashboard(all_leaderboards: dict) -> str:
    """Generate a single beautiful dashboard showing all challenges."""
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Hydrogen Leaderboards</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&amp;family=Space+Grotesk:wght@500;600&amp;display=swap');

        body {{
            font-family: 'Inter', system_ui, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            margin: 0;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        h1 {{
            font-family: 'Space Grotesk', sans-serif;
            color: #60a5fa;
            font-size: 2.5rem;
            margin-bottom: 12px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(520px, 1fr));
            gap: 32px;
        }}
        .card {{
            background: #1e2937;
            border-radius: 20px;
            padding: 28px;
            box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1);
        }}
        .card h2 {{
            margin: 0 0 20px 0;
            color: #bae6fd;
            font-size: 1.35rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Hydrogen Leaderboards</h1>
        <p style="color:#64748b; margin-bottom:40px;">Live performance across all challenges</p>

        <div class="grid">
    """

    for challenge_id, scores in all_leaderboards.items():
        # Mini table for combined view
        mini_html = ""
        for i, entry in enumerate(scores[:8], 1):
            wallet = str(entry.get("wallet", ""))[:12] + "..."
            score = entry.get("score", 0)
            mini_html += f"<div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #334155;'><span>#{i} {wallet}</span><span style='color:#4ade80;font-weight:600;'>{score:.4f}</span></div>"

        html += f"""
            <div class="card">
                <h2>{challenge_id}</h2>
                {mini_html}
                <div style="margin-top:16px; text-align:right;">
                    <a href="{challenge_id}_leaderboard.html" style="color:#60a5fa; text-decoration:none; font-size:0.95rem;">View full leaderboard →</a>
                </div>
            </div>
        """

    html += """
        </div>
    </div>
</body>
</html>
    """
    return html


def main():
    output_dir = "./data/leaderboards"
    os.makedirs(output_dir, exist_ok=True)

    all_leaderboards = {}

    for challenge_id in CHALLENGES:
        # TODO: Replace with real data from validator / on-chain
        placeholder_scores = [
            {
                "wallet": f"5GrwvaEF5zXb26Fz9rcQpDWS{i:02d}CtERHpNehXCPcNoHGKuty",
                "score": round(0.085 + i * 0.0045, 4),
                "improvement": round(0.012 + i * 0.0012, 4),
                "data_source": "pdebench" if i % 2 == 0 else "synthetic",
            }
            for i in range(25)
        ]

        html = generate_leaderboard_html(challenge_id, placeholder_scores)
        filepath = os.path.join(output_dir, f"{challenge_id}_leaderboard.html")
        with open(filepath, "w") as f:
            f.write(html)

        all_leaderboards[challenge_id] = placeholder_scores
        print(f"Generated: {filepath}")

    # Combined dashboard
    combined_html = generate_combined_dashboard(all_leaderboards)
    combined_path = os.path.join(output_dir, "combined_dashboard.html")
    with open(combined_path, "w") as f:
        f.write(combined_html)

    print(f"\nCombined dashboard: {combined_path}")
    print("Leaderboards generated successfully.")


if __name__ == "__main__":
    main()
