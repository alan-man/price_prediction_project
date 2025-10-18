# airbnb_analysis_fixed.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json

class AirbnbDataParser:
    def __init__(self, json_data):
        self.data = json_data
        self.df = None
    
    def parse_json_to_dataframe(self):
        """Parse the JSON Airbnb data into a structured DataFrame"""
        parsed_data = []
        
        for listing in self.data:
            try:
                # Extract basic listing information
                listing_info = {
                    'room_id': listing.get('room_id', ''),
                    'name': listing.get('name', ''),
                    'title': listing.get('title', ''),
                    'city': listing.get('title', '').split('ใน ')[-1] if 'ใน ' in listing.get('title', '') else 'Unknown',
                    'price': listing.get('price', {}).get('unit', {}).get('amount', 0),
                    'currency': listing.get('price', {}).get('unit', {}).get('curency_symbol', ''),
                    'rating': listing.get('rating', {}).get('value', 0),
                    'review_count': listing.get('rating', {}).get('reviewCount', 0),
                    'badges': ', '.join(listing.get('badges', [])),
                    'latitude': listing.get('coordinates', {}).get('latitude', 0),
                    'longitude': listing.get('coordinates', {}).get('longitud', 0),
                }
                
                # Extract host information
                passport = listing.get('passportData', {})
                listing_info.update({
                    'host_id': passport.get('userId', ''),
                    'host_name': passport.get('name', ''),
                    'host_verified': passport.get('isVerified', False),
                    'superhost': passport.get('isSuperhost', False),
                    'host_rating': passport.get('ratingAverage', 0),
                    'host_review_count': passport.get('ratingCount', 0),
                    'years_hosting': passport.get('timeAsHost', {}).get('years', 0),
                })
                
                # Extract room features from structured content
                structured = listing.get('structuredContent', {})
                primary_lines = structured.get('primaryLine', [])
                
                bed_info = []
                host_info = []
                
                for line in primary_lines:
                    line_type = line.get('type', '')
                    body = line.get('body', '')
                    if line_type == 'BEDINFO':
                        bed_info.append(body)
                    elif line_type == 'HOSTINFO':
                        host_info.append(body)
                
                listing_info['bed_info'] = ' | '.join(bed_info)
                listing_info['host_info'] = ' | '.join(host_info)
                
                # Extract number of beds and bedrooms
                beds = 0
                bedrooms = 0
                for info in bed_info:
                    if 'bed' in info.lower():
                        try:
                            beds = int(''.join(filter(str.isdigit, info)))
                        except:
                            pass
                    if 'bedroom' in info.lower():
                        try:
                            bedrooms = int(''.join(filter(str.isdigit, info)))
                        except:
                            pass
                
                listing_info['beds'] = beds
                listing_info['bedrooms'] = bedrooms
                
                # Calculate price per bed
                if beds > 0 and listing_info['price'] > 0:
                    listing_info['price_per_bed'] = listing_info['price'] / beds
                else:
                    listing_info['price_per_bed'] = listing_info['price']
                
                parsed_data.append(listing_info)
                
            except Exception as e:
                print(f"Error parsing listing: {e}")
                continue
        
        self.df = pd.DataFrame(parsed_data)
        
        # FIX: Convert review_count from string to numeric
        if 'review_count' in self.df.columns:
            self.df['review_count'] = pd.to_numeric(self.df['review_count'], errors='coerce').fillna(0)
        
        return self.df
    
    def analyze_data(self):
        """Perform comprehensive analysis on the parsed data"""
        if self.df is None:
            print("No data to analyze. Please parse data first.")
            return
        
        print("=" * 60)
        print("🏠 AIRBNB DATA ANALYSIS REPORT")
        print("=" * 60)
        
        print(f"📊 Total Listings: {len(self.df)}")
        print(f"💰 Price Range: ${self.df['price'].min():.2f} - ${self.df['price'].max():.2f}")
        print(f"🏷️ Currency: {self.df['currency'].iloc[0] if len(self.df) > 0 else 'Unknown'}")
        
        print(f"\n⭐ Rating Statistics:")
        print(f"   Average Rating: {self.df['rating'].mean():.2f}/5")
        print(f"   Highest Rated: {self.df['rating'].max():.2f}/5")
        print(f"   Total Reviews: {self.df['review_count'].sum():.0f}")
        
        print(f"\n🏆 Host Statistics:")
        superhost_count = self.df['superhost'].sum()
        print(f"   Superhosts: {superhost_count} ({superhost_count/len(self.df)*100:.1f}%)")
        print(f"   Verified Hosts: {self.df['host_verified'].sum()}")
        print(f"   Average Years Hosting: {self.df['years_hosting'].mean():.1f} years")
        
        print(f"\n🛏️ Room Features:")
        total_beds = self.df['beds'].sum()
        total_bedrooms = self.df['bedrooms'].sum()
        print(f"   Total Beds: {total_beds}")
        print(f"   Total Bedrooms: {total_bedrooms}")
        print(f"   Average Beds per Listing: {self.df['beds'].mean():.1f}")
        print(f"   Average Bedrooms per Listing: {self.df['bedrooms'].mean():.1f}")
        
        return self.df
    
    def create_visualizations(self):
        """Create comprehensive visualizations"""
        if self.df is None:
            print("No data to visualize. Please parse data first.")
            return
        
        plt.style.use('default')
        plt.figure(figsize=(20, 12))
        
        # 1. Price Distribution
        plt.subplot(2, 3, 1)
        self.df['price'].hist(bins=15, alpha=0.7, edgecolor='black', color='skyblue')
        plt.title('Price Distribution', fontsize=14, fontweight='bold')
        plt.xlabel('Price (MXN)')
        plt.ylabel('Frequency')
        plt.grid(axis='y', alpha=0.3)
        
        # 2. Rating Distribution
        plt.subplot(2, 3, 2)
        ratings = self.df[self.df['rating'] > 0]['rating']
        if len(ratings) > 0:
            ratings.hist(bins=10, alpha=0.7, edgecolor='black', color='lightgreen')
            plt.title('Rating Distribution', fontsize=14, fontweight='bold')
            plt.xlabel('Rating (1-5)')
            plt.ylabel('Count')
            plt.grid(axis='y', alpha=0.3)
        
        # 3. Price vs Rating
        plt.subplot(2, 3, 3)
        valid_data = self.df[(self.df['rating'] > 0) & (self.df['price'] > 0)]
        if len(valid_data) > 0:
            colors = ['red' if x else 'blue' for x in valid_data['superhost']]
            plt.scatter(valid_data['rating'], valid_data['price'], alpha=0.7, c=colors, s=100)
            plt.title('Price vs Rating', fontsize=14, fontweight='bold')
            plt.xlabel('Rating')
            plt.ylabel('Price (MXN)')
            plt.grid(True, alpha=0.3)
            # Add legend for superhosts
            plt.plot([], [], 'o', color='red', label='Superhost')
            plt.plot([], [], 'o', color='blue', label='Regular Host')
            plt.legend()
        
        # 4. Superhost vs Regular Host Prices
        plt.subplot(2, 3, 4)
        if len(self.df[self.df['superhost'] == True]) > 0 and len(self.df[self.df['superhost'] == False]) > 0:
            box_data = [self.df[self.df['superhost'] == True]['price'].values, 
                       self.df[self.df['superhost'] == False]['price'].values]
            plt.boxplot(box_data, tick_labels=['Superhost', 'Regular'])
            plt.title('Price: Superhost vs Regular', fontsize=14, fontweight='bold')
            plt.ylabel('Price (MXN)')
            plt.grid(axis='y', alpha=0.3)
        
        # 5. Review Count Distribution
        plt.subplot(2, 3, 5)
        reviews = self.df[self.df['review_count'] > 0]['review_count']
        if len(reviews) > 0:
            reviews.hist(bins=10, alpha=0.7, edgecolor='black', color='orange')
            plt.title('Review Count Distribution', fontsize=14, fontweight='bold')
            plt.xlabel('Number of Reviews')
            plt.ylabel('Count')
            plt.grid(axis='y', alpha=0.3)
        
        # 6. Price by Number of Beds
        plt.subplot(2, 3, 6)
        bed_prices = self.df[self.df['beds'] > 0]
        if len(bed_prices) > 0:
            plt.scatter(bed_prices['beds'], bed_prices['price'], alpha=0.7, s=100, color='purple')
            plt.title('Price vs Number of Beds', fontsize=14, fontweight='bold')
            plt.xlabel('Number of Beds')
            plt.ylabel('Price (MXN)')
            plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def save_to_csv(self, filename='airbnb_analyzed_data.csv'):
        """Save analyzed data to CSV"""
        if self.df is not None:
            self.df.to_csv(filename, index=False, encoding='utf-8')
            print(f"💾 Data saved to {filename}")
        else:
            print("No data to save.")
    
    def show_data_sample(self):
        """Display a sample of the parsed data"""
        if self.df is not None:
            print("\n📋 SAMPLE OF PARSED DATA:")
            print("=" * 80)
            print(self.df.head())
            print(f"\n📊 DataFrame Shape: {self.df.shape}")
            print(f"🎯 Columns: {list(self.df.columns)}")
        else:
            print("No data to display.")

def load_json_data(file_path):
    """Load JSON data from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        print(f"✅ Successfully loaded JSON data from {file_path}")
        print(f"📁 Number of listings: {len(data)}")
        return data
    except FileNotFoundError:
        print(f"❌ Error: File not found at {file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format in {file_path}: {e}")
        return []
    except Exception as e:
        print(f"❌ Error loading file {file_path}: {e}")
        return []

# =============================================================================
# MAIN EXECUTION - JUST RUN THIS!
# =============================================================================

def main():
    print("🚀 STARTING AIRBNB DATA ANALYSIS")
    print("=" * 50)
    
    # Step 1: Load JSON data from file
    json_file_path = "/Users/yanis/Downloads/search_from_url.json"
    print(f"📂 Loading data from: {json_file_path}")
    airbnb_json_data = load_json_data(json_file_path)
    
    if not airbnb_json_data:
        print("❌ No data loaded. Please check the file path and JSON format.")
        return None
    
    # Step 2: Create parser instance with your data
    parser = AirbnbDataParser(airbnb_json_data)
    
    # Step 3: Parse JSON to DataFrame
    print("📊 Parsing JSON data...")
    df = parser.parse_json_to_dataframe()
    
    # Step 4: Show data sample
    parser.show_data_sample()
    
    # Step 5: Analyze the data
    print("\n🔍 Analyzing data...")
    parser.analyze_data()
    
    # Step 6: Create visualizations
    print("\n📈 Creating visualizations...")
    parser.create_visualizations()
    
    # Step 7: Save to CSV
    print("\n💾 Saving data...")
    parser.save_to_csv('airbnb_analysis.csv')
    
    print("\n✅ ANALYSIS COMPLETE!")
    print("🎯 Next steps: Use the generated CSV file for machine learning modeling")
    
    return df

# Run the analysis
if __name__ == "__main__":
    try:
        result_df = main()
        
        # Additional quick insights
        print("\n" + "=" * 50)
        print("💡 QUICK INSIGHTS")
        print("=" * 50)
        
        if result_df is not None:
            # Most expensive listing
            most_expensive = result_df.loc[result_df['price'].idxmax()]
            print(f"💰 Most expensive: {most_expensive['name'][:50]}... - ${most_expensive['price']:.2f}")
            
            # Highest rated listing
            highest_rated = result_df.loc[result_df['rating'].idxmax()]
            print(f"⭐ Highest rated: {highest_rated['name'][:50]}... - {highest_rated['rating']}/5")
            
            # Average price per bed
            avg_price_per_bed = result_df['price_per_bed'].mean()
            print(f"🛏️ Average price per bed: ${avg_price_per_bed:.2f}")
            
            # Price statistics
            print(f"📊 Price Statistics:")
            print(f"   Mean: ${result_df['price'].mean():.2f}")
            print(f"   Median: ${result_df['price'].median():.2f}")
            print(f"   Standard Deviation: ${result_df['price'].std():.2f}")
            
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()