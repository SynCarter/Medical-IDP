# 👥 User Guide for NGO Healthcare Planners

## Welcome!

This system helps you identify medical deserts, allocate healthcare resources, and make data-driven decisions to save lives. **No technical expertise required!**

---

## 🚀 Getting Started (3 Steps)

### Step 1: Launch the System

**Option A: Web Interface (Recommended)**
```bash
python main.py web
```
Your browser will open automatically to http://localhost:8501

**Option B: Command Line**
```bash
python main.py analyze
```

### Step 2: Navigate the Interface

The dashboard has 5 main sections:
- 📊 **Dashboard** - Overview statistics
- 🤖 **AI Assistant** - Ask questions in plain English
- 🗺️ **Interactive Map** - Visual exploration
- 📋 **Facility Explorer** - Browse all facilities
- 📈 **Reports** - Download analysis

### Step 3: Start Exploring!

Click on example questions or type your own query.

---

## 💡 Example Questions You Can Ask

### Finding Medical Deserts
- "Which regions in Ghana are medical deserts?"
- "Show me areas with the worst healthcare access"
- "Where are the critical gaps in healthcare?"

### Staffing & Resource Allocation
- "Where should we send more surgeons?"
- "Which facilities need urgent staff support?"
- "What are the most common staffing gaps?"

### Equipment & Infrastructure
- "Which hospitals need MRI machines?"
- "Show me facilities with broken equipment"
- "What are the critical equipment shortages?"

### Maternal Healthcare
- "Where are the gaps in maternal healthcare?"
- "Which regions need cesarean section capabilities?"
- "Show me maternity service availability"

### Emergency Services
- "Where are emergency services lacking?"
- "Which areas have no ICU facilities?"
- "Show me trauma care capabilities"

---

## 📊 Understanding the Dashboard

### Key Metrics

**Desert Risk Score (0-100)**
- 🔴 75-100: CRITICAL - Immediate intervention needed
- 🟠 60-74: HIGH - Prioritize for resources
- 🟡 40-59: MODERATE - Monitor closely
- 🟢 0-39: LOW - Adequate coverage

**Capability Score (0-100)**
- Higher = More resources and services available
- Considers: Specialties, Equipment, Procedures

### Color Coding

On the map:
- 🔴 **Red markers** = Critical medical deserts
- 🟠 **Orange markers** = High risk
- 🟡 **Yellow markers** = Moderate risk
- 🟢 **Green markers** = Well-resourced

---

## 🤖 Using the AI Assistant

### How It Works

1. **Ask a question** in natural language
2. **AI analyzes** all facility data
3. **Provides answer** with reasoning
4. **Shows citations** - every claim is backed by data
5. **Recommends actions** you can take

### Best Practices

✅ **DO:**
- Ask specific questions
- Use natural language (like talking to a colleague)
- Explore different regions
- Check the citations to verify

❌ **DON'T:**
- Use technical jargon (unless you want to)
- Expect real-time data (data has a timestamp)
- Rely solely on AI - use your expertise too

### Understanding AI Responses

Every response includes:

1. **Analysis** - What the data shows
2. **Findings** - Key insights discovered
3. **Recommendations** - Actionable next steps
4. **Reasoning Chain** - How the AI reached conclusions
5. **Citations** - Which data supports each claim

---

## 🗺️ Using the Interactive Map

### Navigation

- **Zoom**: Mouse wheel or +/- buttons
- **Pan**: Click and drag
- **Click markers**: View facility details
- **Toggle layers**: Use the layer control (top right)

### Map Features

**Markers**
- Click any marker to see:
  - Facility name and type
  - Risk and capability scores
  - Available specialties
  - Equipment inventory
  - Critical gaps

**Heatmap Layer**
- Shows concentration of medical deserts
- Warmer colors = Higher risk areas
- Helps identify regional patterns

**Filter by Risk Level**
- Toggle different risk categories on/off
- Focus on critical areas first

---

## 📋 Facility Explorer

### Filtering

Use filters to narrow down facilities:

**By Region**
- Select specific region from dropdown
- Compare regional differences

**By Risk Level**
- Focus on critical facilities
- Or review well-resourced areas

**By Facility Type**
- Teaching hospitals
- Regional hospitals
- District hospitals
- Mission hospitals

### Facility Cards

Each card shows:
- 🏥 Name and location
- 📊 Risk and capability scores
- ✅ Available services
- ❌ Critical gaps

---

## 📈 Reports & Export

### Generating Reports

1. Go to **Reports** tab
2. Review identified medical deserts
3. Check regional breakdown
4. See top critical gaps

### Exporting Data

**CSV Export**
- Complete facility analysis
- All scores and capabilities
- Import into Excel or other tools

**JSON Export**
- Medical desert data
- Programmatic access
- Integration with other systems

**HTML Reports**
- Professional-looking reports
- Share with stakeholders
- Print or email

### What to Include in Reports

When presenting to leadership:

1. **Executive Summary**
   - Total facilities analyzed
   - Number of critical cases
   - Top 3 recommendations

2. **Regional Breakdown**
   - Highest risk regions
   - Facilities affected
   - Resource needs

3. **Specific Actions**
   - Where to send doctors
   - Equipment to deploy
   - Infrastructure to build

4. **Supporting Data**
   - Maps and visualizations
   - Citations and sources
   - Success metrics

---

## 🎯 Common Workflows

### 1. Monthly Resource Planning

```
1. Launch system → Dashboard
2. Check "High Risk" facilities
3. Note regions with increased risk
4. Use AI: "What resources are most needed this month?"
5. Export recommendations
6. Present to team
```

### 2. Emergency Response

```
1. Interactive Map → Toggle "Critical" only
2. Identify affected facilities
3. AI Assistant: "What are urgent needs in [region]?"
4. Check staffing gaps
5. Coordinate deployment
```

### 3. Budget Allocation

```
1. Reports → Regional Analysis
2. Sort by "Total Gaps"
3. AI: "Where would $X have most impact?"
4. Export cost-benefit data
5. Prepare budget proposal
```

### 4. Performance Tracking

```
1. Facility Explorer → Filter by region
2. Compare before/after scores
3. Generate progress reports
4. Share with donors
```

---

## 🔍 Reading Citations

Every AI conclusion includes citations showing where the data came from.

**Format:**
```
[Facility ID]: "Source text from facility record"
```

**Example:**
```
Citation: F003 - "No neurosurgeon available"
          F006 - "No surgeon on permanent staff"
          F011 - "Only 2 doctors on staff"

Conclusion: Northern region critically short on surgical staff
```

**Why This Matters:**
- Verify AI conclusions
- Trace decisions back to source
- Build trust with stakeholders
- Ensure accountability

---

## ⚡ Quick Tips

### Saving Time

1. **Use Example Queries** - Click pre-written questions
2. **Bookmark Common Filters** - Set up your regular views
3. **Export Templates** - Reuse report formats
4. **Check Recent Chats** - Reference past analyses

### Getting Better Results

1. **Be Specific** - "Tamale region surgeons" vs "doctors"
2. **Ask Follow-ups** - Dig deeper into answers
3. **Cross-reference** - Check map + data + AI
4. **Update Regularly** - Upload new facility data

### Collaborating

1. **Share URLs** - Send map links to colleagues
2. **Export Reports** - Professional PDFs for meetings
3. **Screenshot Insights** - Quick visual communication
4. **Document Decisions** - Keep AI reasoning for records

---

## 🆘 Troubleshooting

### "No results found"
→ Try broader query or check filters

### "Data seems outdated"
→ Check dataset timestamp, request update

### "AI response unclear"
→ Ask follow-up: "Can you explain that differently?"

### "Map not loading"
→ Refresh page or try different browser

### "Export not working"
→ Check file permissions, try different format

---

## 📞 Support & Feedback

### Getting Help

1. **Help Button** - In-app guidance
2. **Example Queries** - Learn by example
3. **Documentation** - README.md
4. **Team Support** - Contact your admin

### Providing Feedback

Your input improves the system!

**Report Issues:**
- Incorrect data
- Confusing interface
- Missing features
- Bug reports

**Request Features:**
- New query types
- Different visualizations
- Export formats
- Integration needs

---

## 📚 Additional Resources

- **README.md** - Technical documentation
- **INSTALLATION.md** - Setup guide
- **Demo Script** - Try without installation
- **Example Data** - Sample Ghana facilities

---

## 🎯 Success Metrics

Track your impact:

✅ Time saved vs. manual analysis
✅ Resources allocated to high-priority areas
✅ Reduction in response time
✅ Lives potentially saved
✅ Stakeholder satisfaction

---

**Remember: You're not just using software—you're saving lives by connecting expertise to need.**

For questions or support, contact your system administrator.

---

*Last Updated: February 2026*
