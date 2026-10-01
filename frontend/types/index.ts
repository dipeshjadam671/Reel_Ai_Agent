export interface User {
  id: string;
  email: string;
  full_name?: string;
  is_active: boolean;
}

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  monthly_budget_usd: number;
  current_spend_usd: number;
}

export interface Task {
  id: string;
  workspace_id: string;
  name: string;
  topic: string;
  seed_script?: string;
  language: string;
  target_platforms: string[];
  presenter_config: {
    avatar_id?: string;
    voice_id?: string;
    pose?: string;
    layout?: string;
  };
  schedule_config: {
    frequency: string;
    time: string;
    timezone: string;
    active_days: string[];
  };
  brand_preferences: {
    tone: string;
    call_to_action: string;
    color_palette?: string[];
  };
  status: string;
  latest_cycle_id?: string;
  latest_cycle_status?: string;
  created_at: string;
  updated_at: string;
}

export interface Cycle {
  id: string;
  workspace_id: string;
  task_id: string;
  thread_id: string;
  status: string;
  current_agent?: string;
  novelty_score?: number;
  estimated_cost_usd: number;
  actual_cost_usd: number;
  error_details?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface CyclePreview {
  cycle_id: string;
  status: string;
  topic: string;
  language: string;
  video_url?: string;
  thumbnail_url?: string;
  captions_url?: string;
  duration_seconds: number;
  resolution: string;
  title?: string;
  hook?: string;
  call_to_action?: string;
  qa_score?: number;
  compliance_passed: boolean;
}

export interface Source {
  title: string;
  url: string;
  domain: string;
  summary?: string;
  credibility_score: number;
}

export interface Script {
  id: string;
  cycle_id: string;
  title: string;
  hook: string;
  raw_content: string;
  language: string;
  scenes: {
    scene_number: number;
    duration_seconds: number;
    visual_description: string;
    voiceover_text: string;
    on_screen_text?: string;
    presenter_visible: boolean;
  }[];
  claims: any[];
  call_to_action: string;
  version: number;
}

export interface Asset {
  id: string;
  cycle_id: string;
  asset_type: string;
  provider: string;
  external_id: string;
  storage_url: string;
  license_type: string;
  license_url?: string;
  attribution_text?: string;
  duration_seconds?: number;
}

export interface Publication {
  id: string;
  cycle_id: string;
  platform: string;
  status: string;
  platform_post_id?: string;
  permalink?: string;
  published_at?: string;
  error_message?: string;
  views: number;
  likes: number;
  shares: number;
}

export interface Analytics {
  total_videos_created: number;
  total_videos_published: number;
  total_views: number;
  total_likes: number;
  total_shares: number;
  total_spend_usd: number;
  monthly_budget_usd: number;
  recent_spend_records: {
    id: string;
    cycle_id?: string;
    provider: string;
    operation: string;
    amount: number;
    currency: string;
    created_at: string;
  }[];
}

export interface SocialAccount {
  platform: string;
  account_name: string;
  connected: boolean;
  last_synced?: string;
}
