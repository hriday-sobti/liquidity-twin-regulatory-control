export type SectionKey =
  | 'overview'
  | 'movement'
  | 'lineage'
  | 'scenarios'
  | 'close'
  | 'controls'
  | 'reporting'
  | 'queries'
  | 'copilot'
  | 'replay'
  | 'benchmark';

export interface OverviewData {
  snapshot: {
    snapshot_id: string;
    period: string;
    business_date: string;
    status: string;
    rule_version: string;
    calculation_version: string;
    created_at: string;
  };
  kpis: {
    nsfr: number;
    lcr: number;
    asf_usd: number;
    rsf_usd: number;
    hqla_usd: number;
    net_outflows_usd: number;
    control_score: number;
    open_exceptions_count: number;
  };
  movement: {
    previous_nsfr_percentage: number;
    current_nsfr_percentage: number;
    total_movement_pp: number;
    reconciliation_variance_pp: number;
    drivers: Array<{
      driver_name: string;
      contribution_pp: number;
      balance_movement_usd: number;
      impact_direction: string;
    }>;
    largest_driver: string;
  };
}
