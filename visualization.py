"""
Visualization module for medical desert analysis
Creates interactive maps showing facility capabilities and risk areas
"""

import folium
from folium import plugins
import pandas as pd
from typing import List, Dict, Any
import json


def create_medical_desert_map(facility_profiles: List[Any], 
                              output_path: str = 'medical_desert_map.html'):
    """
    Create an interactive map showing medical deserts in Ghana
    
    Color coding:
    - Green: Well-resourced (low desert risk)
    - Yellow: Moderate risk
    - Orange: High risk
    - Red: Critical medical desert
    """
    
    # Center map on Ghana
    ghana_center = [7.9465, -1.0232]
    m = folium.Map(
        location=ghana_center,
        zoom_start=7,
        tiles='OpenStreetMap'
    )
    
    # Create feature groups for different risk levels
    low_risk = folium.FeatureGroup(name='Low Risk (Well-resourced)')
    moderate_risk = folium.FeatureGroup(name='Moderate Risk')
    high_risk = folium.FeatureGroup(name='High Risk')
    critical_risk = folium.FeatureGroup(name='CRITICAL - Medical Desert')
    
    # Add facilities to appropriate groups
    for profile in facility_profiles:
        lat, lon = profile.coordinates
        
        # Determine risk level and color
        if profile.desert_risk_score >= 75:
            color = 'red'
            icon = 'exclamation-triangle'
            group = critical_risk
            risk_label = 'CRITICAL'
        elif profile.desert_risk_score >= 60:
            color = 'orange'
            icon = 'warning'
            group = high_risk
            risk_label = 'HIGH'
        elif profile.desert_risk_score >= 40:
            color = 'yellow'
            icon = 'info-sign'
            group = moderate_risk
            risk_label = 'MODERATE'
        else:
            color = 'green'
            icon = 'ok-sign'
            group = low_risk
            risk_label = 'LOW'
        
        # Create detailed popup
        popup_html = f"""
        <div style="width: 300px; font-family: Arial;">
            <h4 style="margin: 0; color: {color};">{profile.facility_name}</h4>
            <p style="margin: 5px 0;"><b>Type:</b> {profile.facility_type}</p>
            <p style="margin: 5px 0;"><b>Region:</b> {profile.region}</p>
            <p style="margin: 5px 0;"><b>District:</b> {profile.district}</p>
            
            <hr style="margin: 10px 0;">
            
            <p style="margin: 5px 0;"><b>Desert Risk Score:</b> 
                <span style="color: {color}; font-weight: bold;">{profile.desert_risk_score:.1f}/100 ({risk_label})</span>
            </p>
            <p style="margin: 5px 0;"><b>Capability Score:</b> {profile.capability_score:.1f}/100</p>
            
            <hr style="margin: 10px 0;">
            
            <p style="margin: 5px 0;"><b>Specialties ({len(profile.specialties)}):</b></p>
            <ul style="margin: 5px 0; padding-left: 20px;">
                {''.join([f'<li>{s}</li>' for s in profile.specialties[:5]])}
                {f'<li><i>...and {len(profile.specialties) - 5} more</i></li>' if len(profile.specialties) > 5 else ''}
            </ul>
            
            <p style="margin: 5px 0;"><b>Key Equipment ({len(profile.equipment)}):</b></p>
            <ul style="margin: 5px 0; padding-left: 20px;">
                {''.join([f'<li>{e}</li>' for e in profile.equipment[:5]])}
                {f'<li><i>...and {len(profile.equipment) - 5} more</i></li>' if len(profile.equipment) > 5 else ''}
            </ul>
            
            {f'''
            <hr style="margin: 10px 0;">
            <p style="margin: 5px 0; color: red;"><b>⚠️ Critical Gaps ({len(profile.gaps)}):</b></p>
            <ul style="margin: 5px 0; padding-left: 20px;">
                {''.join([f'<li style="color: red;">{g}</li>' for g in profile.gaps[:3]])}
                {f'<li><i>...and {len(profile.gaps) - 3} more</i></li>' if len(profile.gaps) > 3 else ''}
            </ul>
            ''' if profile.gaps else ''}
        </div>
        """
        
        # Add marker
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"{profile.facility_name} - Risk: {profile.desert_risk_score:.0f}",
            icon=folium.Icon(color=color, icon=icon, prefix='glyphicon')
        ).add_to(group)
    
    # Add all groups to map
    low_risk.add_to(m)
    moderate_risk.add_to(m)
    high_risk.add_to(m)
    critical_risk.add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add regional heat map for desert risk
    heat_data = [[p.coordinates[0], p.coordinates[1], p.desert_risk_score/100] 
                 for p in facility_profiles]
    plugins.HeatMap(heat_data, name='Desert Risk Heatmap', 
                   min_opacity=0.3, radius=25, blur=25,
                   gradient={0.0: 'green', 0.4: 'yellow', 
                            0.6: 'orange', 0.8: 'red'}).add_to(m)
    
    # Add title
    title_html = '''
    <div style="position: fixed; 
                top: 10px; left: 50px; width: 400px; height: 90px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px; font-family: Arial;">
        <h4 style="margin: 0;">Ghana Medical Desert Analysis</h4>
        <p style="margin: 5px 0; font-size: 12px;">
            Interactive map showing healthcare facility capabilities and medical desert risk scores.
        </p>
        <p style="margin: 5px 0; font-size: 11px;">
            <b>Red markers:</b> Critical medical deserts | 
            <b>Green markers:</b> Well-resourced areas
        </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Save map
    m.save(output_path)
    return output_path


def create_summary_statistics(facility_profiles: List[Any]) -> Dict[str, Any]:
    """Generate summary statistics for the dashboard"""
    
    total_facilities = len(facility_profiles)
    
    # Risk distribution
    critical = sum(1 for p in facility_profiles if p.desert_risk_score >= 75)
    high = sum(1 for p in facility_profiles if 60 <= p.desert_risk_score < 75)
    moderate = sum(1 for p in facility_profiles if 40 <= p.desert_risk_score < 60)
    low = sum(1 for p in facility_profiles if p.desert_risk_score < 40)
    
    # Regional analysis
    region_stats = {}
    for profile in facility_profiles:
        region = profile.region
        if region not in region_stats:
            region_stats[region] = {
                'count': 0,
                'avg_desert_risk': 0,
                'avg_capability': 0,
                'total_gaps': 0
            }
        
        region_stats[region]['count'] += 1
        region_stats[region]['avg_desert_risk'] += profile.desert_risk_score
        region_stats[region]['avg_capability'] += profile.capability_score
        region_stats[region]['total_gaps'] += len(profile.gaps)
    
    # Calculate averages
    for region, stats in region_stats.items():
        count = stats['count']
        stats['avg_desert_risk'] /= count
        stats['avg_capability'] /= count
    
    # Most common gaps
    all_gaps = [gap for p in facility_profiles for gap in p.gaps]
    gap_counts = {}
    for gap in all_gaps:
        gap_counts[gap] = gap_counts.get(gap, 0) + 1
    
    top_gaps = sorted(gap_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        'total_facilities': total_facilities,
        'risk_distribution': {
            'critical': critical,
            'high': high,
            'moderate': moderate,
            'low': low
        },
        'regional_stats': region_stats,
        'top_gaps': [{'gap': gap, 'count': count} for gap, count in top_gaps],
        'avg_desert_risk': sum(p.desert_risk_score for p in facility_profiles) / total_facilities,
        'avg_capability': sum(p.capability_score for p in facility_profiles) / total_facilities
    }


def generate_regional_report(facility_profiles: List[Any], output_path: str = 'regional_report.html'):
    """Generate a detailed regional analysis report"""
    
    stats = create_summary_statistics(facility_profiles)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ghana Healthcare Regional Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }}
            .header {{
                background-color: #2c3e50;
                color: white;
                padding: 20px;
                text-align: center;
            }}
            .summary {{
                background-color: white;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .stat-grid {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
                margin: 20px 0;
            }}
            .stat-box {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
            }}
            .stat-box.critical {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            }}
            .stat-box.high {{
                background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            }}
            .stat-box.moderate {{
                background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);
            }}
            .stat-box.low {{
                background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            }}
            .stat-value {{
                font-size: 36px;
                font-weight: bold;
            }}
            .stat-label {{
                font-size: 14px;
                margin-top: 5px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                background-color: white;
            }}
            th {{
                background-color: #34495e;
                color: white;
                padding: 12px;
                text-align: left;
            }}
            td {{
                padding: 10px;
                border-bottom: 1px solid #ddd;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            .risk-critical {{ color: #e74c3c; font-weight: bold; }}
            .risk-high {{ color: #e67e22; font-weight: bold; }}
            .risk-moderate {{ color: #f39c12; }}
            .risk-low {{ color: #27ae60; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏥 Ghana Healthcare Infrastructure Report</h1>
            <p>Medical Desert Analysis & Resource Allocation Planning</p>
        </div>
        
        <div class="summary">
            <h2>Executive Summary</h2>
            <p><b>Total Facilities Analyzed:</b> {stats['total_facilities']}</p>
            <p><b>Average Desert Risk Score:</b> {stats['avg_desert_risk']:.1f}/100</p>
            <p><b>Average Capability Score:</b> {stats['avg_capability']:.1f}/100</p>
            
            <div class="stat-grid">
                <div class="stat-box critical">
                    <div class="stat-value">{stats['risk_distribution']['critical']}</div>
                    <div class="stat-label">CRITICAL RISK</div>
                </div>
                <div class="stat-box high">
                    <div class="stat-value">{stats['risk_distribution']['high']}</div>
                    <div class="stat-label">HIGH RISK</div>
                </div>
                <div class="stat-box moderate">
                    <div class="stat-value">{stats['risk_distribution']['moderate']}</div>
                    <div class="stat-label">MODERATE RISK</div>
                </div>
                <div class="stat-box low">
                    <div class="stat-value">{stats['risk_distribution']['low']}</div>
                    <div class="stat-label">LOW RISK</div>
                </div>
            </div>
        </div>
        
        <div class="summary">
            <h2>Regional Analysis</h2>
            <table>
                <tr>
                    <th>Region</th>
                    <th>Facilities</th>
                    <th>Avg Desert Risk</th>
                    <th>Avg Capability</th>
                    <th>Total Gaps</th>
                    <th>Priority</th>
                </tr>
    """
    
    # Sort regions by desert risk
    sorted_regions = sorted(stats['regional_stats'].items(), 
                          key=lambda x: x[1]['avg_desert_risk'], 
                          reverse=True)
    
    for region, data in sorted_regions:
        risk = data['avg_desert_risk']
        if risk >= 75:
            risk_class = 'risk-critical'
            priority = 'CRITICAL'
        elif risk >= 60:
            risk_class = 'risk-high'
            priority = 'HIGH'
        elif risk >= 40:
            risk_class = 'risk-moderate'
            priority = 'MODERATE'
        else:
            risk_class = 'risk-low'
            priority = 'LOW'
        
        html += f"""
                <tr>
                    <td><b>{region}</b></td>
                    <td>{data['count']}</td>
                    <td class="{risk_class}">{risk:.1f}</td>
                    <td>{data['avg_capability']:.1f}</td>
                    <td>{data['total_gaps']}</td>
                    <td class="{risk_class}">{priority}</td>
                </tr>
        """
    
    html += """
            </table>
        </div>
        
        <div class="summary">
            <h2>Most Common Infrastructure Gaps</h2>
            <table>
                <tr>
                    <th>Gap/Need</th>
                    <th>Facilities Affected</th>
                </tr>
    """
    
    for gap_data in stats['top_gaps']:
        html += f"""
                <tr>
                    <td>{gap_data['gap']}</td>
                    <td><b>{gap_data['count']}</b></td>
                </tr>
        """
    
    html += """
            </table>
        </div>
        
        <div class="summary">
            <h2>Recommendations</h2>
            <ol>
    """
    
    # Generate top 5 recommendations
    if sorted_regions[0][1]['avg_desert_risk'] >= 70:
        html += f"<li><b>URGENT:</b> Deploy emergency medical resources to {sorted_regions[0][0]} region (Risk: {sorted_regions[0][1]['avg_desert_risk']:.1f})</li>"
    
    if stats['top_gaps']:
        html += f"<li>Address the most common gap across facilities: {stats['top_gaps'][0]['gap']} (affects {stats['top_gaps'][0]['count']} facilities)</li>"
    
    high_risk_count = stats['risk_distribution']['critical'] + stats['risk_distribution']['high']
    if high_risk_count > 0:
        html += f"<li>Prioritize specialist recruitment for {high_risk_count} high-risk facilities</li>"
    
    html += """
                <li>Establish telemedicine connections between well-resourced and underserved facilities</li>
                <li>Create mobile surgical units to serve remote districts</li>
            </ol>
        </div>
    </body>
    </html>
    """
    
    with open(output_path, 'w') as f:
        f.write(html)
    
    return output_path


if __name__ == "__main__":
    from document_parser import parse_facility_dataset
    
    # Load data
    profiles = parse_facility_dataset('/home/claude/medical_desert_agent/ghana_facilities.csv')
    
    # Create visualizations
    map_path = create_medical_desert_map(profiles)
    print(f"Created map: {map_path}")
    
    report_path = generate_regional_report(profiles)
    print(f"Created report: {report_path}")
    
    # Print statistics
    stats = create_summary_statistics(profiles)
    print(f"\nStatistics:")
    print(f"  Total facilities: {stats['total_facilities']}")
    print(f"  Critical risk: {stats['risk_distribution']['critical']}")
    print(f"  High risk: {stats['risk_distribution']['high']}")
