import { useState } from 'react'
import axios from 'axios'
import { 
  Search, 
  Dna, 
  Activity, 
  Database, 
  ShieldCheck, 
  Stethoscope, 
  AlertCircle, 
  Info,
  MapPin,
  RefreshCw,
  FlaskConical,
  ChevronRight,
  Heart,
  FileText,
  Thermometer,
  Layers
} from 'lucide-react'
import AnatomyVisualization from './AnatomyVisualization'
import './App.css'

function App() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const response = await axios.post('http://localhost:5000/predict', {
        symptoms: query
      })
      
      if (response.data.error || response.data.message) {
         setError(response.data.error || response.data.message)
      } else {
         setResults(response.data)
      }
    } catch (err) {
      setError('Failed to connect to the prediction server. Please ensure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const parseMutationInfo = (infoStr) => {
    if (!infoStr) return {};
    const items = infoStr.split(' | ');
    const data = {};
    items.forEach(item => {
      const [key, ...val] = item.split(': ');
      if (key && val.length > 0) {
        data[key.trim()] = val.join(': ').trim();
      }
    });
    return data;
  };

  const renderDiseaseCard = (result, isTop = false, index = 0) => {
    const mutationData = parseMutationInfo(result.mutation_info);
    const genes = result.related_genes ? result.related_genes.split(',').map(g => g.trim()) : [];
    
    // Determine Risk Level
    let riskColor = 'risk-low';
    let riskLabel = 'Low Risk';
    if (result.confidence_score > 80) { riskColor = 'risk-high'; riskLabel = 'High Risk'; }
    else if (result.confidence_score > 50) { riskColor = 'risk-medium'; riskLabel = 'Medium Risk'; }

    return (
      <div key={index} className={`disease-main-card ${isTop ? 'top-result' : ''}`}>
        {isTop && <div className="top-badge">Top Match</div>}

        {/* 1. Disease Header */}
        <div className="card-header-section">
          <h2 className="disease-name">{result.disease}</h2>
          <div className="header-meta">
            <div className="match-score-pill">
              <Activity size={18} />
              {result.confidence_score}% Confidence
            </div>
            <div className={`risk-pill ${riskColor}`}>
              {riskLabel}
            </div>
          </div>
        </div>

        {/* 2. Description Box */}
        <div className="info-section-box">
          <div className="section-box-title"><FileText size={18} /> Description</div>
          <p className="description-text">{result.description || 'Clinical description not available for this condition.'}</p>
        </div>

        <div className="info-grid">
          {/* 3. Related Genes Box */}
          <div className="info-section-box">
            <div className="section-box-title"><Dna size={18} /> Related Genes</div>
            <div className="gene-tags">
              {genes.length > 0 ? genes.map((gene, i) => (
                <span key={i} className="gene-tag">{gene}</span>
              )) : <span className="gene-tag">N/A</span>}
            </div>
          </div>

          {/* 5. Prevalence in India Box */}
          <div className="info-section-box">
            <div className="section-box-title"><MapPin size={18} /> Prevalence in India</div>
            <p style={{ fontWeight: '600' }}>{result.prevalence_in_india || 'Nationwide / General Prevalence'}</p>
          </div>

          {/* 4. Mutation Information Box (Table) */}
          <div className="info-section-box full-width">
            <div className="section-box-title"><FlaskConical size={18} /> Mutation Details</div>
            <div className="mutation-table-container">
              <table className="mutation-table">
                <thead>
                  <tr>
                    <th>Variation</th>
                    <th>Protein Change</th>
                    <th>Consequence</th>
                    <th>Condition</th>
                    <th>Review Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>{mutationData['Variation'] || 'N/A'}</td>
                    <td>{mutationData['Protein Change'] || 'N/A'}</td>
                    <td>{mutationData['Consequence'] || 'N/A'}</td>
                    <td>{result.disease}</td>
                    <td>{mutationData['Review Status'] || 'Verified'}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* 6. Causes and Prevention Box */}
          <div className="info-section-box">
            <div className="section-box-title"><ShieldCheck size={18} /> Causes & Prevention</div>
            <div style={{ marginBottom: '10px' }}>
              <strong>Causes:</strong><br />
              <p style={{ fontSize: '0.95rem', marginTop: '5px' }}>{result.causes}</p>
            </div>
            <div>
              <strong>Prevention:</strong><br />
              <p style={{ fontSize: '0.95rem', marginTop: '5px' }}>{result.prevention}</p>
            </div>
          </div>

          {/* 7. Recovery Suggestions Box */}
          <div className="info-section-box">
            <div className="section-box-title"><RefreshCw size={18} /> Recovery Suggestions</div>
            <ul className="bullet-list">
              {result.recovery_treatment ? result.recovery_treatment.split('.').filter(s => s.trim()).map((step, i) => (
                <li key={i}>{step.trim()}</li>
              )) : <li>Consult with a specialist for a personalized recovery plan.</li>}
            </ul>
          </div>

          {/* 8. Affected Organs Box */}
          <div className="info-section-box full-width">
            <div className="section-box-title"><Heart size={18} /> Affected Organs</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
              <Layers size={32} color="var(--accent)" />
              <div>
                <span style={{ fontSize: '1.2rem', fontWeight: '700', color: 'var(--text)' }}>{result.affected_organ}</span>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Target system for clinical observation and monitoring.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="app-container">
      <header className="header" style={{ justifyContent: 'center', flexDirection: 'column', textAlign: 'center', gap: '8px', padding: '1.5rem 1rem' }}>
        <div className="logo" style={{ margin: 0 }}>
          <Stethoscope size={28} />
          <span>GenoPredict</span>
        </div>
        <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', letterSpacing: '0.5px' }}>
          Professional AI-powered diagnostic platform
        </div>
      </header>

      <main>
        <div className="hero">
          <h1>Genomic Disease Prediction System</h1>
          <p>Professional AI-powered diagnostic platform</p>
        </div>

        <div className="search-container">
          <form onSubmit={handleSearch}>
            <div className="search-box">
              <Search className="search-icon" size={24} color="var(--text-muted)" />
              <input 
                type="text" 
                className="search-input"
                placeholder="Enter symptoms or gene mutations (e.g. fatigue, HBB mutation)"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              <button type="submit" className="search-btn" disabled={loading} style={{ fontSize: '1.1rem' }}>
                {loading ? 'Analyzing...' : 'Analyze'}
              </button>
            </div>
          </form>
        </div>

        {loading && (
          <div style={{ textAlign: 'center', padding: '4rem' }}>
            <div className="loading-spinner" style={{ margin: '0 auto 20px auto' }}></div>
            <p style={{ fontWeight: '700', color: 'var(--accent)', letterSpacing: '1px' }}>PROCESSING GENOMIC BIOMARKERS...</p>
          </div>
        )}

        {error && (
          <div className="error-msg">
            <AlertCircle size={24} />
            <p style={{ marginTop: '10px' }}>{error}</p>
          </div>
        )}

        {results && (Array.isArray(results) ? results.length > 0 : Object.keys(results).length > 0) && (
          <div className="content-layout">
            <div className="results-container">
              {!Array.isArray(results) 
                ? renderDiseaseCard(results, true)
                : results.map((res, i) => renderDiseaseCard(res, i === 0, i))
              }
            </div>

            <div className="visualization-sidebar">
               <AnatomyVisualization 
                 disease={Array.isArray(results) ? results[0]?.disease : results?.disease}
                 affectedOrgan={Array.isArray(results) ? results[0]?.affected_organ : results?.affected_organ} 
               />
            </div>
          </div>
        )}

        {results && (Array.isArray(results) ? results.length === 0 : Object.keys(results).length === 0) && !loading && (
          <div className="no-results">
            <Info size={48} style={{ opacity: 0.1, marginBottom: '1rem' }} />
            <p>No matches found. Please try more specific symptoms or genomic data.</p>
          </div>
        )}
      </main>

      <footer style={{ padding: '4rem 2rem', borderTop: '1px solid var(--border)', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
        &copy; 2026 Genomic AI Bioinformatics System. All data is for clinical reference and educational use.
      </footer>
    </div>
  )
}

export default App
