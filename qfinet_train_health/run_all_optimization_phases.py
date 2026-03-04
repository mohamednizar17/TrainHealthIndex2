"""
Master Execution Script: Run ALL 4 Optimization Phases + Unified Benchmark
===========================================================================
Executes complete workflow: Baseline → Accuracy → Speed → Edge → Comparison
"""

import subprocess
import sys
import os
from pathlib import Path
import time

class AllPhasesExecutor:
    def __init__(self):
        self.phases = [
            {
                'name': 'Phase 1: Baseline Measurement',
                'script': 'measure_baseline.py',
                'duration': '~3 minutes',
                'purpose': 'Measure current QFINET & Traditional CNN performance'
            },
            {
                'name': 'Phase 2: Accuracy Optimization',
                'script': 'optimize_accuracy.py',
                'duration': '~15 minutes',
                'purpose': 'Data augmentation + ensemble voting → 99%+ accuracy'
            },
            {
                'name': 'Phase 3: Speed Optimization',
                'script': 'optimize_speed.py',
                'duration': '~10 minutes',
                'purpose': 'Knowledge distillation + quantization → <10ms inference'
            },
            {
                'name': 'Phase 4: Edge Optimization',
                'script': 'optimize_edge.py',
                'duration': '~8 minutes',
                'purpose': 'Pruning + TFLite conversion → Raspberry Pi deployment'
            },
            {
                'name': 'Phase 5: Unified Benchmark',
                'script': 'unified_benchmark.py',
                'duration': '~2 minutes',
                'purpose': 'Compare all models & generate recommendations'
            }
        ]
    
    def print_banner(self):
        """Print welcome banner"""
        print("\n" + "="*80)
        print("🚀 QFINET OPTIMIZATION FRAMEWORK - COMPLETE EXECUTION")
        print("="*80)
        print("\n⏱️  Total estimated time: ~40 minutes")
        print("📊 Total models to train: 12+ variants")
        print("💾 Output: Optimized models + comparison charts + recommendations\n")
    
    def print_phase_header(self, phase_num, phase_info):
        """Print phase header"""
        print(f"\n{'='*80}")
        print(f"🔄 EXECUTING: {phase_info['name']}")
        print(f"{'='*80}")
        print(f"📌 Purpose: {phase_info['purpose']}")
        print(f"⏱️  Est. Duration: {phase_info['duration']}")
        print(f"📄 Script: {phase_info['script']}")
        print(f"{'='*80}\n")
    
    def run_phase(self, phase_num, phase_info):
        """Execute single phase"""
        self.print_phase_header(phase_num, phase_info)
        
        script_path = phase_info['script']
        
        if not os.path.exists(script_path):
            print(f"❌ ERROR: {script_path} not found!")
            return False
        
        try:
            # Run script
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=False,
                text=True,
                timeout=3600  # 1 hour timeout per phase
            )
            
            if result.returncode == 0:
                print(f"\n✅ {phase_info['name']} COMPLETED SUCCESSFULLY\n")
                return True
            else:
                print(f"\n❌ {phase_info['name']} FAILED with exit code {result.returncode}\n")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"\n⏱️  {phase_info['name']} TIMEOUT (exceeded 1 hour)\n")
            return False
        except Exception as e:
            print(f"\n❌ ERROR running {phase_info['name']}: {e}\n")
            return False
    
    def print_execution_summary(self, results):
        """Print final summary"""
        print("\n" + "="*80)
        print("📊 EXECUTION SUMMARY")
        print("="*80)
        
        completed = sum(1 for r in results.values() if r)
        total = len(results)
        
        for i, (phase_name, success) in enumerate(results.items(), 1):
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{i}. {phase_name}: {status}")
        
        print(f"\nTotal: {completed}/{total} phases completed successfully")
        
        if completed == total:
            print("\n🎉 ALL PHASES COMPLETED SUCCESSFULLY!")
            print("\n📁 Output files generated:")
            print("   • models/baseline_benchmark.csv")
            print("   • models/accuracy_optimization_results.json")
            print("   • models/speed_optimization_results.json")
            print("   • models/edge_optimization_results.json")
            print("   • models/unified_benchmark_results.csv")
            print("   • models/optimization_comparison.png")
            print("\n🎯 Next steps:")
            print("   1. Review results: models/unified_benchmark_results.csv")
            print("   2. View chart: models/optimization_comparison.png")
            print("   3. Update Streamlit: streamlit_app.py with best models")
            print("   4. Deploy to edge: Download .tflite files to Raspberry Pi")
        else:
            print(f"\n⚠️  {total - completed} phase(s) failed. Review errors above.")
        
        print("\n" + "="*80)
    
    def run_all_phases(self):
        """Execute all phases sequentially"""
        self.print_banner()
        
        results = {}
        start_time = time.time()
        
        for i, phase in enumerate(self.phases, 1):
            success = self.run_phase(i, phase)
            results[phase['name']] = success
            
            # Stop on first failure (optional - change to continue on error)
            if not success:
                print(f"\n⚠️  Stopping execution due to failure in {phase['name']}")
                # Uncomment next line to continue despite failures:
                # continue
        
        elapsed_time = time.time() - start_time
        elapsed_minutes = elapsed_time / 60
        
        print(f"\n⏱️  Total execution time: {elapsed_minutes:.1f} minutes")
        
        self.print_execution_summary(results)
        
        return all(results.values())

def main():
    """Main entry point"""
    executor = AllPhasesExecutor()
    success = executor.run_all_phases()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
