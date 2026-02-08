"""
Map Generator - Interactive visualization of medical facilities and deserts
"""

import folium
from folium import plugins
import pandas as pd
from typing import List, Dict, Any, Optional
import json


class MapGenerator:
    """Generates interactive maps showing facility locations and capability levels"""
    
    # Ghana's approximate center
    GHANA_CENTER = [7.9465, -1.0232]
    
    # Color scheme for facility capabilities
    COLORS = {
        'excellent': '#2ecc71',  # Green
        'good': '#3498db',       # Blue
        'moderate': '#f39c12',   # Orange
        'poor': '#e74c3c',       # Red
        'critical': '#c0392b'    # Dark red
    }
    
    def __init__(self):
        pass
    
    def create_facility_map(
        self,
        facilities: List[Dict[str, Any]],
        center: Optional[List[float]] = None,
        zoom_start: int = 7
    ) -> folium.Map:
        """
        Create interactive map with all facilities
        
        Args:
            facilities: List of facility dictionaries with extracted capabilities
            center: Map center coordinates [lat, lon]
            zoom_start: Initial zoom level
            
        Returns:
            Folium map object
        """
        if center is None:
            center = self.GHANA_CENTER
        
        # Create base map
        m = folium.Map(
            location=center,
            zoom_start=zoom_start,
            tiles='OpenStreetMap'
        )
        
        # Add facility markers
        for facility in facilities:
            self._add_facility_marker(m, facility)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add fullscreen button
        plugins.Fullscreen().add_to(m)
        
        return m
    
    def create_desert_map(
        self,
        facilities: List[Dict[str, Any]],
        medical_deserts: List[Any],
        center: Optional[List[float]] = None
    ) -> folium.Map:
        """
        Create map highlighting medical deserts
        
        Args:
            facilities: List of facility dictionaries
            medical_deserts: List of MedicalDesert objects
            center: Map center
            
        Returns:
            Folium map with desert regions highlighted
        """
        if center is None:
            center = self.GHANA_CENTER
        
        m = folium.Map(
            location=center,
            zoom_start=7,
            tiles='OpenStreetMap'
        )
        
        # Group facilities by region
        facilities_by_region = {}
        for facility in facilities:
            region = facility.get('region', 'Unknown')
            if region not in facilities_by_region:
                facilities_by_region[region] = []
            facilities_by_region[region].append(facility)
        
        # Calculate average position for each region
        region_centers = {}
        for region, facs in facilities_by_region.items():
            lats = [f['latitude'] for f in facs if f.get('latitude')]
            lons = [f['longitude'] for f in facs if f.get('longitude')]
            if lats and lons:
                region_centers[region] = (sum(lats)/len(lats), sum(lons)/len(lons))
        
        # Add desert regions as circles
        for desert in medical_deserts:
            if desert.region in region_centers:
                center_coords = region_centers[desert.region]
                
                # Color by severity
                color = {
                    'critical': self.COLORS['critical'],
                    'severe': self.COLORS['poor'],
                    'moderate': self.COLORS['moderate']
                }.get(desert.severity, self.COLORS['moderate'])
                
                # Radius by severity
                radius = {
                    'critical': 50000,
                    'severe': 40000,
                    'moderate': 30000
                }.get(desert.severity, 30000)
                
                folium.Circle(
                    location=center_coords,
                    radius=radius,
                    popup=self._create_desert_popup(desert),
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.3,
                    weight=2
                ).add_to(m)
                
                # Add label
                folium.Marker(
                    location=center_coords,
                    icon=folium.DivIcon(html=f'''
                        <div style="
                            background-color: {color};
                            color: white;
                            padding: 5px 10px;
                            border-radius: 3px;
                            font-weight: bold;
                            font-size: 12px;
                            white-space: nowrap;
                        ">
                            {desert.region} - {desert.severity.upper()}
                        </div>
                    ''')
                ).add_to(m)
        
        # Add facilities
        for facility in facilities:
            self._add_facility_marker(m, facility, small=True)
        
        plugins.Fullscreen().add_to(m)
        
        return m
    
    def create_capability_heatmap(
        self,
        facilities: List[Dict[str, Any]],
        capability_name: str
    ) -> folium.Map:
        """
        Create heatmap showing distribution of a specific capability
        
        Args:
            facilities: List of facility dictionaries
            capability_name: Name of capability to map
            
        Returns:
            Folium map with heatmap
        """
        m = folium.Map(
            location=self.GHANA_CENTER,
            zoom_start=7,
            tiles='OpenStreetMap'
        )
        
        # Find facilities with the capability
        heat_data = []
        
        for facility in facilities:
            has_capability = False
            
            # Check procedures
            for proc in facility.get('procedures', []):
                if capability_name.lower() in proc.name.lower():
                    has_capability = True
                    break
            
            # Check equipment
            if not has_capability:
                for equip in facility.get('equipment', []):
                    if capability_name.lower() in equip.name.lower():
                        if equip.status == 'operational':
                            has_capability = True
                            break
            
            if has_capability:
                lat = facility.get('latitude')
                lon = facility.get('longitude')
                if lat and lon:
                    # Weight by capability score
                    weight = facility.get('capability_score', 50) / 100
                    heat_data.append([lat, lon, weight])
        
        # Add heatmap layer
        if heat_data:
            plugins.HeatMap(heat_data, radius=30, blur=40).add_to(m)
        
        # Add facility markers
        for facility in facilities:
            self._add_facility_marker(m, facility, small=True)
        
        plugins.Fullscreen().add_to(m)
        
        return m
    
    def _add_facility_marker(
        self,
        map_obj: folium.Map,
        facility: Dict[str, Any],
        small: bool = False
    ):
        """Add a facility marker to the map"""
        lat = facility.get('latitude')
        lon = facility.get('longitude')
        
        if not lat or not lon:
            return
        
        # Determine color based on capability score
        score = facility.get('capability_score', 0)
        
        if score >= 80:
            color = self.COLORS['excellent']
            category = 'Excellent'
        elif score >= 60:
            color = self.COLORS['good']
            category = 'Good'
        elif score >= 40:
            color = self.COLORS['moderate']
            category = 'Moderate'
        elif score >= 20:
            color = self.COLORS['poor']
            category = 'Limited'
        else:
            color = self.COLORS['critical']
            category = 'Critical'
        
        # Create popup
        popup_html = self._create_facility_popup(facility, category)
        
        # Create icon
        if small:
            icon = folium.Icon(color='blue', icon='hospital-o', prefix='fa')
        else:
            icon = folium.Icon(
                color=self._folium_color_from_hex(color),
                icon='hospital-o',
                prefix='fa'
            )
        
        # Add marker
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=facility.get('facility_name'),
            icon=icon
        ).add_to(map_obj)
    
    def _create_facility_popup(self, facility: Dict[str, Any], category: str) -> str:
        """Create HTML popup for facility"""
        name = facility.get('facility_name', 'Unknown')
        ftype = facility.get('facility_type', 'Unknown')
        region = facility.get('region', 'Unknown')
        score = facility.get('capability_score', 0)
        
        html = f"""
        <div style="font-family: Arial, sans-serif; min-width: 250px;">
            <h4 style="margin: 0 0 10px 0; color: #2c3e50;">{name}</h4>
            <p style="margin: 5px 0;"><strong>Type:</strong> {ftype}</p>
            <p style="margin: 5px 0;"><strong>Region:</strong> {region}</p>
            <p style="margin: 5px 0;"><strong>Capability:</strong> {category} ({score:.0f}/100)</p>
        """
        
        # Add procedures
        procedures = facility.get('procedures', [])
        if procedures:
            html += "<p style='margin: 10px 0 5px 0;'><strong>Key Procedures:</strong></p><ul style='margin: 0; padding-left: 20px;'>"
            for proc in procedures[:3]:
                html += f"<li>{proc.name}</li>"
            if len(procedures) > 3:
                html += f"<li><em>...and {len(procedures) - 3} more</em></li>"
            html += "</ul>"
        
        # Add equipment
        equipment = facility.get('equipment', [])
        operational = [e for e in equipment if e.status == 'operational']
        if operational:
            html += "<p style='margin: 10px 0 5px 0;'><strong>Equipment:</strong></p><ul style='margin: 0; padding-left: 20px;'>"
            for equip in operational[:3]:
                html += f"<li>{equip.name}"
                if equip.quantity:
                    html += f" (×{equip.quantity})"
                html += "</li>"
            if len(operational) > 3:
                html += f"<li><em>...and {len(operational) - 3} more</em></li>"
            html += "</ul>"
        
        # Add anomalies
        anomalies = facility.get('anomalies', [])
        if anomalies:
            html += "<p style='margin: 10px 0 5px 0; color: #e74c3c;'><strong>⚠️ Issues:</strong></p><ul style='margin: 0; padding-left: 20px;'>"
            for anomaly in anomalies[:2]:
                html += f"<li style='color: #e74c3c;'>{anomaly}</li>"
            html += "</ul>"
        
        html += "</div>"
        
        return html
    
    def _create_desert_popup(self, desert: Any) -> str:
        """Create HTML popup for medical desert"""
        html = f"""
        <div style="font-family: Arial, sans-serif; min-width: 200px;">
            <h4 style="margin: 0 0 10px 0; color: #c0392b;">Medical Desert: {desert.region}</h4>
            <p style="margin: 5px 0;"><strong>Severity:</strong> {desert.severity.upper()}</p>
            <p style="margin: 5px 0;"><strong>Missing Capabilities:</strong> {len(desert.missing_capabilities)}</p>
        """
        
        if desert.missing_capabilities:
            html += "<ul style='margin: 5px 0; padding-left: 20px;'>"
            for cap in desert.missing_capabilities[:5]:
                html += f"<li>{cap}</li>"
            if len(desert.missing_capabilities) > 5:
                html += f"<li><em>...and {len(desert.missing_capabilities) - 5} more</em></li>"
            html += "</ul>"
        
        html += "</div>"
        
        return html
    
    def _folium_color_from_hex(self, hex_color: str) -> str:
        """Convert hex color to folium color name (approximation)"""
        color_map = {
            '#2ecc71': 'green',
            '#3498db': 'blue',
            '#f39c12': 'orange',
            '#e74c3c': 'red',
            '#c0392b': 'darkred'
        }
        return color_map.get(hex_color, 'blue')
    
    def save_map(self, map_obj: folium.Map, filepath: str):
        """Save map to HTML file"""
        map_obj.save(filepath)
        return filepath
