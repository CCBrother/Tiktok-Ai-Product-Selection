CREATE TABLE IF NOT EXISTS shops (
  shop_id VARCHAR(128) PRIMARY KEY,
  name TEXT,
  follower_count INT,
  rating NUMERIC(3, 2),
  product_count INT,
  country VARCHAR(32),
  created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS creators (
  creator_id VARCHAR(128) PRIMARY KEY,
  nickname TEXT,
  follower_count INT,
  total_videos INT,
  avg_views INT,
  engagement_rate NUMERIC(5, 2),
  country VARCHAR(32)
);

CREATE TABLE IF NOT EXISTS products (
  id SERIAL PRIMARY KEY,
  product_id VARCHAR(128) UNIQUE NOT NULL,
  shop_id VARCHAR(128) REFERENCES shops(shop_id),
  title TEXT,
  description TEXT,
  category VARCHAR(64),
  brand VARCHAR(64),
  price NUMERIC(10, 2),
  currency VARCHAR(8),
  rating NUMERIC(3, 2),
  review_count INT,
  first_seen_at TIMESTAMP,
  last_seen_at TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS product_snapshots (
  id SERIAL PRIMARY KEY,
  product_id VARCHAR(128),
  snapshot_time TIMESTAMP NOT NULL,
  sales INT,
  gmv NUMERIC(14, 2),
  order_count INT,
  price NUMERIC(10, 2),
  video_count INT,
  creator_count INT,
  shop_count INT,
  engagement_score NUMERIC(10, 2),
  raw_json JSONB
);

CREATE TABLE IF NOT EXISTS videos (
  video_id VARCHAR(128) PRIMARY KEY,
  product_id VARCHAR(128) REFERENCES products(product_id),
  creator_id VARCHAR(128) REFERENCES creators(creator_id),
  likes INT,
  comments INT,
  shares INT,
  views INT,
  publish_time TIMESTAMP,
  engagement_score NUMERIC(10, 2)
);

CREATE TABLE IF NOT EXISTS product_history (
  id BIGSERIAL PRIMARY KEY,
  product_id BIGINT NOT NULL REFERENCES products(id),
  observed_date DATE NOT NULL,
  price_usd NUMERIC(10, 2),
  sold_count INTEGER DEFAULT 0,
  sales_growth_pct_7d NUMERIC(8, 2),
  tiktok_mentions_7d INTEGER DEFAULT 0,
  mention_growth_pct_7d NUMERIC(8, 2),
  creator_count_7d INTEGER DEFAULT 0,
  avg_video_engagement_pct NUMERIC(8, 2),
  interaction_velocity NUMERIC(10, 2),
  rating_avg NUMERIC(3, 2),
  rating_count INTEGER DEFAULT 0,
  review_sentiment_score NUMERIC(5, 2),
  growth_score INTEGER DEFAULT 0,
  trend_score INTEGER DEFAULT 0,
  competition_score INTEGER DEFAULT 0,
  profit_score INTEGER DEFAULT 0,
  review_score INTEGER DEFAULT 0,
  lifecycle_score INTEGER DEFAULT 0,
  supply_score INTEGER DEFAULT 0,
  copy_difficulty_score INTEGER DEFAULT 0,
  content_score INTEGER DEFAULT 0,
  viral_score INTEGER DEFAULT 0,
  ai_score INTEGER DEFAULT 0,
  weights_json JSONB DEFAULT '{}'::jsonb,
  decision_json JSONB DEFAULT '{}'::jsonb,
  raw_event_ids TEXT[] DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(product_id, observed_date)
);

CREATE TABLE IF NOT EXISTS ai_product_scores (
  id SERIAL PRIMARY KEY,
  product_id VARCHAR(128) REFERENCES products(product_id),
  score_time TIMESTAMP,
  growth_score NUMERIC(5, 2),
  trend_score NUMERIC(5, 2),
  competition_score NUMERIC(5, 2),
  profit_score NUMERIC(5, 2),
  supply_score NUMERIC(5, 2),
  copy_score NUMERIC(5, 2),
  virality_score NUMERIC(5, 2),
  final_score NUMERIC(5, 2),
  lifecycle_stage VARCHAR(32),
  recommendation_level VARCHAR(8),
  explanation TEXT
);

CREATE TABLE IF NOT EXISTS product_competition (
  id SERIAL PRIMARY KEY,
  product_id VARCHAR(128) REFERENCES products(product_id),
  shop_count INT,
  listing_count INT,
  saturation_score NUMERIC(5, 2)
);

CREATE TABLE IF NOT EXISTS supply_chain (
  id SERIAL PRIMARY KEY,
  product_id VARCHAR(128) REFERENCES products(product_id),
  supplier_count INT,
  avg_moq INT,
  avg_price NUMERIC(10, 2),
  lead_time_days INT,
  supply_score NUMERIC(5, 2),
  risk_level VARCHAR(16)
);

CREATE TABLE IF NOT EXISTS product_lifecycle (
  id SERIAL PRIMARY KEY,
  product_id VARCHAR(128) REFERENCES products(product_id),
  stage VARCHAR(32),
  confidence NUMERIC(5, 2),
  updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_product_history_score ON product_history (observed_date, ai_score DESC);
CREATE INDEX IF NOT EXISTS idx_product_snapshots_product_time ON product_snapshots (product_id, snapshot_time DESC);
CREATE INDEX IF NOT EXISTS idx_videos_product ON videos (product_id, publish_time DESC);
CREATE INDEX IF NOT EXISTS idx_ai_product_scores_product_time ON ai_product_scores (product_id, score_time DESC);
CREATE INDEX IF NOT EXISTS idx_product_competition_product ON product_competition (product_id);
CREATE INDEX IF NOT EXISTS idx_supply_chain_product ON supply_chain (product_id);
CREATE INDEX IF NOT EXISTS idx_product_lifecycle_product ON product_lifecycle (product_id);
