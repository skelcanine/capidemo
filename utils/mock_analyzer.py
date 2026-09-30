import json
import os
from flask import current_app

def get_mock_report():
    """
    Reads mock_report.json from the main directory and returns the python dict.
    """
    mock_path = os.path.join(current_app.root_path, 'mock_report.json')
    if not os.path.exists(mock_path):
        # Fallback default dict if file missing
        return {
            "ssc_classification": "non-SSc",
            "suggested_pattern": "Normal",
            "quality_score": 99.0,
            "total_analysed_mm": 1.51,
            "total_analysed_images": 1,
            "table_data": [
                {"type": "Total capillaries", "total": 28, "percentage": 100.0, "density": 18.56, "apical_diameter": 9.7, "arterial_limb_width": 6.7, "venous_limb_width": 8.6},
                {"type": "Normal capillaries", "total": 25, "percentage": 89.3, "density": 16.57, "apical_diameter": 9.6, "arterial_limb_width": 6.6, "venous_limb_width": 8.5},
                {"type": "Tortuosities", "total": 3, "percentage": 10.7, "density": 1.99, "apical_diameter": 9.8, "arterial_limb_width": 7.9, "venous_limb_width": 9.8},
                {"type": "Abnormal shapes", "total": 0, "percentage": 0.0, "density": 0.0, "apical_diameter": None, "arterial_limb_width": None, "venous_limb_width": None},
                {"type": "Enlarged capillaries", "total": 0, "percentage": 0.0, "density": 0.0, "apical_diameter": None, "arterial_limb_width": None, "venous_limb_width": None},
                {"type": "Giant capillaries", "total": 0, "percentage": 0.0, "density": 0.0, "apical_diameter": None, "arterial_limb_width": None, "venous_limb_width": None},
                {"type": "Hemorrhages", "total": 0, "percentage": 0.0, "density": 0.0, "apical_diameter": None, "arterial_limb_width": None, "venous_limb_width": None}
            ],
            "narratives": {
                "capillary_density": "Conserved with an average density of 18.56 capillaries/mm.",
                "capillary_enlargement": "Infrequent, affecting 0% of capillaries. The average apical diameter was 9.7 µm, venous 8.6 µm, and arterial 6.7 µm. No giant capillaries were found.",
                "capillary_deformities": "Tortuosities: Infrequent, affecting 10.7% of capillaries. Abnormal shapes: None."
            }
        }
    
    with open(mock_path, 'r', encoding='utf-8') as f:
        return json.load(f)
