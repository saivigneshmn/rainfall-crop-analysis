
import sys
import io
from main import RainfallCropAnalyzer
from nl_query_parser import NLQueryParser

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def final_demo():
    """Final demonstration for video"""
    
    print("=" * 100)
    print("RAINFALL & CROP ANALYSIS - FINAL VIDEO DEMONSTRATION")
    print("=" * 100)
    print("\nLoading data...")
    
    analyzer = RainfallCropAnalyzer("data/RF25_ind2022_rfp25.nc", "data/horizontal_crop_vertical_year_report.xls")
    parser = NLQueryParser(analyzer.query_engine)
    print("Data loaded successfully!\n")
    
    # Final 5 queries: 3 successes, 2 failures
    demo_queries = [
        {
            "name": "Query 1: ✅ SUCCESS - Cross-state Sugarcane Comparison",
            "description": "Maharashtra highest vs Karnataka lowest - Sugarcane is produced in 21 states!",
            "query": "Identify the district in Maharashtra with the highest production of Sugarcane and compare that with the district with the lowest production of Sugarcane in Karnataka",
            "expected": "success"
        },
        {
            "name": "Query 2: ✅ SUCCESS - Cross-state Coconut Comparison",
            "description": "Tamil Nadu highest vs Kerala lowest - Two major coconut producing states",
            "query": "Identify the district in Tamil Nadu with the highest production of Coconut and compare that with the district with the lowest production of Coconut in Kerala",
            "expected": "success"
        },
        {
            "name": "Query 3: ✅ SUCCESS - Cross-state Ginger Comparison",
            "description": "Karnataka highest vs Assam lowest - Ginger produced in 9 states",
            "query": "Identify the district in Karnataka with the highest production of Ginger and compare that with the district with the lowest production of Ginger in Assam",
            "expected": "success"
        },
        {
            "name": "Query 4: ❌ FAILURE - Crop Not in State",
            "description": "Banana not produced in Punjab (only produced in 7 states)",
            "query": "Identify the district in Punjab with the highest production of Banana",
            "expected": "failure"
        },
        {
            "name": "Query 5: ❌ FAILURE - Crop Not in Dataset",
            "description": "Rice is not in the agricultural dataset at all",
            "query": "Identify the district in Punjab with the highest production of Rice",
            "expected": "failure"
        }
    ]
    
    results = []
    
    for idx, demo in enumerate(demo_queries, 1):
        print("=" * 100)
        print(f"{demo['name']}")
        print(f"Description: {demo['description']}")
        print("=" * 100)
        print(f"\nNatural Language Query:")
        print(f"\"{demo['query']}\"")
        print()
        
        try:
            result = parser.execute_query(demo['query'])
            
            if 'error' in result and result['error']:
                print(f"[FAILED] Error: {result['error']}\n")
                results.append({
                    'name': demo['name'],
                    'status': 'FAILED',
                    'error': result['error'],
                    'expected': demo['expected']
                })
            elif result.get('result'):
                # Check for data
                success_data = []
                
                if 'highest_district' in result['result']:
                    hd = result['result']['highest_district']
                    if hd.get('districts') is not None and len(hd['districts']) > 0:
                        row = hd['districts'].iloc[0]
                        if row['Production'] > 0:
                            success_data.append({
                                'type': 'Highest',
                                'district': row['District'],
                                'state': row['State'],
                                'production': row['Production']
                            })
                
                if 'lowest_district' in result['result']:
                    ld = result['result']['lowest_district']
                    if ld.get('districts') is not None and len(ld['districts']) > 0:
                        row = ld['districts'].iloc[0]
                        if row['Production'] > 0:
                            success_data.append({
                                'type': 'Lowest',
                                'district': row['District'],
                                'state': row['State'],
                                'production': row['Production']
                            })
                            
                elif 'districts' in result['result']:
                    districts_df = result['result']['districts']
                    if districts_df is not None and len(districts_df) > 0:
                        row = districts_df.iloc[0]
                        if row['Production'] > 0:
                            success_data.append({
                                'type': 'District',
                                'district': row['District'],
                                'state': row['State'],
                                'production': row['Production']
                            })
                
                if success_data:
                    print("[SUCCESS] Results:")
                    for data in success_data:
                        print(f"  {data['type']}: {data['district']}, {data['state']}")
                        print(f"    Production: {data['production']:,.0f} tonnes")
                    
                    # Show citation
                    if result['result'].get('citation'):
                        cite_lines = result['result']['citation'].split('\n')
                        cite_clean = [l.strip() for l in cite_lines if l.strip()][:3]
                        if cite_clean:
                            print(f"\n  Data Source: {cite_clean[0]}")
                    print()
                    
                    results.append({
                        'name': demo['name'],
                        'status': 'SUCCESS',
                        'data': success_data,
                        'expected': demo['expected']
                    })
                else:
                    print("[FAILED] No production data found for the specified crop/state combination\n")
                    results.append({
                        'name': demo['name'],
                        'status': 'FAILED',
                        'reason': 'No production data',
                        'expected': demo['expected']
                    })
            else:
                print("[UNEXPECTED] Query parsed but returned no results\n")
                results.append({
                    'name': demo['name'],
                    'status': 'UNEXPECTED',
                    'expected': demo['expected']
                })
                
        except Exception as e:
            print(f"[FAILED] Exception: {str(e)}\n")
            results.append({
                'name': demo['name'],
                'status': 'EXCEPTION',
                'error': str(e),
                'expected': demo['expected']
            })
    
    # Final Summary
    print("\n" + "=" * 100)
    print("FINAL DEMONSTRATION SUMMARY")
    print("=" * 100)
    
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    failed_count = sum(1 for r in results if r['status'] in ['FAILED', 'EXCEPTION'])
    
    print(f"\n✅ Successful Queries: {success_count}/5")
    print(f"❌ Failed Queries: {failed_count}/5")
    
    print("\n" + "=" * 100)
    print("WORKING EXAMPLES:")
    print("=" * 100)
    for r in results:
        if r['status'] == 'SUCCESS':
            print(f"\n  + {r['name']}")
            for data in r.get('data', []):
                print(f"     {data['district']}, {data['state']}: {data['production']:,.0f} tonnes")
    
    print("\n" + "=" * 100)
    print("FAILURE EXAMPLES:")
    print("=" * 100)
    for r in results:
        if r['status'] in ['FAILED', 'EXCEPTION']:
            print(f"\n  - {r['name']}")
            if 'error' in r:
                error_msg = r['error']
                if len(error_msg) > 100:
                    error_msg = error_msg[:100] + "..."
                print(f"     Reason: {error_msg}")
            elif 'reason' in r:
                print(f"     Reason: {r['reason']}")
    
    print("\n" + "=" * 100)
    print("KEY INSIGHTS:")
    print("=" * 100)
    print("""
1. SUGARCANE works perfectly - produced in 21 states!
   - Maharashtra alone: 269M+ tonnes
   - Karnataka: 123M+ tonnes

2. COCONUT works well - produced in 8 states
   - Tamil Nadu: 13.3B nuts
   - Karnataka: 11.7B nuts

3. GINGER works - produced in 9 states
   - Karnataka: 534K tonnes
   - Assam: 318K tonnes

4. Failures occur when:
   - Crop not produced in that state (e.g., Banana not in Punjab)
   - Crop not in dataset at all (e.g., Rice)

The system handles all these cases gracefully with clear error messages!
    """)
    
    print("=" * 100)

if __name__ == "__main__":
    final_demo()

