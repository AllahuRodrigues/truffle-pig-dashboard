import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_high_signal_mock_data(num_campaigns=50, num_sessions=200000):
    """
    Generates a mock dataset with very strong, clear patterns to enable
    a high-AUC model performance for the demo.
    
    V2 Change: Added 'spend' as a feature influencing conversion to enable lift forecasting.
    """
    print("--- Starting High-Signal Mock Data Factory ---")

    # --- 1. Generate campaigns.csv with distinct performance tiers ---
    print("Generating campaigns.csv with strong performance signals...")
    campaign_ids = [f"campaign_{i+1}" for i in range(num_campaigns)]
    
    tiers = ['Low'] * 20 + ['Medium'] * 20 + ['High'] * 10
    np.random.shuffle(tiers)
    
    campaign_data = {
        'campaign_id': campaign_ids,
        'campaign_name': [f"Campaign {i+1} ({tiers[i]})" for i in range(num_campaigns)],
        'start_date': [datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 365)) for _ in range(num_campaigns)],
        'spend': np.random.randint(1000, 25000, size=num_campaigns),
        'creative_format': np.random.choice(['video', 'static', 'UGC', 'lifestyle'], size=num_campaigns),
        'creative_theme': np.random.choice(['Evergreen', 'Promo / Sale'], size=num_campaigns, p=[0.7, 0.3]),
        'effectiveness_tier': tiers
    }
    campaigns_df = pd.DataFrame(campaign_data)
    campaigns_df.to_csv('campaigns.csv', index=False)
    print(f"✅ campaigns.csv created with {len(campaigns_df)} records.")

    # --- 2. Generate sessions.csv with patterns ---
    print("\nGenerating sessions.csv with stronger conversion patterns...")
    user_ids = [f"user_{i+1}" for i in range(int(num_sessions / 4))]
    
    campaign_spend_dist = campaigns_df['spend'] / campaigns_df['spend'].sum()
    session_campaign_ids = np.random.choice(campaigns_df['campaign_id'], size=num_sessions, p=campaign_spend_dist)
    
    session_data = {
        'session_id': [f"session_{i+1}" for i in range(num_sessions)],
        'user_id': np.random.choice(user_ids, size=num_sessions),
        'session_start': [datetime(2023, 1, 1) + timedelta(seconds=np.random.randint(0, 365*24*3600)) for _ in range(num_sessions)],
        'utm_source': np.random.choice(['google', 'facebook', 'instagram', 'direct'], size=num_sessions, p=[0.4, 0.3, 0.2, 0.1]),
        'utm_medium': np.random.choice(['cpc', 'social_paid', 'organic', 'referral'], size=num_sessions, p=[0.5, 0.2, 0.2, 0.1]),
        'campaign_id': session_campaign_ids
    }
    sessions_df = pd.DataFrame(session_data)

    # Merge campaign effectiveness into sessions
    sessions_df = pd.merge(sessions_df, campaigns_df, on='campaign_id', how='left')

    # --- 3. Create a 'converted' flag based on amplified, high-signal patterns ---
    # **FIX:** Add spend as a predictive feature for conversion.
    # We normalize spend and add it as a small probability lift.
    spend_normalized = (sessions_df['spend'] - sessions_df['spend'].min()) / (sessions_df['spend'].max() - sessions_df['spend'].min())
    spend_lift = spend_normalized * 0.05  # Max 5% lift from spend

    # Start with a base conversion rate that now includes the spend lift
    conversion_probs = np.full(num_sessions, 0.02) + spend_lift
    
    # Create extremely strong signals for conversion from other features
    high_tier_mask = sessions_df['effectiveness_tier'] == 'High'
    promo_mask = sessions_df['creative_theme'] == 'Promo / Sale'
    video_mask = sessions_df['creative_format'] == 'video'
    
    # The "golden path" to conversion is amplified
    golden_path_mask = high_tier_mask & promo_mask & video_mask
    conversion_probs[golden_path_mask] = np.clip(conversion_probs[golden_path_mask] + 0.85, 0, 1) # Add a strong boost
    
    # Strong secondary path
    secondary_path_mask = high_tier_mask & (promo_mask | video_mask)
    conversion_probs[secondary_path_mask] = np.clip(conversion_probs[secondary_path_mask] + 0.50, 0, 1)
    
    # Penalize low-tier campaigns
    low_tier_mask = sessions_df['effectiveness_tier'] == 'Low'
    conversion_probs[low_tier_mask] = np.clip(conversion_probs[low_tier_mask] * 0.1, 0.005, 1) # Reduce probability
    
    sessions_df['converted'] = (np.random.rand(num_sessions) < conversion_probs).astype(int)
    
    actual_conversions = sessions_df['converted'].sum()
    print(f"...Generated {actual_conversions} initial conversions.")
    
    # --- 4. Generate orders.csv from converted sessions ---
    print("\nGenerating orders.csv from converted sessions...")
    converting_sessions = sessions_df[sessions_df['converted'] == 1].copy()
    
    time_deltas = pd.to_timedelta([timedelta(minutes=np.random.randint(5, 59)) for _ in range(len(converting_sessions))])
    
    order_data = {
        'order_id': [f"order_{i+1}" for i in range(len(converting_sessions))],
        'user_id': converting_sessions['user_id'].values,
        'order_datetime': converting_sessions['session_start'].values + time_deltas,
        'gross_revenue': np.random.uniform(50, 300, size=len(converting_sessions)).round(2),
    }
    orders_df = pd.DataFrame(order_data)

    # Clean up final sessions dataframe before saving
    final_session_cols = ['session_id', 'user_id', 'session_start', 'utm_source', 'utm_medium', 'campaign_id', 'converted']
    sessions_df_final = sessions_df[final_session_cols]

    # Save the files
    sessions_df_final.to_csv('sessions.csv', index=False)
    print(f"✅ sessions.csv created with {len(sessions_df_final)} records and {sessions_df_final['converted'].sum()} conversions.")
    
    orders_df.to_csv('orders.csv', index=False)
    print(f"✅ orders.csv created with {len(orders_df)} records.")
    
    print("\n--- High-Signal Mock Data Factory Finished Successfully! ---")


if __name__ == '__main__':
    create_high_signal_mock_data()
