import { useState } from 'react'
import axios from 'axios'
import { Search, Dna, Activity, Database, Zap, ActivitySquare, PlusCircle, ShieldCheck } from 'lucide-react'
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
      // Pointing to Flask backend
      const response = await axios.post('http://localhost:5000/predict', {
        symptoms: query
      })
      
      if (response.data.error || response.data.message) {
         setError(response.data.error || response.data.message)
      } else {
         setResults(response.data)
      }
    } catch (err) {
      setError('Failed to connect to the prediction server. Make sure the backend is running.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <header className="header">
        <div className="logo">
          <Dna className="logo-icon" size={32} />
          <span>GenoPredict</span>
        </div>
      </header>

      <main>
        <div className="hero">
          <h1>Bioinformatics Prediction Engine</h1>
          <p>Analyze symptoms and genetic mutations using our NLP-powered database of genomic data.</p>
        </div>

        <div className="search-container">
          <form onSubmit={handleSearch}>
            <div className="search-box glass">
              <Search className="search-icon" size={24} />
              <input 
                type="text" 
                className="search-input"
                placeholder="Enter symptoms, gene name or mutation..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              <button type="submit" className="search-btn" disabled={loading}>
                {loading ? 'Analyzing...' : 'Analyze'}
              </button>
            </div>
          </form>
        </div>

        {loading && (
          <div className="loader">
            <Zap className="spinner" size={40} />
            <p className="mono">SEQUENCING GENOMIC DATA...</p>
          </div>
        )}

        {error && (
          <div className="error-msg glass">
            {error}
          </div>
        )}

        {results && results.length > 0 && (
          <div className="content-layout">
            <div className="results-container">
              <h2 className="results-title">Top Matches Found</h2>
              
              {results.map((result, index) => (
                <div key={index} className="result-card glass">
                  <div className="result-header">
                    <h2 className="disease-title">{result.disease}</h2>
                    <div className="match-score">
                      <ActivitySquare size={20} />
                      {result.confidence_score}% Match
                    </div>
                  </div>

                  <div className="details-grid">
                    <div className="detail-item">
                      <div className="detail-label"><Dna size={16} /> Related Genes</div>
                      <div className="detail-value">{result.related_genes}</div>
                    </div>
                    
                    <div className="detail-item">
                      <div className="detail-label"><Zap size={16} /> Mutation Info</div>
                      <div className="detail-value">
                        {result.mutation_info.split(' | ').map((info, i) => {
                          const [key, ...valueParts] = info.split(': ');
                          const value = valueParts.join(': ');
                          return (
                            <div key={i} style={{ marginBottom: '10px', fontSize: '0.95rem' }}>
                              <span style={{ color: 'var(--accent)', opacity: 0.8, display: 'block', fontSize: '0.8rem', textTransform: 'uppercase', marginBottom: '2px' }}>{key}</span>
                              <span style={{ fontWeight: '500', color: 'var(--text)' }}>{value || 'N/A'}</span>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    <div className="detail-item">
                      <div className="detail-label"><Database size={16} /> Prevalence in India</div>
                      <div className="detail-value">{result.prevalence_in_india}</div>
                    </div>

                    <div className="detail-item">
                      <div className="detail-label"><Activity size={16} /> Causes</div>
                      <div className="detail-value" style={{ fontWeight: '600' }}>{result.causes}</div>
                    </div>

                    <div className="detail-item">
                      <div className="detail-label"><ShieldCheck size={16} /> Prevention</div>
                      <div className="detail-value" style={{ color: 'var(--accent)', fontWeight: '600' }}>{result.prevention}</div>
                    </div>

                    <div className="detail-item">
                      <div className="detail-label"><PlusCircle size={16} /> Treatment Suggestions</div>
                      <div className="detail-value">{result.recovery_treatment}</div>
                    </div>

                    <div className="detail-item">
                      <div className="detail-label"><Activity size={16} /> Affected Organ</div>
                      <div className="detail-value" style={{ color: 'var(--accent)', fontWeight: 'bold' }}>
                        {result.affected_organ}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="visualization-sidebar">
               <AnatomyVisualization affectedOrgan={results[0]?.affected_organ} />
            </div>
          </div>
        )}

        {results && results.length === 0 && !loading && (
          <div className="no-results glass">
            <p>No matching diseases found. Try adding more specific details.</p>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
