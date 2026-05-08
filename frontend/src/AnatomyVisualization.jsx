import React from 'react';
import './AnatomyVisualization.css';

const AnatomyVisualization = ({ affectedOrgan }) => {
  const organIdMap = {
    "brain": ["organ-brain"],
    "lungs": ["organ-lungs"],
    "heart": ["organ-heart"],
    "breast": ["organ-breast", "organ-breast-right"],
    "blood": ["organ-blood"],
    "blood / bone marrow": ["organ-blood", "organ-bone-marrow", "organ-bone-marrow-right"]
  };

  const activeIds = affectedOrgan ? organIdMap[affectedOrgan.toLowerCase().trim()] || [] : [];

  const isActive = (id) => activeIds.includes(id);

  return (
    <div className="anatomy-visualization">
      <h3>3D Anatomy Diagnostic</h3>
      <div className="anatomy-container">
        <div className="image-wrapper">
          <img src="/body_3d.png" alt="3D Human Body" className="body-3d-image" />
          <div className="overlay-scanline"></div>
          
          {/* Dynamic Markers */}
          {affectedOrgan && (
            <div className={`marker-system ${affectedOrgan.toLowerCase().replace(/ \/ /g, '-').replace(/ /g, '-')}`}>
              <div className="organ-glow-point brain-point" data-organ="brain"></div>
              <div className="organ-glow-point lungs-point" data-organ="lungs"></div>
              <div className="organ-glow-point heart-point" data-organ="heart"></div>
              <div className="organ-glow-point breast-left-point" data-organ="breast"></div>
              <div className="organ-glow-point breast-right-point" data-organ="breast"></div>
              <div className="organ-glow-point blood-point" data-organ="blood"></div>
              <div className="organ-glow-point marrow-left-point" data-organ="blood / bone marrow"></div>
              <div className="organ-glow-point marrow-right-point" data-organ="blood / bone marrow"></div>
            </div>
          )}
        </div>

        {affectedOrgan && (
          <div className="organ-label">
            Target System: <strong>{affectedOrgan}</strong>
            <div className="analysis-text">Status: Pathological detected in this region.</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnatomyVisualization;
