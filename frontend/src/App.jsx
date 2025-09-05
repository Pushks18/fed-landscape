import React, { useState } from 'react';
import axios from 'axios';
import Select from 'react-select';

const logoUrl = "https://placehold.co/150x50/000000/FFFFFF?text=TUFF+Logo";
// const BACKEND_URL = 'https://backend-c7fj.onrender.com'; 
const BACKEND_URL = 'https://fed-landscape-755503321504.us-west1.run.app'; 

const ALL_OPTION = { value: "all", label: "Select All Keywords" };
const KEYWORD_OPTIONS = [
  "NSF Recompete Pilot Program", "Economic Development Agency (EDA)", "CHIPS Act", "Semiconductors",
  "EDA's Impact Newsletter", "AI Legislation", "University", "Research", "Research Expenditures",
  "Research Grant/Award", "Federal AI Legislation", "Pittsburgh", "Nashville", "Georgia", "Texas",
  "HBCUs", "Tech Hub", "Economic Impact"
].map(keyword => ({ value: keyword, label: keyword }));
const DISPLAY_OPTIONS = [ALL_OPTION, ...KEYWORD_OPTIONS];

function App() {
  const [recipientEmail, setRecipientEmail] = useState('tuff2603@gmail.com');
  const [status, setStatus] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedKeywords, setSelectedKeywords] = useState([]);
  const [dateFilter, setDateFilter] = useState('w');
  const [articles, setArticles] = useState([]);
  const [reportContent, setReportContent] = useState('');

  const handleKeywordChange = (selectedOptions, actionMeta) => {
    if (actionMeta.action === 'select-option' && actionMeta.option.value === 'all') {
      setSelectedKeywords(DISPLAY_OPTIONS);
    } else if (actionMeta.action === 'deselect-option' && actionMeta.option.value === 'all') {
      setSelectedKeywords([]);
    } else if (actionMeta.action === 'clear') {
        setSelectedKeywords([]);
    } else {
      let newSelection = selectedOptions.filter(option => option.value !== 'all');
      if (newSelection.length === KEYWORD_OPTIONS.length) {
        setSelectedKeywords(DISPLAY_OPTIONS);
      } else {
        setSelectedKeywords(newSelection);
      }
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const keywordsToSend = selectedKeywords.filter(o => o.value !== 'all').map(o => o.value);
    if (keywordsToSend.length === 0) {
      setStatus('Please select at least one keyword to search.');
      return;
    }
    
    setIsLoading(true);
    setStatus('Searching, classifying, and summarizing articles...');
    setArticles([]);
    setReportContent('');

    try {
      const response = await axios.post(`${BACKEND_URL}/api/process`, {
        recipient_email: recipientEmail,
        selected_keywords: keywordsToSend,
        date_filter: dateFilter
      });
      if (response.data.status === 'success') {
        // --- FIX: Safely set state, providing empty defaults ---
        setArticles(response.data.articles || []);
        setReportContent(response.data.report_content || '');
        setStatus(response.data.message || 'Report generated successfully.');
      } else {
        setStatus(response.data.message || 'An unknown error occurred.');
      }
    } catch (error) {
      setStatus('An error occurred. Please check the backend console.');
    } finally {
      setIsLoading(false);
    }
  };

  const renderReport = (content) => {
    if (!content) return null;
    const reportSections = content.split('---').slice(1).filter(s => s.trim());

    return reportSections.map((section, index) => {
      const lines = section.trim().split('\n').filter(l => l.trim());
      
      const title = lines.find(l => l.startsWith('## '))?.substring(3) || 'No Title';
      const source = lines.find(l => l.startsWith('**Source:'))?.replace('**Source:**', '').trim() || 'N/A';
      const relevance = lines.find(l => l.startsWith('**Relevance:'))?.replace('**Relevance:**', '').trim() || 'N/A';
      const linkMatch = lines.find(l => l.startsWith('[Read'))?.match(/\[(.*?)\]\((.*?)\)/);
      const linkText = linkMatch ? linkMatch[1] : 'Read Full Article';
      const linkUrl = linkMatch ? linkMatch[2] : '#';
      
      const keyPointsIndex = lines.findIndex(l => l.startsWith('**Key Points:**'));
      const paragraph = lines.slice(3, keyPointsIndex > -1 ? keyPointsIndex : undefined).join('\n').trim();
      const points = keyPointsIndex > -1 ? lines.slice(keyPointsIndex + 1, -2).join('\n') : '';

      return (
        <div key={index} className="report-item">
          <h3>{title}</h3>
          <div className="report-item-meta">
            <span><strong>Source:</strong> {source}</span>
            <span className="meta-relevance"><strong>Relevance:</strong> {relevance}</span>
          </div>
          <p>{paragraph}</p>
          <strong>Key Points:</strong>
          <div dangerouslySetInnerHTML={{ __html: points.replace(/\n/g, '<br />') }} />
          <a href={linkUrl} target="_blank" rel="noopener noreferrer" className="report-link">
            {linkText}
          </a>
        </div>
      );
    });
  };

  return (
    <div className="App">
      <header className="app-header">
        <img src={logoUrl} alt="TUFF Logo" className="logo" />
        <h1>TUFF Fed Landscape</h1>
      </header>
      <p>Select keywords to generate and email the latest report on federal activities.</p>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="keyword-select">Filter by Keywords</label>
          <Select
            id="keyword-select" isMulti options={DISPLAY_OPTIONS}
            className="react-select-container" classNamePrefix="react-select"
            onChange={handleKeywordChange} value={selectedKeywords}
            placeholder="Select keywords..."
          />
        </div>
        <div className="form-group">
            <label htmlFor="date-filter">Date Range</label>
            <select 
                id="date-filter" 
                value={dateFilter} 
                onChange={(e) => setDateFilter(e.target.value)}
                className="date-filter-select" 
            >
                <option value="w">Past Week</option>
                <option value="m">Past Month</option>
                <option value="y">Past Year</option>
            </select>
        </div>
        <div className="form-group">
          <label htmlFor="email">Recipient's Email</label>
          <input
            type="email" id="email" value={recipientEmail}
            onChange={(e) => setRecipientEmail(e.target.value)}
          />
        </div>
        <button type="submit" disabled={isLoading}>
          {isLoading ? <><div className="spinner"></div> Processing...</> : 'Generate & Send Report'}
        </button>
      </form>

      {status && <div className="status">{status}</div>}
      
      {reportContent && (
        <div className="report-view">
            <h2>Generated Intelligence Report</h2>
            <div className="report-content">
                {renderReport(reportContent)}
            </div>
        </div>
      )}

      {articles && articles.length > 0 && (
        <div className="results-container">
          <h2>Source Articles (Ranked by Relevance)</h2>
          {articles.map((article, index) => (
            <div className="article-card" key={index}>
              <div className="article-header">
                <h3><a href={article.link} target="_blank" rel="noopener noreferrer">{article.title}</a></h3>
                <span className="relevance-score">
                  {Math.round(article.relevance_score * 100)}% Relevant
                </span>
              </div>
              <p className="article-source">Source: {article.source} | Published: {article.date}</p>
              <p className="article-snippet">{article.snippet}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;

