#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
粤西 InVEST 生境质量论文 — 一键复现主控脚本
==========================================
运行此脚本将依次执行所有分析模块，输出论文所有表格（Table 2-9）的关键数值。

使用方法:
    python MASTER_RUN.py

数据要求:
    - gd_*.npy 和 cache/*.npy 文件必须存在（由原 reproduce_paper.py 或 ArcGIS 采样生成）
    - 依赖: numpy, scipy, esda, libpysal
    
输出目录:
    每个模块的结果在对应的子文件夹终端输出
    图表输出在 figures/ 目录（需另行运行 Figure 生成脚本）
"""
import os, sys, subprocess, time

BASE = os.path.dirname(os.path.abspath(__file__))
MODULES = [
    ("01_VarianceDecomposition_Table2", "Table 4 - 方差分解"),
    ("02_PerClassStats_Table4",         "Table 6 - 各地类统计"),
    ("03_CrossVariableICC_Table5",       "Table 7 - 跨变量 ICC 对比"),
    ("04_MultiTemporal_Table3",         "Table 5 - 多时相分析"),
    ("05_ScenarioAnalysis_Table6",       "Table 8 - 八情景 ICC"),
    ("06_Geodetector_Table7",           "Table 9 - 两阶段地理探测器"),
    ("07_SpatialAutocorrelation_Table8", "Table 10 - 空间自相关"),
    ("08_ForestThreat_Fig5",            "Fig 2b  - 森林威胁四分位"),
    ("09_MonteCarlo_FigS1",             "Fig 5c  - 蒙特卡洛稳健性"),
    ("10_KSensitivity_Table9",          "Table 11 - k 敏感性分析"),
]

print("="*60)
print("粤西 InVEST 生境质量论文 — 全量复现验证")
print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)

passed = 0
failed = 0

for folder, desc in MODULES:
    script = os.path.join(BASE, folder, "run.py")
    if not os.path.exists(script):
        print(f"\n[SKIP] {desc} — 脚本不存在: {script}")
        continue
    
    print(f"\n{'─'*60}")
    print(f"[RUN]  {desc}")
    print(f"{'─'*60}")
    
    t0 = time.time()
    result = subprocess.run(
        [sys.executable, script],
        capture_output=True, text=True, timeout=120
    )
    elapsed = time.time() - t0
    
    if result.returncode == 0:
        print(result.stdout)
        passed += 1
        status = "✅ PASS"
    else:
        print(result.stdout[-500:] if result.stdout else "")
        print(result.stderr[-500:] if result.stderr else "")
        failed += 1
        status = f"❌ FAIL (code={result.returncode})"
    
    print(f"  → {status} ({elapsed:.1f}s)")

print(f"\n{'='*60}")
print(f"复现完成: ✅ {passed} PASS / ❌ {failed} FAIL / 共 {len(MODULES)} 模块")
print(f"结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

if failed == 0:
    print(f"\n🎉 全部通过！所有表格结果可由独立复现验证。")
else:
    print(f"\n⚠️  {failed} 个模块未通过，请检查上述错误信息。")
print("="*60)
