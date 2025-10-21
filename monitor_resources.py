#!/usr/bin/env python3
"""Real-time resource monitoring for M3 Max during workflows"""
import psutil
import time
import os

def format_bytes(bytes):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.1f}{unit}"
        bytes /= 1024
    return f"{bytes:.1f}TB"

def monitor_loop(interval=2):
    """Monitor system resources in real-time"""
    print("\n🍎 M3 Max Resource Monitor")
    print("="*80)
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1, percpu=False)
            cpu_per_core = psutil.cpu_percent(interval=0, percpu=True)
            
            # Memory
            mem = psutil.virtual_memory()
            mem_used_gb = mem.used / (1024**3)
            mem_total_gb = mem.total / (1024**3)
            
            # Process count
            python_procs = sum(1 for p in psutil.process_iter(['name']) 
                             if 'python' in p.info['name'].lower())
            ollama_procs = sum(1 for p in psutil.process_iter(['name']) 
                             if 'ollama' in p.info['name'].lower())
            
            # Display
            print(f"\r🔥 CPU: {cpu_percent:5.1f}%  |  "
                  f"💾 RAM: {mem_used_gb:5.1f}/{mem_total_gb:.0f}GB ({mem.percent:4.1f}%)  |  "
                  f"🐍 Python: {python_procs}  |  "
                  f"🦙 Ollama: {ollama_procs}     ", end="", flush=True)
            
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print("\n\n" + "="*80)
        print("\n📊 Final Stats:")
        print(f"   CPU Cores: {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count()} logical")
        print(f"   RAM Total: {mem_total_gb:.1f}GB")
        print(f"   RAM Usage Peak: {mem.percent:.1f}%")
        print("\n✅ Monitoring stopped")

if __name__ == "__main__":
    monitor_loop()

