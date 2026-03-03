param(
    [string]$ConfigPath = ".\config\swarm_config.json"
)

Write-Host "[Fractal Swarm] Installing requirements..."
pip install -r requirements.txt

Write-Host "[Fractal Swarm] Running swarm..."
python run_swarm.py

Write-Host "[Fractal Swarm] Harvesting + pruning..."
python scripts\pruning.py

Write-Host "[Fractal Swarm] Done. Harvest file: swarm_harvest.jsonl"
