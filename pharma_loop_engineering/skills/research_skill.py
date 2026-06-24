"""Research skill for scientific literature and database searches."""

from typing import Dict, Any, List, Optional, Tuple
import time
import json
import re
from pathlib import Path
from datetime import datetime
from loguru import logger


class ResearchSkill:
    """Skill for searching scientific databases and analyzing literature."""

    # Common pharmaceutical terms for keyword extraction
    PHARMA_KEYWORDS = {
        'drug_types': ['inhibitor', 'agonist', 'antagonist', 'modulator', 'activator', 'blocker'],
        'targets': ['kinase', 'receptor', 'enzyme', 'channel', 'transporter', 'protein'],
        'diseases': ['cancer', 'diabetes', 'alzheimer', 'parkinson', 'fibrosis', 'inflammation'],
        'mechanisms': ['apoptosis', 'proliferation', 'metastasis', 'angiogenesis', 'immune'],
        'properties': ['bioactivity', 'potency', 'selectivity', 'efficacy', 'toxicity']
    }

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = config.get('cache_ttl', 86400)  # 24 hours
        self.max_retries = config.get('max_retries', 3)
        self.retry_delay = config.get('retry_delay', 1)
        self.llm_plugin = config.get('llm_plugin')
        self.output_dir = Path(config.get('output_dir', 'research_results'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("ResearchSkill initialized")

    def _retry_api_call(self, func, *args, **kwargs):
        """Retry API calls with exponential backoff."""
        import time
        attempt = 0
        last_error = None
        while attempt < self.max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                logger.warning(f"API call failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                attempt += 1
                if attempt < self.max_retries:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
        raise last_error

    def _llm_generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """Generate text with LLM with retries."""
        if not self.llm_plugin:
            logger.warning("LLM plugin not available")
            return ""
        try:
            return self._retry_api_call(self.llm_plugin.generate_text, prompt, max_tokens)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return ""

    def search_pubmed(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search PubMed articles using BioPython.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of article dictionaries
        """
        cache_key = f"pubmed_{query}_{max_results}"
        if cache_key in self.cache:
            logger.info(f"Using cached PubMed results for: {query}")
            return self.cache[cache_key]

        try:
            from Bio import Entrez
            Entrez.email = "research@pharmaloop.ai"

            logger.info(f"Searching PubMed: {query}")

            # Search
            handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
            search_results = Entrez.read(handle)
            handle.close()

            id_list = search_results.get("IdList", [])
            total_count = int(search_results.get("Count", 0))

            if not id_list:
                logger.warning(f"No PubMed results for: {query}")
                return []

            # Fetch details
            handle = Entrez.efetch(db="pubmed", id=id_list, rettype="medline", retmode="text")
            records = handle.read()
            handle.close()

            # Parse results
            articles = []
            for pmid in id_list:
                try:
                    article = self._parse_pubmed_record(pmid)
                    if article:
                        articles.append(article)
                except Exception as e:
                    logger.warning(f"Failed to parse PubMed record {pmid}: {e}")

            result = {
                'query': query,
                'total_count': total_count,
                'returned_count': len(articles),
                'articles': articles
            }

            self.cache[cache_key] = result
            return result

        except ImportError:
            logger.error("BioPython not available for PubMed search")
            return []
        except Exception as e:
            logger.error(f"PubMed search failed: {e}")
            return []

    def _parse_pubmed_record(self, pmid: str) -> Optional[Dict[str, Any]]:
        """Parse a single PubMed record."""
        try:
            from Bio import Entrez
            handle = Entrez.efetch(db="pubmed", id=pmid, rettype="xml", retmode="text")
            record = Entrez.read(handle)
            handle.close()

            if not record:
                return None

            article_data = record.get('PubmedArticle', [{}])[0]
            medline = article_data.get('MedlineCitation', {})
            article = medline.get('Article', {})

            title = article.get('ArticleTitle', '')
            abstract = article.get('Abstract', {}).get('AbstractText', [''])[0]
            authors = article.get('AuthorList', [])
            journal = article.get('Journal', {}).get('Title', '')
            pub_date = article.get('Journal', {}).get('JournalIssue', {}).get('PubDate', {})

            return {
                'pmid': pmid,
                'title': str(title),
                'abstract': str(abstract),
                'authors': [str(a) for a in authors[:5]],
                'journal': str(journal),
                'year': pub_date.get('Year', datetime.now().year),
                'source': 'pubmed'
            }

        except Exception as e:
            logger.warning(f"Failed to parse PubMed record {pmid}: {e}")
            return None

    def search_chembl(self, target: str, activity_type: str = 'IC50') -> List[Dict[str, Any]]:
        """
        Search ChEMBL API for bioactivity data.

        Args:
            target: Target name or ChEMBL ID
            activity_type: Type of activity (IC50, EC50, Ki, etc.)

        Returns:
            List of bioactivity records
        """
        cache_key = f"chembl_{target}_{activity_type}"
        if cache_key in self.cache:
            logger.info(f"Using cached ChEMBL results for: {target}")
            return self.cache[cache_key]

        try:
            import requests

            logger.info(f"Searching ChEMBL: {target} (activity: {activity_type})")

            # Search for target
            base_url = "https://www.ebi.ac.uk/chembl/api/data"
            search_url = f"{base_url}/target/search.json"

            params = {'q': target, 'limit': 5}
            response = requests.get(search_url, params=params, timeout=30)
            response.raise_for_status()

            targets = response.json().get('targets', [])

            if not targets:
                logger.warning(f"No ChEMBL targets found for: {target}")
                return []

            # Get activities for first target
            target_chembl_id = targets[0].get('target_chembl_id')
            if not target_chembl_id:
                return []

            activities_url = f"{base_url}/activity.json"
            params = {
                'target_chembl_id': target_chembl_id,
                'standard_type': activity_type,
                'limit': 50,
                'order_by': 'standard_value',
                'order_dir': 'asc'
            }

            response = requests.get(activities_url, params=params, timeout=30)
            response.raise_for_status()

            activities = response.json().get('activities', [])

            # Parse results
            results = []
            for act in activities:
                results.append({
                    'molecule_chembl_id': act.get('molecule_chembl_id'),
                    'compound_name': act.get('ligand_name', 'Unknown'),
                    'activity_type': act.get('standard_type'),
                    'value': act.get('standard_value'),
                    'units': act.get('standard_units'),
                    'target': target,
                    'source': 'chembl'
                })

            self.cache[cache_key] = results
            return results

        except ImportError:
            logger.error("requests not available for ChEMBL search")
            return []
        except Exception as e:
            logger.error(f"ChEMBL search failed: {e}")
            return []

    def search_clinical_trials(self, drug_name: str) -> List[Dict[str, Any]]:
        """
        Search ClinicalTrials.gov for clinical trial data.

        Args:
            drug_name: Name of the drug to search for

        Returns:
            List of clinical trial records
        """
        cache_key = f"clinical_trials_{drug_name}"
        if cache_key in self.cache:
            logger.info(f"Using cached ClinicalTrials results for: {drug_name}")
            return self.cache[cache_key]

        try:
            import requests

            logger.info(f"Searching ClinicalTrials.gov: {drug_name}")

            base_url = "https://clinicaltrials.gov/api/query/full_studies"
            params = {
                'expr': drug_name,
                'min_rnk': 1,
                'max_rnk': 20,
                'fmt': 'json'
            }

            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            studies = data.get('FullStudiesResponse', {}).get('FullStudies', [])

            results = []
            for study in studies:
                protocol = study.get('Study', {}).get('ProtocolSection', {})
                identification = protocol.get('IdentificationModule', {})
                status = protocol.get('StatusModule', {})

                results.append({
                    'nct_id': identification.get('NCTId', ''),
                    'title': identification.get('BriefTitle', ''),
                    'phase': status.get('Phase', 'N/A'),
                    'status': status.get('OverallStatus', 'N/A'),
                    'enrollment': status.get('EnrollmentCount', 0),
                    'source': 'clinicaltrials.gov'
                })

            self.cache[cache_key] = results
            return results

        except ImportError:
            logger.error("requests not available for ClinicalTrials search")
            return []
        except Exception as e:
            logger.error(f"ClinicalTrials search failed: {e}")
            return []

    def extract_keywords(self, text: str, max_keywords: int = 20) -> List[Dict[str, Any]]:
        """
        Extract key terms from text using NLP.

        Args:
            text: Input text
            max_keywords: Maximum number of keywords to extract

        Returns:
            List of keyword dictionaries with relevance scores
        """
        try:
            import re
            from collections import Counter

            # Simple TF-based keyword extraction
            # In production, use more sophisticated NLP (spaCy, BERT, etc.)

            # Tokenize and clean
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

            # Remove stop words
            stop_words = {'the', 'and', 'for', 'with', 'this', 'that', 'from', 'were',
                         'been', 'have', 'has', 'had', 'does', 'did', 'will', 'would',
                         'could', 'should', 'may', 'might', 'must', 'shall'}
            filtered = [w for w in words if w not in stop_words]

            # Count frequencies
            freq = Counter(filtered)

            # Boost pharmaceutical terms
            for term, category in self.PHARMA_KEYWORDS.items():
                for keyword in category:
                    if keyword in freq:
                        freq[keyword] *= 2  # Boost pharma terms

            # Get top keywords
            top_keywords = freq.most_common(max_keywords)

            return [
                {'term': word, 'frequency': count, 'relevance': count / max(freq.values())}
                for word, count in top_keywords
            ]

        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return []

    def calculate_relevance_score(self, paper: Dict[str, Any], query_terms: List[str],
                                 recency_weight: float = 0.3,
                                 citation_weight: float = 0.2) -> float:
        """
        Calculate relevance score for a paper.

        Args:
            paper: Paper dictionary
            query_terms: List of query terms
            recency_weight: Weight for recency (0-1)
            citation_weight: Weight for citations (0-1)

        Returns:
            Relevance score (0-100)
        """
        score = 0.0

        # Term frequency score (max 40 points)
        title = paper.get('title', '').lower()
        abstract = paper.get('abstract', '').lower()
        full_text = f"{title} {abstract}"

        term_matches = sum(1 for term in query_terms if term.lower() in full_text)
        if query_terms:
            term_score = (term_matches / len(query_terms)) * 40
            score += term_score

        # Recency score (max 30 points)
        try:
            year = int(paper.get('year', datetime.now().year - 5))
            age = datetime.now().year - year
            recency_score = max(0, 30 - age * 2)  # Newer papers score higher
            score += recency_score * recency_weight
        except:
            pass

        # Journal impact factor (max 20 points) - simplified
        journal = paper.get('journal', '').lower()
        high_impact = ['nature', 'science', 'cell', 'nejm', 'lancet']
        if any(j in journal for j in high_impact):
            score += 20 * (1 - recency_weight - citation_weight)

        # Abstract length (proxy for detail) - max 10 points
        abstract_len = len(paper.get('abstract', ''))
        if abstract_len > 500:
            score += 10

        return min(100, max(0, score))

    def summarize_abstracts(self, papers: List[Dict[str, Any]], max_tokens: int = 500) -> str:
        """
        Use LLM to summarize abstracts of papers.

        Args:
            papers: List of paper dictionaries
            max_tokens: Maximum tokens for summary

        Returns:
            Summarized text
        """
        if not papers:
            return ""

        abstracts_text = "\n\n".join([
            f"Title: {p.get('title', '')}\nAbstract: {p.get('abstract', '')[:300]}..."
            for p in papers[:10]  # Limit to top 10
        ])

        prompt = f"""
Resume los siguientes abstracts de papers científicos, identificando los hallazgos clave:

{abstracts_text}

Genera un resumen conciso (máximo {max_tokens} tokens) que incluya:
1. Tema principal de investigación
2. Hallazgos clave (3-5 puntos)
3. Metodologías utilizadas
4. Implicaciones para reposicionamiento de fármacos

Responde en español, de manera técnica pero accesible.
"""

        return self._llm_generate(prompt, max_tokens=max_tokens)

    def identify_trends(self, papers: List[Dict[str, Any]]) -> List[str]:
        """
        Identify trends in the literature using LLM.

        Args:
            papers: List of paper dictionaries

        Returns:
            List of identified trends
        """
        if not papers:
            return []

        titles_years = "\n".join([
            f"- {p.get('year', 'N/A')}: {p.get('title', '')}"
            for p in papers[:20]
        ])

        prompt = f"""
Analiza las siguientes publicaciones científicas e identifica tendencias:

{titles_years}

Genera una lista de tendencias clave (3-5 items) en la investigación:
1. Direcciones de investigación emergentes
2. Cambios en enfoques metodológicos
3. Áreas de creciente interés
4. Patrones temporales en las publicaciones

Responde en formato de lista: ["tendencia1", "tendencia2", ...]
"""

        llm_response = self._llm_generate(prompt, max_tokens=1000)

        # Try to parse as list
        try:
            import json
            start = llm_response.find('[')
            end = llm_response.rfind(']') + 1
            if start >= 0 and end > start:
                return json.loads(llm_response[start:end])
        except:
            pass

        return [llm_response] if llm_response else []

    def detect_research_gaps(self, papers: List[Dict[str, Any]]) -> List[str]:
        """
        Detect research gaps from literature.

        Args:
            papers: List of paper dictionaries

        Returns:
            List of identified research gaps
        """
        if not papers:
            return []

        abstracts_summary = "\n".join([
            p.get('abstract', '')[:200] for p in papers[:15]
        ])

        prompt = f"""
Analiza los siguientes abstracts e identifica gaps de investigación:

{abstracts_summary}

Genera una lista de gaps o preguntas sin respuesta:
1. Aspectos no explorados o insuficientemente estudiados
2. Contradicciones en la literatura
3. Limitaciones metodológicas comunes
4. Áreas donde se necesitan más estudios

Responde en formato JSON: {{"gaps": ["gap1", "gap2", ...]}}
"""

        llm_response = self._llm_generate(prompt, max_tokens=1000)

        try:
            import json
            start = llm_response.find('{')
            end = llm_response.rfind('}') + 1
            if start >= 0 and end > start:
                data = json.loads(llm_response[start:end])
                return data.get('gaps', [])
        except:
            pass

        return []

    def generate_research_questions(self, context: str, gaps: List[str] = None) -> List[str]:
        """
        Generate research questions based on context and gaps.

        Args:
            context: Research context
            gaps: List of identified research gaps

        Returns:
            List of research questions
        """
        gaps_text = "\n".join([f"- {g}" for g in (gaps or [])])

        prompt = f"""
Genera preguntas de investigación relevantes para reposicionamiento de fármacos.

Contexto: {context}

Gaps identificados:
{gaps_text}

Genera 5-7 preguntas de investigación específicas,:
1. Pregunta: \"...\"
2. Pregunta: \"...\"

Cada pregunta debe ser:
- Específica y medible
- Relevante para reposicionamiento
- Respaldada por evidencia preliminar
- Novedosa (no obvia)
"""

        llm_response = self._llm_generate(prompt, max_tokens=1500)

        questions = []
        for line in llm_response.split('\n'):
            if 'Pregunta:' in line or 'pregunta:' in line:
                question = line.split(':', 1)[1].strip().strip('"')
                if question:
                    questions.append(question)

        return questions[:7]  # Limit to 7

    def generate_research_report(self, query: str, 
                                pubmed_results: List[Dict] = None,
                                chembl_results: List[Dict] = None,
                                clinical_trials: List[Dict] = None) -> Dict[str, Any]:
        """
        Generate comprehensive research report.

        Args:
            query: Original search query
            pubmed_results: PubMed search results
            chembl_results: ChEMBL bioactivity results
            clinical_trials: Clinical trials results

        Returns:
            Structured research report
        """
        logger.info(f"Generating research report for: {query}")

        # Combine all results
        all_papers = []
        if pubmed_results:
            all_papers.extend(pubmed_results.get('articles', []) if isinstance(pubmed_results, dict) else pubmed_results)
        if chembl_results:
            all_papers.extend(chembl_results)

        total_results = len(all_papers)

        # Extract query terms
        query_terms = self.extract_keywords(query, max_keywords=10)
        query_terms = [k['term'] for k in query_terms]

        # Score papers
        scored_papers = []
        for paper in all_papers:
            score = self.calculate_relevance_score(paper, query_terms)
            paper['relevance_score'] = score
            scored_papers.append(paper)

        # Sort by score
        scored_papers.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        top_papers = scored_papers[:20]

        # Generate summaries and analysis
        key_findings = []
        if top_papers:
            summary = self.summarize_abstracts(top_papers[:5])
            if summary:
                # Extract bullet points from summary
                for line in summary.split('\n'):
                    if line.strip().startswith('-') or line.strip().startswith('•'):
                        key_findings.append(line.strip())

        # Identify trends and gaps
        trends = self.identify_trends(top_papers)
        gaps = self.detect_research_gaps(top_papers)

        # Calculate overall report score
        if scored_papers:
            avg_score = sum(p.get('relevance_score', 0) for p in scored_papers) / len(scored_papers)
            report_score = min(100, avg_score + (10 if trends else 0) + (10 if gaps else 0))
        else:
            report_score = 0

        report = {
            'query': query,
            'total_results': total_results,
            'timestamp': int(time.time()),
            'top_papers': [
                {
                    'title': p.get('title', ''),
                    'authors': p.get('authors', []),
                    'year': p.get('year', 'N/A'),
                    'journal': p.get('journal', ''),
                    'relevance_score': p.get('relevance_score', 0),
                    'abstract': p.get('abstract', '')[:500] + '...' if len(p.get('abstract', '')) > 500 else p.get('abstract', '')
                }
                for p in top_papers
            ],
            'key_findings': key_findings[:10],
            'trends': trends,
            'research_gaps': gaps,
            'clinical_trials_count': len(clinical_trials) if clinical_trials else 0,
            'relevance_score': report_score,
            'summary': {
                'total_papers_analyzed': total_results,
                'high_relevance_papers': sum(1 for p in scored_papers if p.get('relevance_score', 0) >= 70),
                'database_coverage': {
                    'pubmed': len(pubmed_results.get('articles', [])) if isinstance(pubmed_results, dict) else len(pubmed_results or []),
                    'chembl': len(chembl_results or []),
                    'clinical_trials': len(clinical_trials or [])
                }
            }
        }

        # Save report
        report_path = self.output_dir / f"research_report_{int(time.time())}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)

        logger.success(f"Research report generated: {report_path}")
        return report

    def generate_research_summary_text(self, report: Dict[str, Any]) -> str:
        """Generate human-readable research summary."""
        query = report.get('query', 'Unknown')
        total = report.get('total_results', 0)
        score = report.get('relevance_score', 0)

        summary = f"""
# Informe de Investigación: {query}

## Resumen Ejecutivo

- **Total de resultados**: {total} papers/registros
- **Score de relevancia**: {score:.1f}/100
- **Papers de alta relevancia**: {report.get('summary', {}).get('high_relevance_papers', 0)}

## Hallazgos Clave

"""
        for finding in report.get('key_findings', [])[:5]:
            summary += f"- {finding}\n"

        summary += """
## Tendencias Identificadas

"""
        for trend in report.get('trends', [])[:3]:
            summary += f"- {trend}\n"

        summary += """
## Gaps de Investigación

"""
        for gap in report.get('research_gaps', [])[:3]:
            summary += f"- {gap}\n"

        summary += f"""
## Top Papers

"""
        for i, paper in enumerate(report.get('top_papers', [])[:5], 1):
            summary += f"""
### {i}. {paper.get('title', 'Unknown')}
- **Autores**: {', '.join(paper.get('authors', [])[:3])}
- **Año**: {paper.get('year', 'N/A')}
- **Journal**: {paper.get('journal', 'Unknown')}
- **Relevancia**: {paper.get('relevance_score', 0):.1f}/100
- **Abstract**: {paper.get('abstract', 'No disponible')[:200]}...
"""

        return summary

    def clear_cache(self) -> None:
        """Clear the search cache."""
        self.cache.clear()
        logger.info("Research cache cleared")

    def get_search_history(self) -> List[Dict[str, Any]]:
        """Get search history from cache."""
        return [
            {'key': key, 'timestamp': time.time()}
            for key in self.cache.keys()
        ]

    def __repr__(self) -> str:
        return f"ResearchSkill(cached={len(self.cache)}, llm={'available' if self.llm_plugin else 'unavailable'})"