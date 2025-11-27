#!/usr/bin/env python3
"""Merge clean Kaggle Airbnb data with scraped Airbnb data (amenities enrichment).

Creates `clean_data/merged_airbnb_kaggle_scraped.csv` by aligning columns,
creating amenity binary columns and concatenating unique listings.

Usage:
  python3 scripts/merge_kaggle_scraped.py

You can pass custom paths with --kaggle and --scraped flags.
"""
from __future__ import annotations
import argparse
import ast
import os
from collections import Counter
import pandas as pd


def parse_amenities_cell(x):
    if pd.isna(x):
        return []
    if isinstance(x, list):
        return x
    if isinstance(x, str):
        s = x.strip()
        # Try literal_eval for stringified lists
        if s.startswith('[') and s.endswith(']'):
            try:
                return ast.literal_eval(s)
            except Exception:
                pass
        # fallback: split on commas
        return [p.strip() for p in s.split(',') if p.strip()]
    return []


def load_if_exists(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return pd.DataFrame()
    print(f"Loading: {path}")
    df = pd.read_csv(path)
    # normalize listing id column: prefer `listing_id`, fall back to `id`
    if 'listing_id' not in df.columns and 'id' in df.columns:
        df = df.rename(columns={'id': 'listing_id'})
    return df


def main(kaggle_path: str, scraped_path: str, out_path: str):
    kaggle_df = load_if_exists(kaggle_path)
    scraped_df = load_if_exists(scraped_path)

    print(f"Kaggle rows: {len(kaggle_df)}, Scraped rows: {len(scraped_df)}")

    # Normalize scraped columns to common names
    column_mapping = {
        'id': 'listing_id',
        'room_id': 'listing_id',
        'price_night': 'price',
        'lat': 'latitude',
        'lon': 'longitude',
        'rating': 'review_scores_rating',
        'reviews': 'review_scores_checkin'
    }
    scraped_df = scraped_df.rename(columns={k: v for k, v in column_mapping.items() if k in scraped_df.columns})

    # Ensure listing_id exists (as int) for merging/dedup
    if 'listing_id' in scraped_df.columns:
        try:
            scraped_df['listing_id'] = scraped_df['listing_id'].astype('Int64')
        except Exception:
            pass

    if 'listing_id' in kaggle_df.columns:
        try:
            kaggle_df['listing_id'] = kaggle_df['listing_id'].astype('Int64')
        except Exception:
            pass

    # Process scraped amenities
    if not scraped_df.empty and 'amenities_list' in scraped_df.columns:
        scraped_df['amenities_parsed'] = scraped_df['amenities_list'].apply(parse_amenities_cell)
        scraped_amen_counts = Counter(a for sub in scraped_df['amenities_parsed'] for a in sub if a != 'API_FETCH_FAILED')
        scraped_n = len(scraped_df)
        scraped_threshold = max(1, int(0.01 * scraped_n))
        common_scraped_amen = {a for a, c in scraped_amen_counts.items() if c >= scraped_threshold}
        print(f"Scraped: unique amenities={len(scraped_amen_counts)}, frequent>={scraped_threshold}: {len(common_scraped_amen)}")

        for a in sorted(common_scraped_amen):
            col = 'Has_' + a.replace(' ', '_').replace('-', '_').replace('/', '_').replace("'", "").replace('’','')
            scraped_df[col] = scraped_df['amenities_parsed'].apply(lambda lst: int(a in lst))
    else:
        print("No scraped amenities column found or scraped data empty")

    # Identify Kaggle amenity columns (already expanded as Has_...)
    kaggle_amen_cols = [c for c in kaggle_df.columns if str(c).startswith('Has_')]
    scraped_amen_cols = [c for c in scraped_df.columns if str(c).startswith('Has_')]

    all_amen_cols = sorted(set(kaggle_amen_cols + scraped_amen_cols))
    print(f"Kaggle amenity cols: {len(kaggle_amen_cols)}, Scraped amenity cols: {len(scraped_amen_cols)}, Total amenity cols: {len(all_amen_cols)}")

    # Ensure amenity columns exist in both frames
    for col in all_amen_cols:
        if col not in kaggle_df.columns:
            kaggle_df[col] = 0
        if col not in scraped_df.columns:
            scraped_df[col] = 0

    # Determine common columns to keep (intersection)
    common_cols = sorted(set(kaggle_df.columns) & set(scraped_df.columns)) if not kaggle_df.empty and not scraped_df.empty else list(kaggle_df.columns) or list(scraped_df.columns)

    # If listing_id exists, make sure it's included
    if 'listing_id' in kaggle_df.columns or 'listing_id' in scraped_df.columns:
        if 'listing_id' not in common_cols:
            common_cols = ['listing_id'] + [c for c in common_cols if c != 'listing_id']

    print(f"Columns used for concatenation (count={len(common_cols)}): {common_cols[:10]}{'...' if len(common_cols)>10 else ''}")

    kaggle_subset = kaggle_df[common_cols].copy() if not kaggle_df.empty else pd.DataFrame(columns=common_cols)
    scraped_subset = scraped_df[common_cols].copy() if not scraped_df.empty else pd.DataFrame(columns=common_cols)

    merged = pd.concat([kaggle_subset, scraped_subset], ignore_index=True, sort=False)

    if 'listing_id' in merged.columns:
        before = len(merged)
        merged = merged.drop_duplicates(subset=['listing_id'], keep='first')
        print(f"Dropped {before - len(merged)} duplicate rows based on listing_id")

    # Prepare output dir
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    merged.to_csv(out_path, index=False)
    print(f"Saved merged dataset to {out_path} (shape: {merged.shape})")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Merge Kaggle and scraped Airbnb data')
    parser.add_argument('--kaggle', default='clean_data/clean_kaggle_data.csv', help='Path to cleaned Kaggle CSV')
    parser.add_argument('--scraped', default='paris_airbnb_dataset_TEST_AMENITIES.csv', help='Path to scraped CSV')
    parser.add_argument('--out', default='clean_data/merged_airbnb_kaggle_scraped.csv', help='Output merged CSV path')
    args = parser.parse_args()
    main(args.kaggle, args.scraped, args.out)
