import {
  LayoutDashboard,
  TrendingDown,
  GitBranch,
  FlaskConical,
  CheckCircle2,
  ShieldAlert,
  FileSpreadsheet,
  HelpCircle,
  Bot,
  History,
  Layers,
} from 'lucide-react';
import { SectionKey } from '../types';

interface SidebarProps {
  currentSection: SectionKey;
  onSelectSection: (section: SectionKey) => void;
  controlScore?: number;
  openExceptions?: number;
}

export default function Sidebar({
  currentSection,
  onSelectSection,
  controlScore = 98.0,
  openExceptions = 2,
}: SidebarProps) {
  const navItems = [
    { key: 'overview', label: 'Overview', icon: LayoutDashboard },
    { key: 'movement', label: 'Movement Explorer', icon: TrendingDown },
    { key: 'lineage', label: 'Lineage & Audit', icon: GitBranch },
    { key: 'scenarios', label: 'Scenario Lab', icon: FlaskConical },
    { key: 'close', label: 'Close Workspace', icon: CheckCircle2 },
    { key: 'controls', label: 'Controls Catalog', icon: ShieldAlert, badge: `${controlScore}%` },
    { key: 'reporting', label: 'Reporting Packs', icon: FileSpreadsheet },
    { key: 'queries', label: 'Query Workbench', icon: HelpCircle },
    { key: 'copilot', label: 'Analyst Copilot', icon: Bot, badge: 'VERIFIED' },
    { key: 'replay', label: 'Event Replay', icon: History },
    { key: 'benchmark', label: 'Public Benchmark', icon: Layers },
  ];

  return (
    <aside className="w-[240px] bg-surface border-r border-border flex flex-col h-screen select-none shrink-0">
      {/* Brand Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-accent rounded flex items-center justify-center text-white font-mono text-xs font-bold">
            LT
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-tight text-accent">LIQUIDITY TWIN</h1>
            <p className="text-[10px] text-muted font-mono tracking-wider">REGULATORY CONTROL</p>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-2 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentSection === item.key;
          return (
            <button
              key={item.key}
              onClick={() => onSelectSection(item.key as SectionKey)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded text-xs font-medium transition-colors ${
                isActive
                  ? 'bg-accent-light text-accent border border-accent/20 font-semibold'
                  : 'text-text hover:bg-background hover:text-accent'
              }`}
            >
              <div className="flex items-center gap-2.5 truncate">
                <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-accent' : 'text-muted'}`} />
                <span className="truncate">{item.label}</span>
              </div>
              {item.badge && (
                <span
                  className={`text-[9px] px-1.5 py-0.5 rounded font-mono shrink-0 ${
                    item.badge === 'VERIFIED'
                      ? 'bg-success-light text-success border border-success-border'
                      : 'bg-background text-muted border border-border'
                  }`}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Institutional Metadata Footer */}
      <div className="p-3 border-t border-border bg-background/50 text-[10px] font-mono text-muted space-y-1">
        <div className="flex justify-between">
          <span>PERIOD</span>
          <span className="text-text font-semibold">2026-Q3 FROZEN</span>
        </div>
        <div className="flex justify-between">
          <span>RULE VER</span>
          <span className="text-text">3.2.0 (BCBS 295)</span>
        </div>
        <div className="flex justify-between">
          <span>EXCEPTIONS</span>
          <span className={openExceptions > 0 ? 'text-warning font-semibold' : 'text-success'}>
            {openExceptions} TRACKED
          </span>
        </div>
      </div>
    </aside>
  );
}
