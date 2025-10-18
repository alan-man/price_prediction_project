# airbnb_paris_collector.py
import pyairbnb
import json

def search_paris_airbnb():
    """Search Airbnb listings in Paris for December 1-31, 2025"""
    
    print("🚀 SEARCHING AIRBNB LISTINGS IN PARIS")
    print("=" * 50)
    print("📍 Location: Paris, France")
    print("📅 Dates: December 1-31, 2025")
    print("💵 Currency: EUR")
    print("=" * 50)
    
    # Paris bounding box coordinates
    paris_coords = {
        "ne_lat": 48.902,   # Northeast latitude
        "ne_long": 2.469,   # Northeast longitude  
        "sw_lat": 48.815,   # Southwest latitude
        "sw_long": 2.224    # Southwest longitude
    }
    
    try:
        # Get dynamic hash for better results
        print("🔑 Fetching API hash...")
        dynamic_hash = pyairbnb.fetch_stays_search_hash()
        
        print("🔍 Searching Airbnb listings...")
        results = pyairbnb.search_all(
            check_in="2025-12-01",
            check_out="2025-12-31",
            ne_lat=paris_coords["ne_lat"],
            ne_long=paris_coords["ne_long"],
            sw_lat=paris_coords["sw_lat"],
            sw_long=paris_coords["sw_long"],
            zoom_value=2,
            price_min=0,
            price_max=10000,  # Adjust this if you want higher/lower price range
            currency="EUR",
            language="fr",
            hash=dynamic_hash
        )
        
        print(f"✅ Found {len(results)} listings in Paris")
        
        # Show sample of results
        if results:
            print("\n📋 SAMPLE LISTINGS:")
            print("-" * 40)
            for i, listing in enumerate(results[:3]):  # Show first 3 listings
                name = listing.get('name', 'N/A')[:100]
                price = listing.get('price', {}).get('unit', {}).get('amount', 'N/A')
                rating = listing.get('rating', {}).get('value', 'N/A')
                print(f"{i+1}. {name}...")
                print(f"   💰 Price: €{price}")
                print(f"   ⭐ Rating: {rating}/5")
                print()
        
        return results
        
    except Exception as e:
        print(f"❌ Error searching Paris: {e}")
        return []

def save_paris_data(results, filename="./search_from_url.json"):
    """Save Paris Airbnb data to JSON file"""
    if not results:
        print("❌ No data to save")
        return False
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Successfully saved {len(results)} listings to:")
        print(f"   {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return False

def analyze_paris_data(results):
    """Quick analysis of Paris Airbnb data"""
    if not results:
        return
    
    print("📊 QUICK ANALYSIS OF PARIS DATA:")
    print("-" * 30)
    
    # Basic statistics
    total_listings = len(results)
    
    # Price analysis
    prices = [listing.get('price', {}).get('unit', {}).get('amount', 0) for listing in results]
    valid_prices = [p for p in prices if p > 0]
    
    # Rating analysis
    ratings = [listing.get('rating', {}).get('value', 0) for listing in results]
    valid_ratings = [r for r in ratings if r > 0]
    
    # Superhost count
    superhosts = sum(1 for listing in results 
                    if listing.get('passportData', {}).get('isSuperhost', False))
    
    print(f"🏠 Total Listings: {total_listings}")
    print(f"💰 Average Price: €{sum(valid_prices)/len(valid_prices):.2f}" if valid_prices else "💰 No price data")
    print(f"📈 Price Range: €{min(valid_prices)} - €{max(valid_prices)}" if valid_prices else "")
    print(f"⭐ Average Rating: {sum(valid_ratings)/len(valid_ratings):.1f}/5" if valid_ratings else "⭐ No rating data")
    print(f"🏆 Superhosts: {superhosts} ({superhosts/total_listings*100:.1f}%)")

def main():
    """Main function to collect and save Paris Airbnb data"""
    print("🎯 PARIS AIRBNB DATA COLLECTOR")
    print("=" * 50)
    
    # Step 1: Search for Paris listings
    results = search_paris_airbnb()
    
    if not results:
        print("❌ No results found. Exiting.")
        return
    
    # Step 2: Save the data
    success = save_paris_data(results)
    
    # Step 3: Quick analysis
    if success:
        analyze_paris_data(results)
    
    # Step 4: Next steps
    print("\n" + "=" * 50)
    print("\n2. The data is saved here:")
    print("search_from_url.json")
 

if __name__ == "__main__":
    main()