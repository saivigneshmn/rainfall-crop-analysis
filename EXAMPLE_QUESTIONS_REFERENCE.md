# Example Questions Reference Guide

This document lists all example questions available in the app, organized by category. These questions have been tested and should work correctly with the Natural Language Query Parser.

## 📊 Total Questions: 32

---

## 🎯 Challenge Questions (4)
**These are the original challenge questions from the requirements.**

1. **Multi-part Query**
   - "Compare the average annual rainfall in Tamil Nadu and Karnataka for the last 2 available years. In parallel, list the top 5 most produced crops in Tamil Nadu and Karnataka during the same period, citing all data sources."

2. **District Comparison**
   - "Identify the district in Tamil Nadu with the highest production of Sugarcane in the most recent year available and compare that with the district with the lowest production of Sugarcane in west bengal"

3. **Trend & Correlation**
   - "Analyze the production trend of Sugarcane in Andhra Pradesh. Correlate this trend with the corresponding climate data for the same period and provide a summary of the apparent impact."

4. **Policy Arguments**
   - "A policy advisor is proposing a scheme to promote Sugarcane over Banana in Tamil Nadu. Based on historical data from the last 3 years, what are the three most compelling data-backed arguments to support this policy? Your answer must synthesize data from both climate and agricultural sources."

---

## 📚 Simple Queries (4)
**Beginner-friendly, single-answer questions.**

1. **Rainfall Query**
   - "What is the average annual rainfall in Maharashtra?"

2. **Top Crops**
   - "List the top 10 most produced crops in Karnataka"

3. **District Production**
   - "Which district in Andhra Pradesh has the highest production of Coconut?"

4. **Rainfall Comparison**
   - "Compare rainfall between Kerala and Tamil Nadu"

---

## 🔄 Variations & Edge Cases (7)
**Different phrasings and edge cases.**

1. **Year-specific Query**
   - "What are the most produced crops in Gujarat for the year 2023?"

2. **Lowest Production**
   - "Find the district with the lowest production of Ginger in Assam"

3. **Specific Year Comparison**
   - "Compare average rainfall in Uttar Pradesh and Bihar for 2022"

4. **Multiple Years, More Crops**
   - "Show me the top 15 crops produced in Maharashtra during the last 2 years"

5. **Implicit State**
   - "What is the highest production district for Ginger in the most recent year available?"

6. **Multiple Comparisons**
   - "List top crops in West Bengal and compare with top crops in Odisha"

7. **Combined Trend & Correlation**
   - "Show me the production trend of Tobacco and correlate it with climate data in Andhra Pradesh"

---

## 🗺️ Cross-State Comparisons (3)
**Comparing districts across different states.**

1. **Turmeric Comparison**
   - "Identify the district in Karnataka with the highest production of Turmeric and compare that with the district with the lowest production of Turmeric in Tamil Nadu"

2. **Coconut Comparison**
   - "Find the district in Kerala with the highest production of Coconut and compare that with the district with the lowest production of Coconut in Karnataka"

3. **Cotton Comparison**
   - "Identify the district in Maharashtra with the highest production of Cotton and compare that with the district with the lowest production of Cotton in Gujarat"

---

## 📈 Trend Analysis Queries (3)
**Analyzing production trends over time.**

1. **Banana Production**
   - "Analyze the production trend of Banana in Tamil Nadu over the last decade"

2. **Turmeric Analysis**
   - "What is the production trend of Turmeric in Karnataka?"

3. **Cotton Analysis**
   - "Analyze the production trend of Cotton in Gujarat"

---

## 🔗 Correlation Queries (3)
**Finding relationships between rainfall and production.**

1. **Sugarcane & Rainfall**
   - "Correlate the production of Sugarcane in Uttar Pradesh with rainfall data"

2. **Banana & Climate**
   - "What is the relationship between Banana production and climate data in Kerala?"

3. **Coconut & Rainfall**
   - "Analyze how Coconut production in Tamil Nadu correlates with rainfall patterns"

---

## ⚖️ Policy & Comparison Queries (3)
**Generating data-backed policy arguments.**

1. **Cotton vs Sugarcane**
   - "A policy maker wants to promote Cotton over Sugarcane in Maharashtra. Based on the last 3 years of data, what are three data-backed arguments?"

2. **Banana vs Coconut**
   - "Compare Banana and Coconut production in Kerala and provide arguments for promoting one over the other"

3. **Turmeric vs Ginger**
   - "Give me arguments for promoting Turmeric over Ginger in Karnataka based on historical production data"

---

## 🌐 Complex Multi-part Queries (3)
**Combining multiple query types in one question.**

1. **Multi-state Rainfall & Crops**
   - "Compare rainfall in Kerala, Tamil Nadu, and Karnataka. Also show the top 3 crops in each state for 2022"

2. **Trend + District Analysis**
   - "Analyze the trend of Sugarcane production in Maharashtra and identify the top 5 districts producing it in 2023"

3. **Correlation + Districts**
   - "Correlate Cotton production in Gujarat with rainfall data and list the top producing districts"

---

## 🏢 Real-world Scenarios (3)
**Business and research use cases.**

1. **Business Decision**
   - "A food processing company wants to set up a Sugarcane processing unit. Which state should they choose - Tamil Nadu or Karnataka? Provide data-backed recommendations."

2. **Agricultural Planning**
   - "For agricultural planning, compare the top 5 crops in Andhra Pradesh and Telangana and their production trends"

3. **Research Query**
   - "A researcher needs to understand rainfall patterns. Compare average annual rainfall across Maharashtra, Karnataka, and Tamil Nadu for available years"

---

## ✅ Testing Checklist for Evaluators

When testing the system, evaluators might try:

- [ ] Simple single queries (rainfall, top crops)
- [ ] Complex multi-part queries
- [ ] Cross-state comparisons
- [ ] Trend analysis over time
- [ ] Correlation between rainfall and production
- [ ] Policy argument generation
- [ ] Year-specific queries (2022, 2023)
- [ ] Multiple state comparisons (3+ states)
- [ ] District-level queries
- [ ] Questions with implicit states/crops
- [ ] Edge cases (lowest production, implicit parameters)

---

## 📝 Query Patterns Covered

✅ **Rainfall Queries**
- Single state average rainfall
- Multi-state comparison
- Year-specific rainfall

✅ **Crop Production Queries**
- Top N crops by state
- District-level production (highest/lowest)
- Cross-state district comparison

✅ **Trend Analysis**
- Production trends over time
- Decadal trends

✅ **Correlation**
- Rainfall vs production
- Climate data correlation

✅ **Policy Support**
- Crop comparison arguments
- Data-backed recommendations

✅ **Multi-part Queries**
- Combining rainfall + crops
- Trend + district analysis
- Correlation + rankings

---

## 💡 Tips for Evaluators

1. **State Names**: Use full state names (e.g., "Tamil Nadu", "Andhra Pradesh")
2. **Crop Names**: Use capitalized crop names (e.g., "Sugarcane", "Coconut", "Banana")
3. **Years**: Specify years if needed (2022, 2023, "last 2 years", "most recent year")
4. **Comparisons**: Use words like "compare", "vs", "versus", "highest", "lowest"
5. **Multi-part**: Use phrases like "in parallel", "also", "and" to combine queries

---

## 🚨 Known Limitations

- Some crops may not be available in all states (system handles gracefully)
- Rainfall data available for 2022 only
- Crop data available for 2022-2023
- District names must match data exactly (system tries fuzzy matching)

