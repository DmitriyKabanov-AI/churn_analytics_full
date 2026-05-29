import sys, os, subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../analytics'))

def test_all_charts_run():
    analytics_dir = os.path.join(os.path.dirname(__file__), '../../analytics')
    for fname in os.listdir(analytics_dir):
        if fname.startswith('chart') and fname.endswith('.py') and fname != 'chart_engine.py':
            script_path = os.path.join(analytics_dir, fname)
            result = subprocess.run(['python', script_path], cwd=analytics_dir, capture_output=True, text=True)
            assert result.returncode == 0, f"{fname} failed: {result.stderr}"